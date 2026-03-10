from sqlmodel import create_engine, Session
from app.config import Config



engine = create_engine(
    Config.DATABASE_URL,
)


def get_session():
    with Session(engine) as session:
        yield session
