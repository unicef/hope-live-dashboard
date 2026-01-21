import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope_live.config.settings")

app = Celery("hope_live")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
