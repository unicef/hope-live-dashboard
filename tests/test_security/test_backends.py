from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from hope_live.security.backends import AnyUserAuthBackend

User = get_user_model()


@pytest.mark.django_db
def test_debug_mode_auto_user_creation():
    backend = AnyUserAuthBackend()
    request = HttpRequest()

    with patch("hope_live.security.backends.settings.DEBUG", True):
        user = backend.authenticate(request, username="debug_user", password="any")

        assert user is not None
        assert user.username == "debug_user"
        assert user.is_staff
        assert user.is_superuser
        assert user.is_active


@pytest.mark.django_db
def test_production_mode_no_auto_creation():
    backend = AnyUserAuthBackend()
    request = HttpRequest()

    with patch("hope_live.security.backends.settings.DEBUG", False):
        user = backend.authenticate(request, username="prod_user", password="any")

        assert user is None


@pytest.mark.django_db
def test_existing_user_upgrade_in_debug_mode():
    backend = AnyUserAuthBackend()
    request = HttpRequest()

    existing_user = User.objects.create_user(username="existing", email="existing@example.com", password="password123")
    existing_user.is_staff = False
    existing_user.is_superuser = False
    existing_user.save()

    with patch("hope_live.security.backends.settings.DEBUG", True):
        updated_user = backend.authenticate(request, username="existing", password="any")

        assert updated_user is not None
        assert updated_user.username == "existing"
        assert updated_user.is_staff
        assert updated_user.is_superuser


@pytest.mark.django_db
def test_multiple_debug_user_creation():
    backend = AnyUserAuthBackend()
    request = HttpRequest()

    with patch("hope_live.security.backends.settings.DEBUG", True):
        users = []
        for i in range(5):
            user = backend.authenticate(request, username=f"user{i}", password="any")
            users.append(user)

        assert len(users) == 5
        assert len({u.username for u in users}) == 5
        assert all(u.is_staff and u.is_superuser for u in users)
