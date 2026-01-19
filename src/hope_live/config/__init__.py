from smart_env import SmartEnv

DJ_ENVIRON_DOC = "https://django-environ.readthedocs.io/en/latest/"
DJANGO_HELP_BASE = "https://docs.djangoproject.com/en/5.2/ref/settings"


def setting(anchor: str) -> str:
    return f"@see {DJANGO_HELP_BASE}#{anchor}"


DEFAULTS = {
    "AZURE_CLIENT_ID": (str, "", "", "", ""),
    "AZURE_CLIENT_SECRET": (str, "", "", "", ""),
    "AZURE_TENANT_KEY": (str, "", "", "", ""),
    "ALLOWED_HOSTS": (list, [], ["*"], False, ""),
    "CACHE_URL": (str, "", "", True, setting("cache-url")),
    "CELERY_BROKER_URL": (str, "", "", True, "Celery Broker URL"),
    "CHANNEL_BROKER": (str, ""),
    "CONSTANCE_REDIS_URL": (str, "", "", True, "Redis server to store django-constance data"),
    "CSP_DEFAULT_SRC": (list, [], [], False, ""),
    "CSP_IMG_SRC": (list, [], [], False, ""),
    "CSRF_COOKIE_SECURE": (bool, True, False, True, setting("csrf-cookie-secure")),
    "CSRF_TRUSTED_ORIGINS": (list, ["http://localhost"], "", True, ""),
    "DATABASE_URL": (str, "sqlite://", "", "", f"{DJ_ENVIRON_DOC}types.html#environ-env-db-url"),
    "DATABASE_HOPE_URL": (str, "sqlite://", "", "", f"{DJ_ENVIRON_DOC}types.html#environ-env-db-url"),
    "DEBUG": (bool, False, "", "", ""),
    "ENVIRONMENT": (str, "production", "develop", False, "Environment"),
    "EXTRA_APPS": (list, "", "", False, ""),  # nosec
    "EXTRA_AUTHENTICATION_BACKENDS": (list, [], [], False, "Extra authentications backends enabled to add."),
    "EXTRA_MIDDLEWARES": (list, "", "", False, ""),  # nosec
    "LOG_LEVEL": (str, "ERROR"),
    "REDIS_URL": (str, "", "", True, "Redis Key/Value storage server"),
    "SECRET_KEY": (str, ""),
    "SENTRY_DSN": (str, ""),
    "SENTRY_ENABLE_TRACING": (bool, False, False, "", ""),
    "SENTRY_URL": (str, ""),
    "SESSION_COOKIE_HTTPONLY": (bool, True),
    "SESSION_COOKIE_NAME": (str, "sessionid"),
    "SOCIAL_AUTH_LOGIN_URL": (str, "/login/", "", False, ""),
    "SOCIAL_AUTH_RAISE_EXCEPTIONS": (bool, False, True, False),
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": (bool, True, False, False, ""),
    "SUPERUSERS": (list, [], [], False, ""),
    "STREAMING_BROKER_URL": (str, "", "", True, "RabbitMQ Server address"),
}

env = SmartEnv(**DEFAULTS)
