from datetime import datetime, UTC

from sqlalchemy import ScalarResult, func
from sqlmodel import Session, select, update

from app.models.auth import User
from app.models.billing import Usage, BillingLedger


class BillingAggregator:
    def __init__(self, session: Session):
        self._session = session

    def get_users(self, period_end: datetime = datetime.now(UTC)) -> ScalarResult[User]:
        stmt = select(User).where((User.id == Usage.user_id) & (Usage.timestamp <= period_end))
        results = self._session.exec(stmt)
        return results

    def aggregate_user_billing(self, user: User, upto: datetime = datetime.now(UTC)):
        stmt = (select(func.sum(Usage.tokens), func.min(Usage.timestamp), func.max(Usage.timestamp))
                .where((Usage.user_id == user.id) & (Usage.timestamp <= upto) & (Usage.ledger_id == None)))
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

        stmt = update(Usage) \
                .where((Usage.user_id == user.id) & (Usage.timestamp <= upto) & (Usage.ledger_id == None)) \
                .values(ledger_id=new_ledger_entry.id)
        self._session.exec(stmt)

        self._session.commit()

        return new_ledger_entry
