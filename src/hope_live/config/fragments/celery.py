from celery.schedules import crontab  # type: ignore[import-untyped]

CELERY_BEAT_SCHEDULE = {
    "sync_daily_aggregates": {
        "task": "hope_live.analysis.tasks.sync_daily_aggregates",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2:00 AM UTC
        "args": (),  # Defaults to current + previous year
    },
}
