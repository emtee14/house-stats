from celery import Celery
from celery.schedules import crontab

from app.settings import get_settings

settings = get_settings()

celery_worker = Celery(
    "app",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_worker.conf.timezone = "UTC"

celery_worker.conf.beat_schedule = {
    # Aggregate user billing usage daily at 11pm
    "aggregate-billing-everyday-23:00": {
        "task": "app.tasks.billing.sched_aggregate_current_billing",
        "schedule": crontab(hour="23"),
    },
}


from app.tasks import billing #noqa: E402,F401
from app.tasks import stats #noqa: E402,F401