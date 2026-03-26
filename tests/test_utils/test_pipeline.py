from unittest.mock import Mock, patch

import pytest
from django.contrib.auth import get_user_model

from hope_live.utils.pipeline import configure_user

User = get_user_model()


@pytest.mark.django_db
@patch("hope_live.utils.pipeline.settings.SUPERUSERS", ["admin@example.com", "super@example.com"])
def test_configure_user_superuser():
    user = User.objects.create_user(username="admin", email="admin@example.com", password="password123")
    user.is_staff = False
    user.is_superuser = False
    user.save()

    result = configure_user(user)

    user.refresh_from_db()
    assert user.is_staff is True
    assert user.is_superuser is True
    assert result == {}


@pytest.mark.django_db
@patch("hope_live.utils.pipeline.settings.SUPERUSERS", ["admin@example.com"])
def test_configure_user_non_superuser():
    user = User.objects.create_user(username="regular", email="regular@example.com", password="password123")
    user.is_staff = False
    user.is_superuser = False
    user.save()

    result = configure_user(user)

    user.refresh_from_db()
    assert user.is_staff is False
    assert user.is_superuser is False
    assert result == {}


@pytest.mark.django_db
@patch("hope_live.utils.pipeline.settings.SUPERUSERS", ["admin@example.com"])
def test_configure_user_multiple_users():
    users = [
        User.objects.create_user(username="admin", email="admin@example.com", password="password123"),
        User.objects.create_user(username="regular", email="regular@example.com", password="password123"),
        User.objects.create_user(username="super", email="super@example.com", password="password123"),
    ]

    for user in users:
        user.is_staff = False
        user.is_superuser = False
        user.save()

    with patch("hope_live.utils.pipeline.settings.SUPERUSERS", ["admin@example.com", "super@example.com"]):
        for user in users:
            configure_user(user)

    users[0].refresh_from_db()
    users[1].refresh_from_db()
    users[2].refresh_from_db()

    assert users[0].is_staff is True
    assert users[0].is_superuser is True

    assert users[1].is_staff is False
    assert users[1].is_superuser is False

    assert users[2].is_staff is True
    assert users[2].is_superuser is True


@pytest.mark.django_db
@patch("hope_live.utils.pipeline.settings.SUPERUSERS", ["admin@example.com"])
def test_configure_user_no_user():
    result = configure_user(None)
    assert result == {}


@pytest.mark.django_db
@patch("hope_live.utils.pipeline.settings.SUPERUSERS", ["admin@example.com"])
def test_configure_user_already_superuser():
    user = User.objects.create_user(username="admin", email="admin@example.com", password="password123")
    user.is_staff = True
    user.is_superuser = True
    user.save()

    result = configure_user(user)

    user.refresh_from_db()
    assert user.is_staff is True
    assert user.is_superuser is True
    assert result == {}


def test_configure_user_with_kwargs():
    user = Mock()
    user.email = "test@example.com"
    user.is_staff = False
    user.is_superuser = False
    user.save = Mock()

    with patch("hope_live.utils.pipeline.settings.SUPERUSERS", []):
        result = configure_user(user, extra_arg="value", another_arg=123)

    assert result == {}
    user.save.assert_not_called()
