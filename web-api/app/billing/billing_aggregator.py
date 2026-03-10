import uuid
from datetime import datetime, UTC, timedelta
from typing import List

from sqlalchemy import ScalarResult, func
from sqlmodel import Session, select, update

from app.config import Config
from app.models.auth import User
from app.models.billing import Usage, BillingLedger, AggregationEvent
from app.billing.stripe_adapter import StripePaymentAdapter


class BillingAggregator:
    def __init__(self, session: Session):
        self._session = session

    def get_users(self, period_end: datetime = datetime.now(UTC)) -> ScalarResult[User]:
        stmt = (
            select(User)
            .where((User.id == Usage.user_id) & (Usage.timestamp <= period_end))
            .distinct(User.id)
        )
        results = self._session.exec(stmt)
        return results

    def aggregate_user_billing(self, user: User, upto: datetime = datetime.now(UTC)):
        stmt = select(
            func.sum(Usage.tokens), func.min(Usage.timestamp), func.max(Usage.timestamp)
        ).where(
            (Usage.user_id == user.id)
            & (Usage.timestamp <= upto)
            & (Usage.ledger_id == None) # noqa: E711
        )
        usage_stats = self._session.exec(stmt).one_or_none()

        if None not in usage_stats:
            total_tokens = usage_stats[0]
            period_start = usage_stats[1]
            period_end = usage_stats[2]
        else:
            raise ValueError("User has no usage recorded")

        new_ledger_entry = BillingLedger(
            user_id=user.id,
            total_tokens=total_tokens,
            timestamp=datetime.now(UTC),
            period_start=period_start,
            period_end=period_end,
        )

        self._session.add(new_ledger_entry)

        return new_ledger_entry

    def update_usage_events(self, ledger_entry: BillingLedger):
        stmt = (
            update(Usage)
            .where(
                (Usage.user_id == ledger_entry.user_id)
                & (Usage.timestamp <= ledger_entry.period_end)
                & (Usage.ledger_id == None) # noqa: E711
            )
            .values(ledger_id=ledger_entry.id)
        )
        self._session.exec(stmt)

        return ledger_entry

    def aggregate_usage_batch(self, users: List[uuid.UUID]):
        ledger_entries = []
        for user_id in users:
            user = self._session.get(User, user_id)
            if user is None:
                raise ValueError("Invalid user ID")
            ledger_entry = self.aggregate_user_billing(user)
            ledger_entries.append(ledger_entry)

        ledger_ids = [ledger.id for ledger in ledger_entries]
        return ledger_ids

    def aggregate_en_masse(self, billing_hour: int = 23) -> AggregationEvent:
        self._session.no_autoflush = True
        agg_event = AggregationEvent(
            run_time=0,  # temp
            timestamp=datetime.now(UTC),
        )
        self._session.add(agg_event)

        aggregator = BillingAggregator(self._session)

        date_today = datetime.today()
        date_today += timedelta(hours=billing_hour)

        users = aggregator.get_users(period_end=date_today)

        ledger_list = []
        for user in users:
            ledger_entry = self.aggregate_user_billing(user)
            ledger_list.append(ledger_entry)

        for ledger in ledger_list:
            stripe_instance = StripePaymentAdapter(Config.STRIPE_API_TOKEN)
            user = self._session.get(User, ledger.user_id)

            event_id = stripe_instance.log_new_billing_event(
                "api_requests",
                user.stripe_id,
                ledger.total_tokens,
            )

            ledger.stripe_event_id = event_id
            ledger.aggregation_event_id = agg_event.id
            aggregator.update_usage_events(ledger)

        run_time = int((datetime.now(UTC) - agg_event.timestamp).total_seconds() * 1000)
        agg_event.run_time = run_time

        self._session.commit()

        return agg_event