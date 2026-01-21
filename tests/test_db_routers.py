from unittest.mock import Mock

import pytest

from hope_live.db_routers import HopeRouter
from hope_live.models import BusinessArea, User


class TestHopeRouter:
    def test_db_for_read_hope_model(self):
        router = HopeRouter()
        assert router.db_for_read(BusinessArea) == "hope"

    def test_db_for_read_other_model(self):
        router = HopeRouter()
        assert router.db_for_read(User) is None

    def test_db_for_write(self):
        router = HopeRouter()
        assert router.db_for_write(BusinessArea) is None
        assert router.db_for_write(User) is None

    def test_allow_relation_both_hope(self):
        router = HopeRouter()
        obj1 = Mock()
        obj1._meta.app_label = "hope_live"
        obj1.__module__ = "hope_live.models.hope"
        obj2 = Mock()
        obj2._meta.app_label = "hope_live"
        obj2.__module__ = "hope_live.models.hope"
        assert router.allow_relation(obj1, obj2) is True

    def test_allow_relation_mixed(self):
        router = HopeRouter()
        obj1 = Mock()
        obj1.__module__ = "hope_live.models.hope"
        obj2 = Mock()
        obj2.__module__ = "django.contrib.auth.models"
        assert router.allow_relation(obj1, obj2) is None

    @pytest.mark.parametrize(
        ("model_name", "expected"),
        [
            ("businessarea", False),
            ("hopeprogram", False),
            ("payment", False),
            ("deliverymechanism", False),
            ("financialserviceprovider", False),
            ("household", False),
            ("paymentplan", False),
            ("paymentverification", False),
            ("user", None),
        ],
    )
    def test_allow_migrate(self, model_name, expected):
        router = HopeRouter()
        assert router.allow_migrate("default", "hope_live", model_name=model_name) is expected

    def test_allow_migrate_other_app(self):
        router = HopeRouter()
        assert router.allow_migrate("default", "auth", model_name="user") is None
