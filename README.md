# Kobi.app - AI-Powered SME Inventory & Order Management

Kobi.app, KOBİ'ler ve kooperatifler için stok süreçlerini otomatikleştiren, müşteri destek sürecini yapay zeka ile yöneten ve kargo/sipariş gecikmelerini öngören modern bir SaaS (Yazılım Hizmeti Olarak) mimarisidir.

## Özellikler

- 🧠 **AI Inventory Intelligence Engine**: Stok seviyelerini analiz eder, tüketim hızını ölçer ve "X gün sonra bitecek, Y adet sipariş ver" önerisi sunar (Gemini API ile).
- 💬 **AI Customer Support Agent**: Doğal dil işleme (NLP) ile müşterilerin "Siparişim nerede?", "Stokta var mı?" gibi sorularına RAG mantığıyla yanıt verir.
- 📊 **Modern Dashboard**: Next.js 14, TailwindCSS ve shadcn/ui ile geliştirilmiş Linear/Stripe estetiğinde dark-mode arayüz.
- ⚡ **Asenkron Mimari**: FastAPI ve WebSockets sayesinde gerçek zamanlı uyarılar ve yüksek performans.

## Teknoloji Yığını

- **Frontend**: Next.js (App Router), TypeScript, TailwindCSS v4, shadcn/ui.
- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL (Demo için SQLite fallback), WebSockets.
- **AI**: Google Gemini API (Agent tabanlı iş akışları).

## Local Development (Kurulum)

### Backend
1. `cd backend`
2. `python3 -m venv venv`
3. `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. `pip install -r requirements.txt` (Eğer requirements dosyası yoksa: `pip install fastapi uvicorn sqlalchemy aiosqlite pydantic google-generativeai`)
5. Veritabanını hazırlamak için seed scriptini çalıştırın:
   ```bash
   export PYTHONPATH=$(pwd)
   python scripts/seed.py
   ```
6. API'yi başlatın: `uvicorn app.main:app --reload`
7. API Dökümantasyonu: `http://localhost:8000/docs`

### Frontend
1. `cd frontend`
2. Node.js v20.x gereklidir.
3. `npm install`
4. `npm run dev`
5. Tarayıcıda açın: `http://localhost:3000`

### Docker ile Çalıştırma
```bash
docker-compose up --build
```

## AI Agent ve Prompt Engineering Yapısı

Sistemde iki ana Agent bulunmaktadır (`backend/app/services/ai_agent.py`):
1. **Inventory Agent**: Veritabanındaki ürün ve stok verilerini (JSON formatında) alır. Modelin sistem prompt'unda ona bir "Inventory Intelligence Engine" olduğu söylenir. Çıktı olarak JSON formatında risk düzeyi, bitiş süresi ve yeniden sipariş önerisi döner.
2. **Customer Support Agent**: Mock bir RAG mimarisi kullanır. Müşterinin sorduğu soruya yanıt verebilmesi için en son sipariş durumları context olarak prompt'a enjekte edilir.

## Demo Senaryoları
1. **Düşük Stok Uyarı Senaryosu**: 
   - Seed scripti ile bazı ürünlerin stokları bilinçli olarak "Threshold" değerinin altında üretilir.
   - Dashboard açıldığında AI Inventory Insights paneli saniyeler içinde "Organik Domates Salçası"nın kritik seviyede olduğunu ve kaç birim sipariş verilmesi gerektiğini yazar.
2. **Müşteri Sipariş Sorgusu**:
   - Sağ alttaki AI Support Chat bölümüne "Siparişim nerede?" yazıldığında, sistem en son oluşturulan siparişin güncel durumunu (örneğin: "Siparişiniz yola çıktı (In Transit)") doğal dilde yanıtlar.

## Neden Bu Mimari Seçildi?
- **FastAPI**: Asenkron yapısı ve Python ekosistemi sayesinde AI (Gemini) servisleri ile mükemmel bir senkronizasyon sağlar.
- **Modüler Monolit**: Başlangıç ve hackathon hızı için tek bir proje altında katmanlara (Routers, Services, Repositories) ayrıldı. İleride trafiğe bağlı olarak Inventory, Orders ve AI Inference kısımları izole mikroservislere kolayca dönüştürülebilir.
