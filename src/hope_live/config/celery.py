import logging
import os
from typing import Any

from celery import Celery  # type: ignore[import-untyped]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope_live.config.settings")

app = Celery("hope_live")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(packages=["hope_live.analysis"])

logger = logging.getLogger(__name__)


@app.task(bind=True)  # type: ignore[untyped-decorator]
def debug_task(self: Any) -> None:
    logger.info(f"Request: {self.request!r}")
