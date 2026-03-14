from celery import Task
from sqlmodel import Session

from app.db import create_engine_from_settings
from app.settings import get_settings


class DatabaseTask(Task):
    _session = None

    def __call__(self, *args, **kwargs):
        if "session" in kwargs:
            # Testing case — don't override
            return self.run(*args, **kwargs)

        engine = create_engine_from_settings(get_settings())
        with Session(engine) as session:
            self._session = session
            return self.run(*args, session=session, **kwargs)
