from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.models.models import Order
from app.schemas.schemas import OrderOut
from app.services.ai_agent import support_agent

router = APIRouter()

@router.get("/", response_model=List[OrderOut])
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    return result.scalars().all()

@router.post("/support-chat")
async def chat_with_support(query: dict, db: AsyncSession = Depends(get_db)):
    text = query.get("query", "")
    response = await support_agent.handle_query(text, db)
    return {"response": response}
