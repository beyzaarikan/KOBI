from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.operation_service import OperationService
from app.schemas.operation import DailyOperationReport

router = APIRouter()

operation_service = OperationService()


@router.get("/daily-summary", response_model=DailyOperationReport)
async def get_daily_operation_summary(
    session: AsyncSession = Depends(get_db)
):
    return await operation_service.generate_daily_operation_report(session)