"""Celery application configuration for async task processing."""
from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "domainhunter",
    broker=settings.redis_url,
    backend=settings.redis_url
)

# Import tasks to register them
from app.core import tasks  # noqa: E402, F401

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=900,  # 15 minutes per task (100 domains * 15s timeout)
    task_soft_time_limit=870,  # 14.5 minutes soft limit
    worker_prefetch_multiplier=1,  # Disable prefetching for better load balancing
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks (memory management)
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
    task_default_retry_delay=60,  # 1 minute delay before retry
    task_max_retries=2,  # Max 2 retries for transient failures
    result_expires=3600,  # Results expire after 1 hour
)

