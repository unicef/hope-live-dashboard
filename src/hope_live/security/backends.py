from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

from hope_live.models import User


class AnyUserAuthBackend(ModelBackend):
    """DEBUG Only smart auth backend  auto-create users."""

    def authenticate(
        self,
        request: HttpRequest,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> User | None:
        if settings.DEBUG:
            user, __ = get_user_model().objects.update_or_create(
                username=username,
                defaults={"is_staff": True, "is_active": True, "is_superuser": True},
            )
            return user
        return None
