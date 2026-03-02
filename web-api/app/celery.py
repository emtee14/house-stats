from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from app.config import Config

celery_worker = Celery(
    "app",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND
)
celery_worker.conf.timezone = 'UTC'

celery_worker.conf.beat_schedule = {
    # Aggregate user billing usage daily at 11pm
    'aggregate-billing-sunday-00:00': {
        'task': 'app.tasks.billing.aggregate_current_billing',
        'schedule': crontab(hour="23"),
    },
}

import app.tasks.email
import app.tasks.billing