from celery import Celery

from app.config import Config

celery_worker = Celery(
    "app",
    broker=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,

)

import app.tasks.email

# celery_worker.autodiscover_tasks(["app.tasks"])