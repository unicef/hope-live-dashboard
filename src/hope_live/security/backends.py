from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.contrib.auth.models import _User


class AnyUserAuthBackend(ModelBackend):
    """DEBUG Only smart auth backend  auto-create users."""

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> "_User | None":
        user: _User
        if settings.DEBUG:
            user, __ = get_user_model().objects.update_or_create(
                username=username,
                defaults={"is_staff": True, "is_active": True, "is_superuser": True},
            )
            return user
        return None
