import pytest
from django.test import override_settings
from testutils.factories import UserFactory

from hope_live.utils.pipeline import configure_user

pytestmark = [pytest.mark.django_db]


@override_settings(SUPERUSERS=["admin@example.com"])
def test_configure_user_superuser():
    user = UserFactory(username="admin@example.com", is_staff=False, is_superuser=False)
    configure_user(user=user)
    user.refresh_from_db()
    assert user.is_staff
    assert user.is_superuser


@override_settings(SUPERUSERS=["admin@example.com"])
def test_configure_user_regular():
    user = UserFactory(username="user@example.com", is_staff=False, is_superuser=False)
    configure_user(user=user)
    user.refresh_from_db()
    assert not user.is_staff
    assert not user.is_superuser


@override_settings(SUPERUSERS=["admin@example.com"])
def test_configure_user_not_in_superusers():
    user = UserFactory(username="other@example.com", is_staff=False, is_superuser=False)
    configure_user(user=user)
    user.refresh_from_db()
    assert not user.is_staff
    assert not user.is_superuser


def test_configure_user_none():
    assert configure_user(user=None) == {}
