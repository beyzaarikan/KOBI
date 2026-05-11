from pydantic import BaseModel
from typing import Dict, List


class OperationMetrics(BaseModel):
    total_orders: int
    to_prepare: int
    to_package: int
    to_ship: int
    delayed: int
    waiting_stock: int
    critical_stock_products: int


class DailyOperationReport(BaseModel):
    summary: str
    tasks: Dict[str, List[str]]
    priorities: List[str]
    raw_metrics: OperationMetrics