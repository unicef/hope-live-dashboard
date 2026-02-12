"""
ASGI config for hope_live project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import logging
import os
import sys

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

try:
    from hope_live.ws import routing

    websocket_application = AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)))
except ImportError as e:
    logger.warning(f"Could not import WebSocket routing: {e}")
    websocket_application = None
except (AttributeError, KeyError, TypeError, ValueError) as e:
    # Catch specific exceptions that could occur during WebSocket setup
    # - AttributeError: missing attribute in routing module
    # - KeyError: missing key in configuration
    # - TypeError: wrong type passed to a function
    # - ValueError: invalid value passed to a function
    logger.error(f"Error setting up WebSocket routing: {e}")
    websocket_application = None

# Define the main ASGI application
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": websocket_application or None,
    }
)

# Export the application
__all__ = ["application"]
