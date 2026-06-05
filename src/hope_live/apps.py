from typing import TYPE_CHECKING, Any

from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models import Model

if TYPE_CHECKING:
    from .models import User


class Config(AppConfig):
    name = "hope_live"
    verbose_name = "Security"


def settings_context(request: Any) -> dict[str, Any]:
    return {"ENABLE_WEBSOCKETS": settings.ENABLE_WEBSOCKETS}


def on_login(sender: type[Model], user: "User", **kwargs: Any) -> None:
    if user.email in settings.SUPERUSERS or user.username in settings.SUPERUSERS:
        user.is_superuser = True
        user.is_staff = True
        user.save()


user_logged_in.connect(on_login)
