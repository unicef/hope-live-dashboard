"""
ASGI config for hope_live project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import logging
import os
import sys
from typing import Any, cast

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

logger = logging.getLogger(__name__)

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope_live.config.settings")
django_asgi_app = get_asgi_application()

websocket_application: Any | None = None

try:
    from hope_live.ws import routing

    websocket_patterns = cast("Any", routing.websocket_urlpatterns)
    websocket_application = AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_patterns)))
except ImportError as e:
    logger.warning(f"Could not import WebSocket routing: {e}")
except (AttributeError, KeyError, TypeError, ValueError) as e:
    logger.error(f"Error setting up WebSocket routing: {e}")

application_dict: dict[str, Any] = {
    "http": django_asgi_app,
}
if websocket_application is not None:
    application_dict["websocket"] = websocket_application

application = ProtocolTypeRouter(application_dict)

# Export the application
__all__ = ["application"]
