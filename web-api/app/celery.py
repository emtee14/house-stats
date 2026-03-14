from celery import Celery
from celery.schedules import crontab

from app.settings import get_settings

settings = get_settings()

celery_worker = Celery(
    "app",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_results,
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
