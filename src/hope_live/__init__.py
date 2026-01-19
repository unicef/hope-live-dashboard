import django_stubs_ext as django_stubs

from .config.celery_app import app as celery_app
from .version import __version__

django_stubs.monkeypatch()
VERSION = __version__

__all__ = ("celery_app",)
