import os
import sys
from pathlib import Path

import pytest
import responses

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))


class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


def pytest_configure(config):
    os.environ["DJANGO_SETTINGS_MODULE"] = "hope_live.config.settings"
    os.environ.setdefault("CONSTANCE_REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("CHANNEL_BROKER", "redis://localhost:6379/0")

    from django.conf import settings

    settings.DATABASE_ROUTERS = []
    settings.MIGRATION_MODULES = DisableMigrations()
    settings.DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda r: False}
    settings.CONSTANCE_REDIS_CONNECTION = os.environ.get("CONSTANCE_REDIS_URL", "redis://localhost:6379/0")

    import django
    from django.apps import apps

    from hope_live.models.hope import HopeModel

    if not apps.ready:
        django.setup()

    # Force managed=True for all HopeModels so tables are created in test DB
    for model in apps.get_models():
        if issubclass(model, HopeModel):
            model._meta.managed = True


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
