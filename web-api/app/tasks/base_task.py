from celery import Task
from app.db import get_session

class DatabaseTask(Task):
    _session = None
    def __call__(self, *args, **kwargs):
        if "session" in kwargs:
            # Testing case — don't override
            return self.run(*args, **kwargs)

        self._session = get_session()
        return self.run(*args, session=self._session, **kwargs)
