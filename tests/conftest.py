import contextlib
import os
import sys
from pathlib import Path

import pytest
import responses

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))
sys.path.insert(0, str(here))


def pytest_addoption(parser):
    # Helper to safely add options
    def safe_addoption(*args, **kwargs):
        with contextlib.suppress(Exception):
            parser.addoption(*args, **kwargs)

    safe_addoption(
        "--with-selenium",
        action="store_true",
        dest="enable_selenium",
        default=False,
        help="enable selenium tests",
    )
    safe_addoption(
        "--show-browser",
        "-S",
        action="store_true",
        dest="show_browser",
        default=False,
        help="will not start browsers in headless mode",
    )
    safe_addoption(
        "--driver",
        action="store",
        dest="driver",
        default="chrome",
        help="Browser driver to use (chrome, firefox, edge)",
    )
    safe_addoption(
        "--with-sentry",
        action="store_true",
        dest="with_sentry",
        default=False,
        help="enable sentry error logging",
    )
    safe_addoption(
        "--sentry-environment",
        action="store",
        dest="sentry_environment",
        default="test",
        help="set sentry environment",
    )


def pytest_configure(config):
    sys._called_from_pytest = True
    import logging

    from django.conf import settings

    # Silence noisy broken pipe warnings from django.server
    logging.disable(logging.CRITICAL)

    # Override settings for tests
    settings.ADMINS = ""
    settings.ALLOWED_HOSTS = ["*"]
    settings.DJANGO_SETTINGS_MODULE = "hope_live.config.settings"
    settings.FILE_STORAGE_DEFAULT = "django.core.files.storage.FileSystemStorage"
    settings.FILE_STORAGE_MEDIA = "django.core.files.storage.FileSystemStorage"
    settings.FILE_STORAGE_HOPE = "django.core.files.storage.FileSystemStorage"
    settings.CATCH_ALL_EMAIL = ""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CSRF_COOKIE_SECURE = False
    settings.MAILJET_API_KEY = ""
    settings.MAILJET_SECRET_KEY = ""
    settings.MAILJET_TEMPLATE_REPORT_READY = ""
    settings.MAILJET_TEMPLATE_ZIP_PASSWORD = ""
    settings.MEDIA_ROOT = "/tmp/media"
    settings.SECURE_HSTS_PRELOAD = False
    settings.SECURE_SSL_REDIRECT = False
    settings.SECRET_KEY = "123"
    settings.SENTRY_ENVIRONMENT = ""
    settings.SENTRY_URL = ""
    settings.SESSION_COOKIE_SECURE = False
    settings.SESSION_COOKIE_NAME = "hope_live_test"
    settings.SESSION_COOKIE_DOMAIN = ""
    settings.STATIC_ROOT = "/tmp/static"
    settings.SIGNING_BACKEND = "django.core.signing.TimestampSigner"
    settings.WP_PRIVATE_KEY = ""
    if not config.option.with_sentry:
        os.environ["SENTRY_DSN"] = ""
    else:
        os.environ["SENTRY_ENVIRONMENT"] = config.option.sentry_environment

    # Enable selenium if flag or marker is used
    enable_sel = getattr(config.option, "enable_selenium", False) or "--with-selenium" in sys.argv
    config.option.enable_selenium = enable_sel or ("selenium" in getattr(config.option, "markexpr", ""))

    config.addinivalue_line("markers", "skip_test_if_env(env): this mark skips the tests for the given env")
    import django

    django.setup()

    config.addinivalue_line("markers", "admin: mark test as admin test")
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "django_db: mark test as requiring django database")
    config.addinivalue_line("markers", "skip_models: skip specific models in tests")
    config.addinivalue_line("markers", "skip_buttons: skip specific buttons in tests")
    config.addinivalue_line("markers", "asyncio: mark test as async test")
    config.addinivalue_line("markers", "selenium: marks tests that require selenium browser")

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(settings.STATIC_ROOT, exist_ok=True)


def pytest_runtest_setup(item):
    driver = item.config.getoption("--driver") or ""

    if driver.lower() == "firefox" and list(item.iter_markers(name="skip_if_firefox")):
        pytest.skip("Test skipped because Firefox")
    if driver.lower() == "safari" and list(item.iter_markers(name="skip_if_safari")):
        pytest.skip("Test skipped because Safari")
    if driver.lower() == "edge" and list(item.iter_markers(name="skip_if_edge")):
        pytest.skip("Test skipped because Edge")

    env_names = [mark.args[0] for mark in item.iter_markers(name="skip_test_if_env")]
    if env_names and item.config.getoption("--env") in os.environ:
        pytest.skip(f"Test skipped because env {env_names!r} is present")


def pytest_collection_modifyitems(config, items):
    # Fix: properly check both flag and marker expression
    enable_sel = getattr(config.option, "enable_selenium", False)
    markexpr = getattr(config.option, "markexpr", "")

    if not enable_sel and "selenium" not in markexpr:
        skip_mymarker = pytest.mark.skip(reason="selenium not enabled")
        for item in items:
            if item.get_closest_marker("selenium"):
                item.add_marker(skip_mymarker)
    else:
        # Enable selenium if marker is used
        config.option.enable_selenium = True


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def user_factory():
    from factories import UserFactory

    return UserFactory


@pytest.fixture
def office_factory():
    from factories import OfficeFactory

    return OfficeFactory


@pytest.fixture
def program_factory():
    from factories import ProgramFactory

    return ProgramFactory


@pytest.fixture
def group_factory():
    from factories import GroupFactory

    return GroupFactory


@pytest.fixture
def user_role_factory():
    from factories import UserRoleFactory

    return UserRoleFactory


@pytest.fixture
def admin_user(db):
    from hope_live.models import User

    return User.objects.create_superuser(username="admin", email="admin@test.com", password="password")


@pytest.fixture(scope="session")
def download_path(tmp_path_factory):
    """Provide a temporary download directory for browser tests."""
    return str(tmp_path_factory.mktemp("downloads"))


@pytest.fixture
def live_server_with_static(live_server, settings):
    """
    Wrap the live_server with StaticFilesHandler for Selenium tests.
    Similar to hct-mis implementation.
    """

    settings.STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }

    class StaticFilesLiveServer:
        def __init__(self, live_server):
            self.live_server = live_server
            self.url = live_server.url

        def __getattr__(self, name):
            return getattr(self.live_server, name)

    return StaticFilesLiveServer(live_server)


@pytest.fixture
def browser(sb, live_server_with_static, admin_user):
    """
    Provide a SeleniumBase browser instance bound to the live server.
    Replaces the raw Selenium driver to use SeleniumBase's smart waits.
    """
    sb.live_server_url = live_server_with_static.url

    original_open = sb.open

    def custom_open(url):
        if url.startswith("http"):
            original_open(url)
        else:
            original_open(f"{sb.live_server_url}{url}")

    sb.open = custom_open

    def login_as_user(user=None):
        from django.conf import settings
        from django.test import Client

        target_user = user or admin_user
        client = Client()
        client.force_login(target_user)
        cookie_name = settings.SESSION_COOKIE_NAME
        cookie_value = client.cookies[cookie_name].value
        sb.open("/login/")
        sb.add_cookie({"name": cookie_name, "value": cookie_value, "path": "/"})

    sb.login_as_user = login_as_user
    return sb
