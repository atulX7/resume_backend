# app/celery_app.py
import multiprocessing

try:
    multiprocessing.set_start_method('spawn', force=True)
except RuntimeError:
    # The start method has already been set
    pass

from celery import Celery
from app.core.config import Settings
from app.core.logging import setup_logging

setup_logging()  # Set up central logging

settings = Settings()

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,   # Adjust as needed
    backend=settings.CELERY_BACKEND_URL,  # Adjust as needed
)
celery_app.conf.worker_hijack_root_logger = False

# Optionally, route tasks to specific queues:
celery_app.conf.task_routes = {
    "app.tasks.mock_interview.process_mock_interview_task": {"queue": "mock_interview"}
}

# Explicitly import the task module so that tasks get registered
import app.tasks.mock_interview
