from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    price: float

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    inventory_health_score: float
    
    class Config:
        from_attributes = True

class InventoryBase(BaseModel):
    product_id: int
    current_stock: int
    threshold: int

class InventoryOut(InventoryBase):
    id: int
    predicted_depletion_date: Optional[datetime] = None
    restock_suggestion: Optional[int] = None
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    customer_name: str
    customer_email: Optional[str] = None
    total_amount: float
    risk_level: Optional[str] = "Low"

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class OrderItemOut(OrderItemBase):
    id: int
    order_id: int
    
    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    total_orders_today: int
    low_stock_alerts: int
    delayed_shipments: int
    revenue_today: float
