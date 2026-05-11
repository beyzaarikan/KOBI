from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import Order, Shipment
from app.schemas.schemas import OrderOut
from app.services.ai_agent import support_agent

router = APIRouter()


# ─── Request/Response Modelleri ───────────────
class ChatRequest(BaseModel):
    message: str  # "query" yerine "message" — daha anlamlı


class ChatResponse(BaseModel):
    intent: str
    answer: str
    requires_human: bool
    context_found: bool


# ─── Endpointler ──────────────────────────────
@router.get("/", response_model=List[OrderOut])
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    return result.scalars().all()


@router.post("/support-chat", response_model=ChatResponse)
async def chat_with_support(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Yöneticinin doğal dilde yazdığı soruyu alır,
    intent tespiti + entity extraction yaparak DB'den context çeker,
    AI ile cevap üretir.

    Örnek istek:
        { "message": "128 numaralı sipariş nerede?" }

    Örnek cevap:
        {
            "intent": "SHIPMENT_STATUS",
            "answer": "128 numaralı sipariş kargoda...",
            "requires_human": false,
            "context_found": true
        }
    """
    result = await support_agent.handle_query(request.message, db)
    return ChatResponse(**result)


@router.get("/delayed-shipments")
async def get_delayed_shipments(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(Shipment, Order)
        .join(Order, Shipment.order_id == Order.id)
        .where(Shipment.estimated_delivery < now)
        .where(~Shipment.status.ilike("%delivered%"))
    )

    delayed_shipments = []

    for shipment, order in result.all():
        delay_days = 0
        if shipment.estimated_delivery:
            delay_days = (now.date() - shipment.estimated_delivery.date()).days

        customer_message = (
            f"Merhaba {order.customer_name}, {order.id} numaralı siparişinizin "
            f"teslimatında {delay_days} günlük bir gecikme görünüyor. "
            "Süreci takip ediyoruz ve en kısa sürede sizi bilgilendireceğiz."
        )

        manager_summary = (
            f"{order.id} numaralı sipariş {delay_days} gündür gecikmiş görünüyor. "
            f"Kargo durumu: {shipment.status}. Müşterinin bilgilendirilmesi önerilir."
        )

        delayed_shipments.append({
            "order_id": order.id,
            "customer_name": order.customer_name,
            "shipment_status": shipment.status,
            "estimated_delivery_date": shipment.estimated_delivery,
            "delay_days": delay_days,
            "customer_message": customer_message,
            "manager_summary": manager_summary
        })

    return delayed_shipments