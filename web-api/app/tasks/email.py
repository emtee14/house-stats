from app.celery import celery_worker


@celery_worker.task
def send_email():
    print("send_email")
