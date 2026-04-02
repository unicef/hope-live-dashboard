from typing import Any

from ..settings import DEBUG

FLAGS_STATE_LOGGING = DEBUG
FLAGS: dict[str, list[Any]] = {
    "LOCAL_LOGIN": [
        {"condition": "hostname", "value": "localhost,127.0.0.1"},
    ]
    if DEBUG
    else [],
    "DEVELOP_DEBUG_TOOLBAR": [
        {"condition": "hostname", "value": "localhost,127.0.0.1"},
    ]
    if DEBUG
    else [],
    "DJANGO_ADMIN": [],
}

# Register flag conditions
from hope_live.utils.flags import *  # noqa: E402 F403
