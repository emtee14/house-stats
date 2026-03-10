import time
import uuid
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from sqlmodel import Session

from app.billing.billing_aggregator import BillingAggregator
from app.billing.stripe_adapter import StripePaymentAdapter
from app.celery import celery_worker
from app.config import Config
from app.models.auth import User
from app.models.billing import Usage, AggregationEvent, BillingLedger
from app.tasks.base_task import DatabaseTask


@celery_worker.task(base=DatabaseTask)
def log_token_usage(user_id: UUID, endpoint: str,
                    bill_time: datetime, token_amount: int,
                    session: Session = None) -> None:
    new_charge = Usage(
        user_id=user_id,
        api_route=endpoint,
        tokens=token_amount,
        timestamp=bill_time,
    )

    session.add(new_charge)
    session.commit()
    print(f"Logged user {user_id} endpoint usage, charged {token_amount} tokens")


@celery_worker.task(base=DatabaseTask)
def aggregate_current_billing(session: Session = None, billing_hour: int = 23) -> uuid.UUID:
    aggregator = BillingAggregator(session)

    event = aggregator.aggregate_en_masse(billing_hour)

    return event.id
