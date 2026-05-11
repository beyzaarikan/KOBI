from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Order, Inventory, Product


class OperationService:
    async def generate_daily_operation_report(self, session: AsyncSession):
        orders_result = await session.execute(select(Order))
        orders = orders_result.scalars().all()

        inventory_result = await session.execute(
            select(Product, Inventory).join(Inventory, Product.id == Inventory.product_id)
        )
        inventory_data = inventory_result.all()

        total_orders = len(orders)

        to_prepare = 0
        to_package = 0
        to_ship = 0
        delayed = 0
        waiting_stock = 0

        for order in orders:
            raw_status = getattr(order, "status", "")
            status = getattr(raw_status, "value", str(raw_status))
            status = str(status).lower().strip().split(".")[-1]

            if status == "preparing":
                to_prepare += 1
                to_package += 1
            elif status == "shipped":
                to_ship += 1
            elif status == "delivered":
                pass

            risk_level = str(getattr(order, "risk_level", "")).lower().strip()
            if risk_level in ["high", "critical"]:
                delayed += 1

        critical_stock_products = 0

        for product, inventory in inventory_data:
            current_stock = getattr(inventory, "current_stock", 0)
            threshold = getattr(inventory, "threshold", 0)

            if current_stock <= threshold:
                critical_stock_products += 1

        summary = (
            f"Bugün toplam {total_orders} sipariş bulunuyor. "
            f"{to_prepare} sipariş hazırlanacak, {to_package} sipariş paketlenecek, "
            f"{to_ship} sipariş kargo sürecinde. "
            f"{delayed} riskli/gecikme ihtimali olan sipariş var. "
            f"Ayrıca {critical_stock_products} ürün kritik stok seviyesinde."
        )

        tasks = {
            "depo": [
                f"{to_prepare} sipariş hazırlanacak.",
                f"{to_package} sipariş paketlenecek.",
                f"{critical_stock_products} kritik stok ürünü kontrol edilecek."
            ],
            "kargo": [
                f"{to_ship} siparişin kargo süreci takip edilecek."
            ],
            "yonetici": [
                f"{delayed} riskli sipariş kontrol edilecek.",
                f"{waiting_stock} stok bekleyen sipariş için aksiyon alınacak."
            ]
        }

        priorities = [
            "Riskli veya gecikme ihtimali olan siparişler kontrol edilmeli.",
            "Hazırlanacak ve paketlenecek siparişler tamamlanmalı.",
            "Kritik stok seviyesindeki ürünler için tedarik planı yapılmalı."
        ]

        return {
            "summary": summary,
            "tasks": tasks,
            "priorities": priorities,
            "raw_metrics": {
                "total_orders": total_orders,
                "to_prepare": to_prepare,
                "to_package": to_package,
                "to_ship": to_ship,
                "delayed": delayed,
                "waiting_stock": waiting_stock,
                "critical_stock_products": critical_stock_products
            }
        }