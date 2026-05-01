import contextlib
from typing import TYPE_CHECKING, Any

from adminfilters.utils import parse_bool
from django.conf import settings
from django.core.exceptions import ValidationError
from flags import state as flag_state
from flags.conditions import conditions

if TYPE_CHECKING:
    from django.http import HttpRequest


@contextlib.contextmanager
def enable_flag(name: str) -> Any:
    flag_state.enable_flag(name)
    yield
    flag_state.disable_flag(name)


def validate_bool(value: str) -> None:
    if value.lower() not in ["true", "1", "yes", "t", "y", "false", "0", "no", "f", "n"]:
        raise ValidationError("Enter a valid bool")


@conditions.register("superuser", validator=validate_bool)  # type: ignore[untyped-decorator]
def superuser(value: str, request: "HttpRequest | None" = None, **kwargs: Any) -> bool:
    if request is None:
        return False
    return request.user.is_superuser == parse_bool(value)


@conditions.register("debug", validator=validate_bool)  # type: ignore[untyped-decorator]
def debug(value: str, **kwargs: Any) -> bool:
    return bool(parse_bool(value) == settings.DEBUG)


@conditions.register("hostname")  # type: ignore[untyped-decorator]
def hostname(value: str, request: "HttpRequest | None" = None, **kwargs: Any) -> bool:
    if request is None:
        return False
    host = request.get_host().split(":")[0]
    return host in value.split(",")
