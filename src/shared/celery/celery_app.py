"""
Celery application configuration for the AI Agent Platform.
"""

from celery import Celery

from src.shared.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "ai_agent_platform",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=[
        "src.services.knowledge_base.tasks",
        "src.services.orchestration.tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_routes={
        "src.services.knowledge_base.tasks.*": {"queue": "knowledge_base"},
        "src.services.orchestration.tasks.*": {"queue": "orchestration"},
    },
    task_default_queue="default",
    task_default_exchange="default",
    task_default_exchange_type="direct",
    task_default_routing_key="default",
)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-executions": {
        "task": "src.services.execution_monitoring.tasks.cleanup_expired_executions",
        "schedule": 3600.0,  # Run every hour
    },
}

if __name__ == "__main__":
    celery_app.start() 