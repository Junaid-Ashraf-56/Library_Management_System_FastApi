from celery import Celery
import os

celery_app = Celery(
    "library",
    broker=os.environ["CELERY_BROKER_URL"],
    backend=os.environ["CELERY_RESULT_BACKEND"],
)
