from sqlmodel import Field, Session, SQLModel, create_engine, select
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: bytes = Field(default_factory=lambda : uuid.uuid4().bytes, primary_key=True)
    email: str = Field(index=True)
    name: str = Field()
