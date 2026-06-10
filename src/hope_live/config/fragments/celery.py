from celery.schedules import crontab  # type: ignore[import-untyped]

from hope_live.config import env

# Required by django-celery-boost to track task status
CELERY_BROKER_URL = env("REDIS_URL") or "redis://127.0.0.1:6379/1"
CELERY_RESULT_BACKEND = env("REDIS_URL") or "redis://127.0.0.1:6379/1"
CELERY_TASK_IGNORE_RESULT = False

CELERY_TASK_DEFAULT_QUEUE = env("CELERY_TASK_DEFAULT_QUEUE")
CELERY_TASK_REVOKED_QUEUE = env("CELERY_TASK_REVOKED_QUEUE")

CELERY_BEAT_SCHEDULE = {
    "sync_daily_aggregates": {
        "task": "hope_live.analysis.tasks.schedule_sync_daily_aggregates",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2:00 AM UTC
        "args": (),  # Defaults to current + previous year
    },
}
