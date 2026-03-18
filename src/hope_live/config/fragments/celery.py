from celery.schedules import crontab  # type: ignore[import-untyped]

from hope_live.config import env

CELERY_TASK_DEFAULT_QUEUE = env("CELERY_TASK_DEFAULT_QUEUE")
CELERY_TASK_REVOKED_QUEUE = env("CELERY_TASK_REVOKED_QUEUE")

CELERY_BEAT_SCHEDULE = {
    "sync_daily_aggregates": {
        "task": "hope_live.analysis.tasks.schedule_sync_daily_aggregates",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2:00 AM UTC
        "args": (),  # Defaults to current + previous year
    },
}
