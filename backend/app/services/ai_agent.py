import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Product, Inventory, Order,Shipment

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY", "MOCK_KEY"))

# Use a specific model
MODEL_NAME = 'gemini-2.5-flash'

class InventoryAgent:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel(MODEL_NAME)
        except Exception as e:
            self.model = None
            print(f"Failed to load AI model: {e}")

    async def analyze_inventory(self, session: AsyncSession):
        """Analyzes the current inventory and returns insights."""
        result = await session.execute(
            select(Product, Inventory).join(Inventory, Product.id == Inventory.product_id)
        )
        data = result.all()
        
        inventory_context = []
        for p, inv in data:
            inventory_context.append({
                "product_name": p.name,
                "current_stock": inv.current_stock,
                "critical_level": inv.threshold,
                "average_daily_sales": 2.5 # Mock velocity
            })
            
        prompt = f"""
        Sen bir KOBİ için uzman bir Envanter Zeka Motorusun.
        Aşağıdaki envanter verilerini analiz et ve eyleme geçirilebilir içgörüler sağla.
        SADECE aşağıdaki alanları içeren bir JSON dizisi (array) döndür:
        - "product_name": Ürün adı
        - "status": Durum (Kritik, Uyarı, Normal)
        - "critical_explanation": Neden önemli olduğunu açıklayan metin (ör: "Domates stoğu kritik seviyenin altına düşmüş. Günlük ortalama satış 12 kg olduğu için mevcut stok yaklaşık 3-4 gün içinde tükenebilir.")
        - "order_recommendation": Geçmiş satışa göre öneri (ör: "Son 7 günlük satış hızına göre en az 100 kg sipariş verilmesi önerilir.")
        - "supplier_email_draft": Tedarikçiye gönderilecek sipariş maili taslağı (ör: "Merhaba, Domates stoğumuz kritik seviyenin altına düşmüştür. En kısa sürede 100 kg tedariği için fiyat ve teslimat bilgisi rica ederiz.")
        
        Veri: {json.dumps(inventory_context)}
        """
        
        if not self.model or os.getenv("GEMINI_API_KEY") == "MOCK_KEY":
            # Mock response if no API key
            return [
                {
                    "product_name": "Organik Domates Salçası",
                    "status": "Kritik",
                    "critical_explanation": "Organik Domates Salçası stoğu kritik seviyenin altına düşmüş. Günlük ortalama satış 2.5 adet olduğu için mevcut stok çok kısa sürede tükenebilir.",
                    "order_recommendation": "Son satış hızına göre en az 50 adet sipariş verilmesi önerilir.",
                    "supplier_email_draft": "Merhaba,\n\nOrganik Domates Salçası stoğumuz kritik seviyenin altına düşmüştür. En kısa sürede 50 adet tedariği için fiyat ve teslimat bilgisi paylaşmanızı rica ederiz.\n\nTeşekkürler."
                }
            ]
            
        try:
            response = await self.model.generate_content_async(
                prompt,
                request_options={"timeout": 60}
            )
            content = response.text
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"AI Generation error: {e}")
            return []



# ─────────────────────────────────────────────
# INTENT TESPİTİ
# ─────────────────────────────────────────────
def detect_intent(message: str) -> str:
    """
    Mesajdan intent tespit eder.
    Döndürülen değerler:
      ORDER_STATUS   - siparişin durumu
      SHIPMENT_STATUS - kargo / teslimat
      PRODUCT_STOCK  - stok sorgulama
      RETURN_REQUEST - iade
      GENERAL_SUPPORT - diğer
    """
    message_lower = message.lower()
 
    shipment_keywords = ["kargo", "teslimat", "ne zaman gelir", "gönderildi mi", "yolda mı", "takip"]
    order_keywords = ["sipariş", "siparişim", "nerede", "durum", "hazırlanıyor", "onaylandı"]
    stock_keywords = ["stok", "stokta", "var mı", "mevcut", "ürün var", "tükendi"]
    return_keywords = ["iade", "iptal", "geri", "değişim"]
 
    if any(k in message_lower for k in return_keywords):
        return "RETURN_REQUEST"
    if any(k in message_lower for k in stock_keywords):
        return "PRODUCT_STOCK"
    if any(k in message_lower for k in shipment_keywords):
        return "SHIPMENT_STATUS"
    if any(k in message_lower for k in order_keywords):
        return "ORDER_STATUS"
    return "GENERAL_SUPPORT"
 
 
# ─────────────────────────────────────────────
# ENTITY EXTRACTION
# ─────────────────────────────────────────────
def extract_order_id(message: str) -> int | None:
    """
    Mesajdan sipariş numarasını çıkarır.
    Örnek: "128 numaralı siparişim" → 128
    """
    # Sayı + "numaralı" / "no" / "#" kalıpları
    patterns = [
        r"#\s*(\d+)",
        r"(\d+)\s*numaralı",
        r"sipariş\s*no\s*[:\-]?\s*(\d+)",
        r"no\s*[:\-]?\s*(\d+)",
        r"\bno\.?\s*(\d+)\b",
        r"\b(\d{1,6})\b",  # son çare: mesajdaki herhangi bir sayı
    ]
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return int(match.group(1))
    return None
 
 
def extract_product_name(message: str) -> str | None:
    """
    Mesajdan ürün adı ipucu çıkarır (basit keyword eşleşmesi).
    Seed'deki ürün isimleriyle karşılaştırır.
    """
    known_products = [
        "espresso", "filtre kahve", "domates", "salça",
        "zeytinyağı", "bal", "kahve"
    ]
    message_lower = message.lower()
    for kw in known_products:
        if kw in message_lower:
            return kw
    return None
 
 
# ─────────────────────────────────────────────
# VERİTABANI SORGULARI
# ─────────────────────────────────────────────
async def get_order_with_shipment(order_id: int, session: AsyncSession) -> dict | None:
    """Sipariş ve bağlı kargo bilgisini çeker."""
    result = await session.execute(
        select(Order, Shipment)
        .outerjoin(Shipment, Order.id == Shipment.order_id)
        .where(Order.id == order_id)
    )
    row = result.first()
    if not row:
        return None
 
    order, shipment = row
    return {
        "order_id": order.id,
        "customer_name": order.customer_name,
        "status": order.status,
        "total_amount": order.total_amount,
        "risk_level": order.risk_level,
        "created_at": str(order.created_at),
        "shipment": {
            "tracking_number": shipment.tracking_number if shipment else None,
            "status": shipment.status if shipment else "Bilgi yok",
            "estimated_delivery": str(shipment.estimated_delivery) if shipment and shipment.estimated_delivery else "Belirtilmemiş",
            "is_delayed": bool(shipment.is_delayed) if shipment else False,
        } if shipment else None,
    }
 
 
async def get_product_stock(keyword: str, session: AsyncSession) -> list[dict]:
    """Ürün adı içeren ürünleri ve stok bilgilerini çeker."""
    result = await session.execute(
        select(Product, Inventory)
        .outerjoin(Inventory, Product.id == Inventory.product_id)
        .where(Product.name.ilike(f"%{keyword}%"))
    )
    rows = result.all()
    found = []
    for product, inv in rows:
        found.append({
            "product_name": product.name,
            "current_stock": inv.current_stock if inv else 0,
            "threshold": inv.threshold if inv else 0,
            "is_critical": (inv.current_stock < inv.threshold) if inv else False,
        })
    return found
 
 
# ─────────────────────────────────────────────
# PROMPT OLUŞTURMA
# ─────────────────────────────────────────────
def build_prompt(message: str, intent: str, context: dict) -> str:
    base = """Sen küçük işletmeler için çalışan nazik ve profesyonel bir iç destek asistanısın.
Yöneticinin sorduğu soruları veritabanından gelen bilgilerle cevaplayacaksın.
 
Kurallar:
- Kısa ve net cevap ver (2-4 cümle).
- Teknik detay verme.
- Eğer bilgi yoksa uydurma, kibarca bilmediğini söyle.
- Türkçe cevap ver.
"""
 
    if intent in ("ORDER_STATUS", "SHIPMENT_STATUS"):
        order_info = context.get("order")
        if not order_info:
            return base + f'\nYönetici sorusu: "{message}"\n\nBu sipariş numarasına ait kayıt bulunamadı. Bunu kibarca belirt.'
 
        shipment = order_info.get("shipment")
        shipment_text = ""
        if shipment:
            delayed = "Evet" if shipment["is_delayed"] else "Hayır"
            shipment_text = f"""
Kargo Bilgisi:
  Takip No: {shipment["tracking_number"] or "Henüz atanmadı"}
  Kargo Durumu: {shipment["status"]}
  Tahmini Teslimat: {shipment["estimated_delivery"]}
  Gecikme Var Mı: {delayed}
"""
 
        return base + f"""
Yönetici sorusu: "{message}"
 
Sipariş Bilgisi:
  Sipariş No: {order_info["order_id"]}
  Müşteri: {order_info["customer_name"]}
  Durum: {order_info["status"]}
  Toplam Tutar: {order_info["total_amount"]} TL
  Risk: {order_info["risk_level"]}
{shipment_text}
"""
 
    elif intent == "PRODUCT_STOCK":
        products = context.get("products", [])
        if not products:
            return base + f'\nYönetici sorusu: "{message}"\n\nBu ürünle ilgili stok kaydı bulunamadı. Bunu kibarca belirt.'
 
        product_text = "\n".join([
            f'  - {p["product_name"]}: {p["current_stock"]} adet '
            f'(Eşik: {p["threshold"]}, Kritik: {"Evet" if p["is_critical"] else "Hayır"})'
            for p in products
        ])
        return base + f"""
Yönetici sorusu: "{message}"
 
Stok Bilgisi:
{product_text}
"""
 
    elif intent == "RETURN_REQUEST":
        return base + f"""
Yönetici sorusu: "{message}"
 
Bu iade/iptal talebi şu an otomatik işlenemiyor. Yöneticiye manuel inceleme yapması gerektiğini söyle.
"""
 
    else:
        return base + f'\nYönetici sorusu: "{message}"\n\nGenel bir soru. Elimdeki bilgilerle yardımcı olmaya çalış.'


class CustomerSupportAgent:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel(MODEL_NAME)
        except Exception as e:
            self.model = None
            print(f"AI model yüklenemedi: {e}")
 
    async def handle_query(self, message: str, session: AsyncSession) -> dict:
        """
        Mesajı işler ve yapılandırılmış cevap döndürür.
        Dönüş formatı:
        {
            "intent": str,
            "answer": str,
            "requires_human": bool,
            "context_found": bool
        }
        """
        intent = detect_intent(message)
        context = {}
        context_found = True
 
        # Entity extraction ve DB sorgusu
        if intent in ("ORDER_STATUS", "SHIPMENT_STATUS"):
            order_id = extract_order_id(message)
            if order_id:
                order_data = await get_order_with_shipment(order_id, session)
                if order_data:
                    context["order"] = order_data
                else:
                    context_found = False
            else:
                context_found = False
 
        elif intent == "PRODUCT_STOCK":
            keyword = extract_product_name(message)
            if keyword:
                products = await get_product_stock(keyword, session)
                context["products"] = products
                context_found = bool(products)
            else:
                context_found = False
 
        # Prompt oluştur
        prompt = build_prompt(message, intent, context)
 
        # Mock mod (API key yoksa)
        if not self.model or os.getenv("GEMINI_API_KEY", "MOCK_KEY") == "MOCK_KEY":
            answer = self._mock_response(intent, context, context_found)
            return {
                "intent": intent,
                "answer": answer,
                "requires_human": intent == "RETURN_REQUEST" or not context_found,
                "context_found": context_found,
            }
 
        # Gerçek AI çağrısı
        try:
            response = await self.model.generate_content_async(
                prompt,
                request_options={"timeout": 60}
            )
            return response.text
        except Exception as e:
            print(f"AI hatası: {e}")
            answer = "Şu an isteğinizi işleyemiyorum, lütfen daha sonra tekrar deneyin."
 
        return {
            "intent": intent,
            "answer": answer,
            "requires_human": intent == "RETURN_REQUEST" or not context_found,
            "context_found": context_found,
        }
 
    def _mock_response(self, intent: str, context: dict, context_found: bool) -> str:
        """API key yokken demo için mock cevap üretir."""
        if not context_found:
            return "Bu bilgiye ait kayıt sistemde bulunamadı. Lütfen numarayı veya ürün adını kontrol edin."
 
        if intent in ("ORDER_STATUS", "SHIPMENT_STATUS"):
            order = context.get("order", {})
            shipment = order.get("shipment") or {}
            return (
                f"{order.get('order_id')} numaralı sipariş şu an "
                f"'{order.get('status')}' durumunda. "
                f"Kargo durumu: {shipment.get('status', 'Bilgi yok')}. "
                f"Tahmini teslimat: {shipment.get('estimated_delivery', 'Belirtilmemiş')}."
            )
 
        if intent == "PRODUCT_STOCK":
            products = context.get("products", [])
            lines = []
            for p in products:
                durum = "KRİTİK STOK" if p["is_critical"] else "Yeterli stok"
                lines.append(f"{p['product_name']}: {p['current_stock']} adet ({durum})")
            return "Stok bilgisi:\n" + "\n".join(lines)
 
        return "Sorunuzu aldım. Bu konuda size yardımcı olmaya çalışıyorum."
    
inventory_agent = InventoryAgent()
support_agent = CustomerSupportAgent()
