from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel, Relationship
import uuid

from app.models.auth import User


class Usage(SQLModel, table=True):
    __tablename__ = "endpoint_usage"
    __table_args__ = {"schema": "billing"}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="auth.users.id")

    api_route: str = Field()
    tokens: int = Field()
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    ledger_id: uuid.UUID = Field(foreign_key="billing.billing_ledger.id", nullable=True)

    billing_ledger: "BillingLedger" = Relationship(back_populates="cost_items")


class BillingLedger(SQLModel, table=True):
    __tablename__ = "billing_ledger"
    __table_args__ = {"schema": "billing"}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="auth.users.id")

    total_tokens: int = Field()

    period_start: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    period_end: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    stripe_event_id: str = Field(nullable=True)
    aggregation_event_id: uuid.UUID = Field(
        foreign_key="billing.aggregation_event.id", nullable=True
    )

    cost_items: List[Usage] = Relationship(back_populates="billing_ledger")
    user: User = Relationship(back_populates="billing_ledgers")
    aggregation_event: "AggregationEvent" = Relationship(
        back_populates="billing_ledgers"
    )


class AggregationEvent(SQLModel, table=True):
    __tablename__ = "aggregation_event"
    __table_args__ = {"schema": "billing"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_time: int = Field()
    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    billing_ledgers: List[BillingLedger] = Relationship(
        back_populates="aggregation_event"
    )
