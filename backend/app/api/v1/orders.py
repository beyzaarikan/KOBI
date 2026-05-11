from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.db.session import get_db
from app.models.models import Order
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