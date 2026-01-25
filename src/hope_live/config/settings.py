from pathlib import Path

from . import env

SETTINGS_DIR = Path(__file__).parent
PACKAGE_DIR = SETTINGS_DIR.parent
DEVELOPMENT_DIR = PACKAGE_DIR.parent.parent

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")


INSTALLED_APPS = [
    "daphne",
    "channels",
    "hope_live.theme",
    "hope_live.web",
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "unfold.contrib.location_field",
    "unfold.contrib.constance",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "unicef_security",
    "csp",
    "debug_toolbar",
    "social_django",
    "admin_extra_buttons",
    "django_extensions",
    "adminactions",
    "issues",
    "smart_env",
    "adminfilters",
    "adminfilters.depot",
    "constance",
    "tailwind",
    "flags",
    "hope_live",
    "hope_live.ws",
    *env("EXTRA_APPS"),
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    *env("EXTRA_MIDDLEWARES"),
]

ROOT_URLCONF = "hope_live.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            str(PACKAGE_DIR / "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "constance.context_processors.config",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "hope_live.web.context_processors.app",
            ],
            "libraries": {
                "unfold": "unfold.templatetags.unfold",
            },
            "builtins": ["unfold.templatetags.unfold"],
        },
    },
]

WSGI_APPLICATION = "hope_live.config.wsgi.application"

ASGI_APPLICATION = "hope_live.config.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("CHANNEL_BROKER") or env("REDIS_URL")],
        },
    },
}


DATABASES = {
    "default": env.db("DATABASE_URL"),
    "hope": env.db("DATABASE_HOPE_URL"),
}

DATABASE_ROUTERS = ["hope_live.db_routers.HopeRouter"]

CACHE_URL = env("CACHE_URL")

if CACHE_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": CACHE_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
            },
            "TIMEOUT": 60 * 60 * 24,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
            "TIMEOUT": 60 * 60 * 24,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
AUTH_USER_MODEL = "hope_live.User"
SUPERUSERS = env("SUPERUSERS")

AUTHENTICATION_BACKENDS = (
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
    "django.contrib.auth.backends.ModelBackend",
    *env("EXTRA_AUTHENTICATION_BACKENDS"),
)

LANGUAGE_CODE = "en-us"
ugettext = lambda s: s  # noqa E731
LANGUAGES = (
    ("es", ugettext("Spanish")),  # type: ignore[no-untyped-call]
    ("fr", ugettext("French")),  # type: ignore[no-untyped-call]
    ("en", ugettext("English")),  # type: ignore[no-untyped-call]
    ("ar", ugettext("Arabic")),  # type: ignore[no-untyped-call]
)

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = str(DEVELOPMENT_DIR / "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

LOGIN_URL = "web:login"
LOGIN_REDIRECT_URL = "web:dashboard"
LOGOUT_REDIRECT_URL = "web:login"

from .fragments.app import *  # noqa: E402 F403
from .fragments.celery import *  # noqa: E402 F403  # noqa: E402 F403
from .fragments.constance import *  # noqa: E402 F403
from .fragments.csp import *  # noqa: E402 F403
from .fragments.debug_toolbar import *  # noqa: E402 F403
from .fragments.flags import *  # noqa: E402 F403
from .fragments.issues import *  # noqa: E402 F403
from .fragments.sentry import *  # noqa: E402 F403
from .fragments.social_auth import *  # noqa: E402 F403
from .fragments.streaming import *  # noqa: E402 F403
from .fragments.tailwind import *  # noqa: E402 F403
from .fragments.unfold import *  # noqa: E402 F403
