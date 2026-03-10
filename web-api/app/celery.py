from celery import Celery
from celery.schedules import crontab

from app.config import Config

celery_worker = Celery(
    "app",
    broker=Config.CELERY_BROKER_URL,
    result_backend=Config.CELERY_RESULT_BACKEND,
)
celery_worker.conf.timezone = "UTC"

celery_worker.conf.beat_schedule = {
    # Aggregate user billing usage daily at 11pm
    "aggregate-billing-everyday-23:00": {
        "task": "app.tasks.billing.sched_aggregate_current_billing",
        "schedule": crontab(hour="23"),
    },
}


# celery_worker.autodiscover_tasks(["app.tasks"])
