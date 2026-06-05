from pathlib import Path

from . import env

SETTINGS_DIR = Path(__file__).parent
PACKAGE_DIR = SETTINGS_DIR.parent
DEVELOPMENT_DIR = PACKAGE_DIR.parent.parent
APPEND_SLASH = True
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")
DJANGO_ADMIN_URL = env("DJANGO_ADMIN_URL")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")
ENABLE_WEBSOCKETS = env("ENABLE_WEBSOCKETS")


# Application definition

INSTALLED_APPS = [
    "daphne",
    "channels",
    "hope_live.theme",
    "hope_live.web",
    "adminactions",
    "unicef_security",
    "django.contrib.admin",  # required
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "csp",
    "debug_toolbar",
    "django_extensions",
    "social_django",
    "admin_extra_buttons",
    "django_celery_boost",
    "issues",
    "smart_env",
    "adminfilters",
    "adminfilters.depot",
    "constance",
    "tailwind",
    "flags",
    "hope_live",
    "hope_live.ws",
    "hope_live.analysis",
    "widget_tweaks",
    "django_celery_beat",
    "rest_framework",
    "drf_spectacular",
    *env("EXTRA_APPS"),
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
                "hope_live.analysis.context_processors.available_years",
                "unicef_security.context_processors.current_state",
                "hope_live.apps.settings_context",
            ],
        },
    },
]

WSGI_APPLICATION = "hope_live.config.wsgi.application"

ASGI_APPLICATION = "hope_live.config.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(env("CHANNEL_BROKER") or env("REDIS_URL")).replace("localhost", "127.0.0.1") + "?protocol=2"],
        },
    },
}


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": env.db("DATABASE_URL"),
    "hope": env.db("DATABASE_HOPE_URL"),
}

CACHE_URL = env("CACHE_URL")

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

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

LOCALE_PATHS = [
    DEVELOPMENT_DIR / "locale",
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = env.str("STATIC_ROOT")


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

LOGIN_URL = "web:login"
LOGIN_REDIRECT_URL = "web:dashboard"

from .fragments.app import *  # noqa: E402 F403
from .fragments.celery import *  # noqa: E402 F403
from .fragments.constance import *  # noqa: E402 F403
from .fragments.csp import *  # noqa: E402 F403
from .fragments.debug_toolbar import *  # noqa: E402 F403
from .fragments.drf import *  # noqa: E402 F403
from .fragments.flags import *  # noqa: E402 F403
from .fragments.issues import *  # noqa: E402 F403
from .fragments.sentry import *  # noqa: E402 F403
from .fragments.social_auth import *  # noqa: E402 F403
from .fragments.streaming import *  # noqa: E402 F403
from .fragments.tailwind import *  # noqa: E402 F403
