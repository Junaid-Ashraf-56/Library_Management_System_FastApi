import os

from celery import Celery

celery_app = Celery(
    "library",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
    include=["app.tasks.receipt_tasks"],
)

celery_app.conf.update(
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    task_track_started=True,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
)
