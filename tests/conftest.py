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


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Force managed=True for HopeModels to ensure tables are created in tests."""
    import django
    from django.apps import apps

    from hope_live.models.hope import HopeModel

    if not apps.ready:
        django.setup()

    for model in apps.get_models():
        if issubclass(model, HopeModel):
            model._meta.managed = True
