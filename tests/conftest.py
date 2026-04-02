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


def pytest_configure(config):
    os.environ["DJANGO_SETTINGS_MODULE"] = "hope_live.config.settings"
    # Setup Django
    import django

    django.setup()

    # Register custom marks to avoid warnings
    config.addinivalue_line("markers", "admin: mark test as admin test")
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "django_db: mark test as requiring django database")
    config.addinivalue_line("markers", "skip_models: skip specific models in tests")
    config.addinivalue_line("markers", "skip_buttons: skip specific buttons in tests")
    config.addinivalue_line("markers", "asyncio: mark test as async test")


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


@pytest.fixture(autouse=True)
def cleanup_flags(db):
    from django.db import DatabaseError, transaction
    from flags.models import FlagState

    yield

    # Try to cleanup, but if it fails (e.g., due to broken transaction), just skip it
    # The test database will be destroyed after the test run anyway
    with contextlib.suppress(DatabaseError, transaction.TransactionManagementError):
        FlagState.objects.all().delete()
