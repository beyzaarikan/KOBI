from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.operation_service import OperationService
from app.services.ai_agent import support_agent, inventory_agent
from app.schemas.operation import DailyOperationReport

router = APIRouter()

operation_service = OperationService()


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    intent: str
    answer: str
    requires_human: bool
    context_found: bool


class InventoryAnalysisResponse(BaseModel):
    analysis: list


@router.get("/daily-summary", response_model=DailyOperationReport)
async def get_daily_operation_summary(
    session: AsyncSession = Depends(get_db)
):
    return await operation_service.generate_daily_operation_report(session)


@router.post("/chat", response_model=ChatResponse)
async def chat_with_support(
    request: ChatMessage,
    session: AsyncSession = Depends(get_db)
):
    """Müşteri desteği chatbot endpoint'i"""
    result = await support_agent.handle_query(request.message, session)
    return result


@router.get("/inventory-analysis")
async def analyze_inventory(
    session: AsyncSession = Depends(get_db)
):
    """Envanter analiz raporu"""
    result = await inventory_agent.analyze_inventory(session)
    return {"analysis": result}