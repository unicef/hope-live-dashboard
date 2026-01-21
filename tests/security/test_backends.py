from unittest.mock import MagicMock

from django.test import override_settings

from hope_live.security.backends import AnyUserAuthBackend


@override_settings(DEBUG=True)
def test_authenticate_debug_true(db):
    backend = AnyUserAuthBackend()
    request = MagicMock()
    user = backend.authenticate(request, username="testuser")
    assert user is not None
    assert user.username == "testuser"
    assert user.is_staff
    assert user.is_superuser


@override_settings(DEBUG=False)
def test_authenticate_debug_false(db):
    backend = AnyUserAuthBackend()
    request = MagicMock()
    user = backend.authenticate(request, username="testuser")
    assert user is None
