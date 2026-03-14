
from pydantic import BaseModel
from typing import List


class UsageResponse(BaseModel):
    api_route: str
    tokens: int
    timestamp: str


class BillingLedgerResponse(BaseModel):
    id: str
    total_tokens: int
    period_start: str
    period_end: str
    timestamp: str
    stripe_event_id: str | None = None


class BillingSummaryResponse(BaseModel):
    current_period_tokens: int
    period_start: str
    period_end: str
    estimated_cost: float | None = None


class UsageSummaryResponse(BaseModel):
    total_tokens: int
    total_requests: int
    average_tokens_per_request: float
    top_routes: List[dict]  # [{"route": str, "tokens": int, "requests": int}]
    period_days: int


class UsageTrendPoint(BaseModel):
    date: str
    tokens: int
    requests: int


class UsageTrendsResponse(BaseModel):
    trends: List[UsageTrendPoint]