from app.db.session import Base
from sqlalchemy import Column, Integer, String, DateTime, func, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    customer = "customer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.admin)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    sku = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Float, nullable=False)
    inventory_health_score = Column(Float, default=100.0)
    
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    movements = relationship("InventoryMovement", back_populates="product")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    current_stock = Column(Integer, default=0)
    threshold = Column(Integer, default=10)
    predicted_depletion_date = Column(DateTime(timezone=True), nullable=True)
    restock_suggestion = Column(Integer, nullable=True)
    
    product = relationship("Product", back_populates="inventory")

class MovementType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    change_amount = Column(Integer, nullable=False)
    type = Column(Enum(MovementType), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String)
    
    product = relationship("Product", back_populates="movements")

class OrderStatus(str, enum.Enum):
    preparing = "preparing"
    shipped = "shipped"
    delivered = "delivered"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String)
    status = Column(Enum(OrderStatus), default=OrderStatus.preparing)
    total_amount = Column(Float, default=0.0)
    risk_level = Column(String, default="Low") # Low, Medium, High
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    items = relationship("OrderItem", back_populates="order")
    shipment = relationship("Shipment", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    tracking_number = Column(String, nullable=True)
    status = Column(String, default="Pending")
    estimated_delivery = Column(DateTime(timezone=True), nullable=True)
    is_delayed = Column(Integer, default=0) # 0 False, 1 True
    
    order = relationship("Order", back_populates="shipment")

class AILog(Base):
    __tablename__ = "ai_logs"
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String)
    prompt = Column(String)
    response = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default="pending") # pending, completed
    priority = Column(String, default="normal") # normal, high, critical
    created_by_ai = Column(Integer, default=1) # 1 True, 0 False
    created_at = Column(DateTime(timezone=True), server_default=func.now())
