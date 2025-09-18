from typing import Any

from ..settings import DEBUG

FLAGS_STATE_LOGGING = DEBUG
FLAGS: dict[str, list[Any]] = {
    "LOCAL_LOGIN": [],
    "DEVELOP_DEBUG_TOOLBAR": [],
    "DJANGO_ADMIN": [],
}
