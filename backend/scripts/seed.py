import asyncio
import os
import random
from datetime import datetime, timedelta
from app.db.session import AsyncSessionLocal, engine, Base
from app.models.models import User, Product, Inventory, Order, OrderItem, InventoryMovement, MovementType, OrderStatus, Shipment


async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        # Create Products
        products_data = [
            {"name": "Espresso Çekirdeği (1kg)", "sku": "CF-ESP-1KG", "price": 450.0},
            {"name": "Filtre Kahve (500g)", "sku": "CF-FLT-500", "price": 250.0},
            {"name": "Organik Domates Salçası", "sku": "KO-DOM-SAL", "price": 120.0},
            {"name": "Soğuk Sıkım Zeytinyağı (1L)", "sku": "KO-ZEY-1L", "price": 380.0},
            {"name": "Süzme Çiçek Balı", "sku": "KO-BAL-800", "price": 550.0},
        ]
        
        products = []
        for p_data in products_data:
            p = Product(**p_data)
            session.add(p)
            products.append(p)
            
        await session.commit()
        
        # Create Inventory
        for p in products:
            current_stock = random.randint(5, 100)
            threshold = random.randint(10, 30)
            
            # Simulate a predicted depletion
            depletion_days = random.randint(1, 14) if current_stock < threshold + 10 else random.randint(15, 60)
            predicted_date = datetime.now() + timedelta(days=depletion_days)
            
            inv = Inventory(
                product_id=p.id,
                current_stock=current_stock,
                threshold=threshold,
                predicted_depletion_date=predicted_date,
                restock_suggestion=threshold * 3 if current_stock < threshold else 0
            )
            session.add(inv)
            
            # Create some movements
            for _ in range(5):
                mov = InventoryMovement(
                    product_id=p.id,
                    change_amount=random.randint(1, 10),
                    type=random.choice([MovementType.IN, MovementType.OUT]),
                    reason="Initial seed"
                )
                session.add(mov)
                
        await session.commit()
        
        # Create Orders
        for i in range(10):
            status = random.choice(list(OrderStatus))
            order = Order(
                customer_name=f"Customer {i}",
                customer_email=f"customer{i}@example.com",
                status=status,
                risk_level="High" if status == OrderStatus.preparing and random.random() > 0.7 else "Low",
            )
            session.add(order)
            await session.flush() # To get order.id
            
            # Order Items
            total = 0
            for _ in range(random.randint(1, 3)):
                p = random.choice(products)
                qty = random.randint(1, 5)
                total += p.price * qty
                item = OrderItem(
                    order_id=order.id,
                    product_id=p.id,
                    quantity=qty,
                    unit_price=p.price
                )
                session.add(item)
            
            order.total_amount = total
            
            # Shipment
            shipment = Shipment(
                order_id=order.id,
                tracking_number=f"TRK{random.randint(100000, 999999)}" if status != OrderStatus.preparing else None,
                status="In Transit" if status == OrderStatus.shipped else "Pending",
                is_delayed=1 if random.random() > 0.8 else 0
            )
            session.add(shipment)
            
        await session.commit()
        print("Database seeded successfully with mock data.")

if __name__ == "__main__":
    asyncio.run(seed_data())
