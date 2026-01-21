import os
import sys
from pathlib import Path

import pytest
import responses

here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here / "extras"))


def pytest_configure(config):
    os.environ["DJANGO_SETTINGS_MODULE"] = "hope_live.config.settings"

    from django.conf import settings

    # Disable routers to allow migrations on all DBs
    settings.DATABASE_ROUTERS = []

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
