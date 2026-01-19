from .. import env

CELERY_BROKER_URL = env("CELERY_BROKER_URL") or env("REDIS_URL")
CELERY_IGNORE_RESULT = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULE = {
    "update-dashboard-cache-every-hour": {
        "task": "hope_live.tasks.update_dashboard_cache",
        "schedule": 3600.0,
    },
}
