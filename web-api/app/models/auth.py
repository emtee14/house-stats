from datetime import datetime, UTC
from hashlib import sha256
from typing import List, TYPE_CHECKING

import bcrypt
from pydantic import EmailStr
from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship
import uuid

if TYPE_CHECKING:
    from app.models.billing import BillingLedger


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    email: EmailStr = Field(index=True)
    password: bytes = Field()

    first_name: str = Field()
    last_name: str = Field()

    stripe_id: str = Field(index=True, nullable=True)
    subscription_id: str = Field(index=True, nullable=True)

    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
    api_tokens: List["ApiToken"] = Relationship(back_populates="user")

    billing_ledgers: List["BillingLedger"] = Relationship(back_populates="user")

    def set_password(self, password: str):
        password_bytes = password.encode()
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        self.password = hashed_password

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password)


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "auth"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="auth.users.id")
    token_hash: bytes = Field()
    issued_at: datetime = Field(default_factory=lambda : datetime.now(UTC),
                                sa_column=Column(DateTime(timezone=True), nullable=False))
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    revoked: bool = Field(default=False)

    user: User = Relationship(back_populates="refresh_tokens")

    def set_token_hash(self, token: str):
        token_bytes = token.encode()
        hashed_token = sha256(token_bytes).digest()
        self.token_hash = hashed_token

    def revoke_token(self):
        self.revoked = True

class ApiToken(SQLModel, table=True):
    __tablename__ = "api_tokens"
    __table_args__ = {"schema": "auth"}
    id: str = Field(primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="auth.users.id")

    name: str = Field()

    token_hash: bytes = Field()

    issued_at: datetime = Field(default_factory=lambda : datetime.now(UTC),
                                     sa_column=Column(DateTime(timezone=True), nullable=False))
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    revoked: bool = Field(default=False)

    user: User = Relationship(back_populates="api_tokens")
