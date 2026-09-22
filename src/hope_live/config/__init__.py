import os
import tempfile

from smart_env import SmartEnv

DJ_ENVIRON_DOC = "https://django-environ.readthedocs.io/en/latest/"
DJANGO_HELP_BASE = "https://docs.djangoproject.com/en/5.2/ref/settings"


def setting(anchor: str) -> str:
    return f"@see {DJANGO_HELP_BASE}#{anchor}"


DEFAULTS = {
    "ADMIN_EMAIL": (str, "", "admin", True, "Initial user created at first deploy"),
    "ADMIN_PASSWORD": (str, "", "", True, "Password for initial user created at first deploy"),
    "AZURE_CLIENT_ID": (str, "", "", "", ""),
    "AZURE_CLIENT_SECRET": (str, "", "", "", ""),
    "AZURE_TENANT_ID": (str, "", "", "", ""),
    "ALLOWED_HOSTS": (list, [], ["*"], False, ""),
    "CACHE_URL": (str, "", "", True, setting("cache-url")),
    "CELERY_TASK_DEFAULT_QUEUE": (str, "celery", "celery", False, "Default Celery queue"),
    "CELERY_TASK_REVOKED_QUEUE": (str, "revoked", "revoked", False, "Celery revoked tasks queue"),
    "CHANNEL_BROKER": (str, ""),
    "CONSTANCE_REDIS_URL": (str, "", "", True, "Redis server to store django-constance data"),
    "CSP_DEFAULT_SRC": (list, [], [], False, ""),
    "CSP_IMG_SRC": (list, [], [], False, ""),
    "CSRF_COOKIE_SECURE": (bool, True, False, True, setting("csrf-cookie-secure")),
    "CSRF_TRUSTED_ORIGINS": (list, ["http://localhost"], "", True, ""),
    "DATABASE_URL": (str, "sqlite://", "", "", f"{DJ_ENVIRON_DOC}types.html#environ-env-db-url"),
    "DATABASE_HOPE_URL": (str, "sqlite://", "", "", f"{DJ_ENVIRON_DOC}types.html#environ-env-db-url"),
    "DEBUG": (bool, False, "", "", ""),
    "DJANGO_ADMIN_URL": (
        str,
        "admin/",
        "admin/",
        False,
        "URL path for Django admin interface (without trailing slash)",
    ),
    "ENABLE_WEBSOCKETS": (bool, False, False, False, "Whether to enable WebSockets support."),
    "ENVIRONMENT": (str, "production", "develop", False, "Environment"),
    "EXTRA_APPS": (list, "", "", False, ""),  # nosec
    "EXTRA_AUTHENTICATION_BACKENDS": (list, [], [], False, "Extra authentications backends enabled to add."),
    "EXTRA_MIDDLEWARES": (list, "", "", False, ""),  # nosec
    "LOG_LEVEL": (str, "ERROR"),
    "MEDIA_ROOT": (
        str,
        os.path.join(tempfile.gettempdir(), "hope_portal", "media"),
        os.path.join(tempfile.gettempdir(), "hope_portal", "media"),
        False,
        "The root directory for media files.",
    ),
    "REDIS_URL": (str, "", "", True, "Redis Key/Value storage server"),
    "SECRET_KEY": (str, ""),
    "SENTRY_DSN": (str, ""),
    "SENTRY_ENABLE_TRACING": (bool, False, False, "", ""),
    "SENTRY_URL": (str, ""),
    "SESSION_COOKIE_HTTPONLY": (bool, True),
    "SESSION_COOKIE_AGE": (int, 86400),
    "SESSION_EXPIRE_AT_BROWSER_CLOSE": (bool, True),
    "SESSION_COOKIE_NAME": (str, "sessionid"),
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": (bool, True),
    "SECURE_HSTS_PRELOAD": (bool, True),
    "SECURE_HSTS_SECONDS": (int, 31536000, 0, False, setting("secure-hsts-seconds")),
    "SECURE_CONTENT_TYPE_NOSNIFF": (bool, True, True, False, setting("secure-content-type-nosniff")),
    "SECURE_PROXY_SSL_HEADER": (
        tuple,
        ("HTTP_X_FORWARDED_PROTO", "https"),
        ("HTTP_X_FORWARDED_PROTO", "https"),
        False,
        setting("secure-proxy-ssl-header"),
    ),
    "SECURE_REFERRER_POLICY": (
        str,
        "strict-origin-when-cross-origin",
        "strict-origin-when-cross-origin",
        False,
        setting("secure-referrer-policy"),
    ),
    "SECURE_SSL_REDIRECT": (bool, False, False, False, setting("secure-ssl-redirect")),
    "SOCIAL_AUTH_LOGIN_URL": (str, "/login/", "", False, ""),
    "SOCIAL_AUTH_RAISE_EXCEPTIONS": (bool, False, True, False),
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": (bool, True, False, False, ""),
    "SUPERUSERS": (list, [], [], False, ""),
    "STATIC_ROOT": (
        str,
        os.path.join(tempfile.gettempdir(), "hope_live", "static"),
        os.path.join(tempfile.gettempdir(), "hope_live", "static"),
        False,
        "The root directory for static files.",
    ),
    "STREAMING_BROKER_URL": (str, "", "", False, "The URL of the streaming broker."),
}

env = SmartEnv(**DEFAULTS)

# Load Celery app on Django startup so the Admin uses the configured backend
from .celery import app as celery_app  # noqa: E402

__all__ = ("env", "setting", "celery_app")
