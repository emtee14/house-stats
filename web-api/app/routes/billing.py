from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from app.auth.deps import get_current_user
from app.db import get_session
from app.models.auth import User
from app.models.billing import Usage, BillingLedger

from datetime import datetime, UTC, timedelta
from typing import List
from fastapi import Query

from app.routes.schemas.billing import (
    UsageResponse,
    BillingLedgerResponse,
    BillingSummaryResponse,
    UsageSummaryResponse,
    UsageTrendsResponse,
    UsageTrendPoint
)

router = APIRouter(tags=["Billing"])

@router.get(
    "/api-usage",
    response_model=List[UsageResponse],
    summary="Get API usage for a user",
    description="Returns usage records for the authenticated user between the provided start and end timestamps."
)
def get_usage(
    start: datetime = Query(..., description="Start datetime for the usage window"),
    end: datetime = Query(..., description="End datetime for the usage window"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[UsageResponse]:

    stmt = select(Usage).where(
        (Usage.user_id == user.id)
        & (Usage.timestamp <= end)
        & (Usage.timestamp >= start)
    )

    results = session.exec(stmt).all()

    return [
        UsageResponse(
            api_route=u.api_route,
            tokens=u.tokens,
            timestamp=u.timestamp.isoformat(),
        )
        for u in results
    ]


@router.get(
    "/billing/history",
    response_model=List[BillingLedgerResponse],
    summary="Get billing history",
    description="Returns the user's billing ledger entries showing past billing periods and token usage."
)
def get_billing_history(
    limit: int = Query(12, description="Maximum number of billing periods to return"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[BillingLedgerResponse]:

    stmt = select(BillingLedger).where(
        BillingLedger.user_id == user.id
    ).order_by(BillingLedger.period_end.desc()).limit(limit)

    results = session.exec(stmt).all()

    return [
        BillingLedgerResponse(
            id=str(ledger.id),
            total_tokens=ledger.total_tokens,
            period_start=ledger.period_start.isoformat(),
            period_end=ledger.period_end.isoformat(),
            timestamp=ledger.timestamp.isoformat(),
            stripe_event_id=ledger.stripe_event_id,
        )
        for ledger in results
    ]


@router.get(
    "/billing/current-period",
    response_model=BillingSummaryResponse,
    summary="Get current billing period summary",
    description="Returns usage summary for the current billing period (last 28 days)."
)
def get_current_billing_period(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> BillingSummaryResponse:

    today = datetime.now(UTC)
    period_end = today.replace(day=28)
    if today.day > 28:
        if period_end.month == 12:
            period_end = period_end.replace(year=period_end.year + 1, month=1)
        else:
            period_end = period_end.replace(month=period_end.month + 1)

    period_start = period_end - timedelta(days=28)

    stmt = select(func.sum(Usage.tokens)).where(
        (Usage.user_id == user.id)
        & (Usage.timestamp >= period_start)
        & (Usage.timestamp <= period_end)
    )

    result = session.exec(stmt).one_or_none()
    current_tokens = result if result is not None else 0


    return BillingSummaryResponse(
        current_period_tokens=current_tokens,
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
        estimated_cost=None,
    )


@router.get(
    "/billing/usage/summary",
    response_model=UsageSummaryResponse,
    summary="Get usage summary",
    description="Returns aggregated usage statistics for the specified period."
)
def get_usage_summary(
    days: int = Query(30, description="Number of days to analyze"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UsageSummaryResponse:

    start_date = datetime.now(UTC) - timedelta(days=days)

    stmt = select(
        func.sum(Usage.tokens),
        func.count(Usage.id)
    ).where(
        (Usage.user_id == user.id)
        & (Usage.timestamp >= start_date)
    )

    result = session.exec(stmt).one_or_none()
    total_tokens = result[0] if result and result[0] else 0
    total_requests = result[1] if result and result[1] else 0

    avg_tokens = total_tokens / total_requests if total_requests > 0 else 0

    stmt = select(
        Usage.api_route,
        func.sum(Usage.tokens).label('total_tokens'),
        func.count(Usage.id).label('request_count')
    ).where(
        (Usage.user_id == user.id)
        & (Usage.timestamp >= start_date)
    ).group_by(Usage.api_route).order_by(func.sum(Usage.tokens).desc()).limit(10)

    route_results = session.exec(stmt).all()

    top_routes = [
        {
            "route": route.api_route,
            "tokens": route.total_tokens,
            "requests": route.request_count
        }
        for route in route_results
    ]

    return UsageSummaryResponse(
        total_tokens=total_tokens,
        total_requests=total_requests,
        average_tokens_per_request=round(avg_tokens, 2),
        top_routes=top_routes,
        period_days=days,
    )


@router.get(
    "/billing/usage/trends",
    response_model=UsageTrendsResponse,
    summary="Get usage trends",
    description="Returns daily usage trends over the specified date range."
)
def get_usage_trends(
    start: datetime = Query(..., description="Start date for trends"),
    end: datetime = Query(..., description="End date for trends"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UsageTrendsResponse:

    stmt = select(Usage).where(
        (Usage.user_id == user.id)
        & (Usage.timestamp >= start)
        & (Usage.timestamp <= end)
    ).order_by(Usage.timestamp)

    results = session.exec(stmt).all()

    from collections import defaultdict
    daily_stats = defaultdict(lambda: {"tokens": 0, "requests": 0})

    for usage in results:
        date_key = usage.timestamp.date().isoformat()
        daily_stats[date_key]["tokens"] += usage.tokens
        daily_stats[date_key]["requests"] += 1

    trends = [
        UsageTrendPoint(
            date=date,
            tokens=stats["tokens"],
            requests=stats["requests"]
        )
        for date, stats in sorted(daily_stats.items())
    ]

    return UsageTrendsResponse(trends=trends)
