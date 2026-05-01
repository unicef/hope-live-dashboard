from typing import TYPE_CHECKING
from unittest import mock

import pytest
from django.core.exceptions import ValidationError

from hope_live.utils.flags import debug, hostname, superuser, validate_bool

if TYPE_CHECKING:
    from django.http import HttpRequest


@pytest.mark.parametrize("value", ["true", "1", "yes", "t", "y", "false", "0", "no", "f", "n"])
def test_validate_bool(value):
    validate_bool(value)  # No exception should be raised


@pytest.mark.parametrize("value", ["a", "9"])
def test_validate_bool_fail(value):
    with pytest.raises(ValidationError):
        assert validate_bool(value)


@pytest.mark.parametrize("value", ["t", "tRue", "yes", "1"])
def test_superuser(rf, value, admin_user):
    request = rf.get("/")
    request.user = admin_user
    assert superuser(value, request)


@pytest.mark.parametrize("value", ["t", "tRue", "yes", "1"])
def test_debug(settings, value):
    settings.DEBUG = True
    assert debug(value)


@pytest.mark.parametrize("value", ["myserver.com", "myserver.com:888", "myserver.com:443"])
def test_hostname(value, rf):
    request: HttpRequest = rf.get("/")
    with mock.patch.object(request, "get_host", return_value=value):
        assert hostname("myserver.com", request)


def test_hostname_mismatch(rf):
    request: HttpRequest = rf.get("/")
    with mock.patch.object(request, "get_host", return_value="production.com"):
        assert not hostname("localhost", request)


@pytest.mark.parametrize("path", ["/api/data/", "/dal/autocomplete/", "/healthcheck/", "/autocomplete/user/"])
def test_show_ddt_excluded_paths(rf, settings, path):
    from hope_live.config.fragments.debug_toolbar import show_ddt

    settings.DEBUG = True
    request = rf.get(path)
    with mock.patch.object(request, "get_host", return_value="localhost:8000"):
        assert show_ddt(request) is False


@pytest.mark.django_db
def test_show_ddt_allowed_path(rf, settings):
    from flags.models import FlagState

    from hope_live.config.fragments.debug_toolbar import show_ddt

    settings.DEBUG = True
    FlagState.objects.create(
        name="DEVELOP_DEBUG_TOOLBAR",
        condition="hostname",
        value="localhost,127.0.0.1",
    )

    request = rf.get("/dashboard/")
    with mock.patch.object(request, "get_host", return_value="localhost:8000"):
        assert request.path == "/dashboard/"
        assert show_ddt(request) is True


@pytest.mark.django_db
def test_show_ddt_production_hostname(rf, settings):
    from flags.models import FlagState

    from hope_live.config.fragments.debug_toolbar import show_ddt

    settings.DEBUG = True
    FlagState.objects.create(
        name="DEVELOP_DEBUG_TOOLBAR",
        condition="hostname",
        value="localhost,127.0.0.1",
    )

    request = rf.get("/dashboard/")
    with mock.patch.object(request, "get_host", return_value="dashboard-hope-dev.unitst.org:443"):
        assert show_ddt(request) is False
