# backend/celery_app.py
import os
from celery import Celery
from dotenv import load_dotenv
from core.config import get_settings

load_dotenv()
settings = get_settings()

BROKER_URL = os.getenv("BROKER_URL", settings.REDIS_URL)
RESULT_BACKEND = os.getenv("RESULT_BACKEND", settings.REDIS_URL)

app = Celery("workers", broker=BROKER_URL, backend=RESULT_BACKEND)

app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="default",
    result_expires=3600,
    enable_utc=True,
    timezone="UTC",
    task_routes={
        "workers.tasks.embedding_tasks.*": {"queue": "embeddings"},
        "workers.tasks.upload_tasks.*": {"queue": "uploads"},
        "workers.tasks.cleanup_tasks.*": {"queue": "cleanup"},
    },
)
