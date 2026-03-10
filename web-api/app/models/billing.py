from datetime import datetime
from typing import List

from sqlmodel import Field, SQLModel, Relationship
import uuid


class Usage(SQLModel, table=True):
    __tablename__ = "endpoint_usage"
    __table_args__ = {"schema": "billing"}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="auth.users.id")

    api_route: str = Field()
    tokens: int = Field()
    timestamp: datetime = Field()

    ledger_id: uuid.UUID = Field(foreign_key="billing.billing_ledger.id", nullable=True)

    billing_ledger: "BillingLedger" = Relationship(back_populates="cost_items")



class BillingLedger(SQLModel, table=True):
    __tablename__ = "billing_ledger"
    __table_args__ = {"schema": "billing"}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="auth.users.id")

    total_tokens: int = Field()

    period_start: datetime = Field()
    period_end: datetime = Field()
    timestamp: datetime = Field()

    cost_items: List[Usage] = Relationship(back_populates="billing_ledger")
