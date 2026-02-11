import logging
import os
from typing import Any

from celery import Celery  # type: ignore[import-untyped]

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope_live.config.settings")

app = Celery("hope_live")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
# Explicitly list the apps to ensure tasks are discovered
app.autodiscover_tasks(packages=["hope_live.analysis"])

logger = logging.getLogger(__name__)


@app.task(bind=True)  # type: ignore[untyped-decorator]
def debug_task(self: Any) -> None:
    logger.info(f"Request: {self.request!r}")
