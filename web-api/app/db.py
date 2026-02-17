from sqlalchemy import text
from sqlmodel import SQLModel, create_engine, Session
from app.config import Config

from app.models.auth import User

engine = create_engine(
    Config.DATABASE_URL,
)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        conn.commit()
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session