from unittest.mock import MagicMock

from django.test import override_settings

from hope_live.apps import on_login


@override_settings(SUPERUSERS=["admin@example.com"])
def test_on_login_superuser():
    user = MagicMock()
    user.email = "admin@example.com"
    user.username = "admin"

    on_login(sender=MagicMock(), user=user)

    assert user.is_superuser
    assert user.is_staff
    user.save.assert_called_once()


@override_settings(SUPERUSERS=["admin@example.com"])
def test_on_login_regular():
    user = MagicMock()
    user.email = "user@example.com"
    user.username = "user"
    user.is_superuser = False
    user.is_staff = False

    on_login(sender=MagicMock(), user=user)

    assert not user.is_superuser
    assert not user.is_staff
    user.save.assert_not_called()
