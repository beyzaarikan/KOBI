from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.db.session import get_db
from app.models.models import Product, Inventory, InventoryMovement, Order, OrderItem
from app.schemas.schemas import ProductOut, InventoryOut, DashboardMetrics
from app.services.ai_agent import inventory_agent

router = APIRouter()

@router.get("/products", response_model=List[ProductOut])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()

@router.get("/inventory", response_model=List[InventoryOut])
async def get_inventory(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Inventory))
    return result.scalars().all()

@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    # Total orders today
    orders_result = await db.execute(select(func.count(Order.id)))
    total_orders = orders_result.scalar_one()
    
    # Low stock
    low_stock_res = await db.execute(select(func.count(Inventory.id)).where(Inventory.current_stock < Inventory.threshold))
    low_stock_alerts = low_stock_res.scalar_one()
    
    # Revenue today (mocking all time for demo)
    rev_res = await db.execute(select(func.sum(Order.total_amount)))
    revenue = rev_res.scalar_one() or 0.0
    
    return DashboardMetrics(
        total_orders_today=total_orders,
        low_stock_alerts=low_stock_alerts,
        delayed_shipments=1, # Mock
        revenue_today=revenue
    )

@router.get("/ai/inventory-insights")
async def get_ai_inventory_insights(db: AsyncSession = Depends(get_db)):
    insights = await inventory_agent.analyze_inventory(db)
    return {"insights": insights}
