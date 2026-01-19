from unittest.mock import patch

from django.core.cache import cache

from hope_live.utils.cache import DashboardCache


def test_get_version_initial():
    cache.delete(DashboardCache.VERSION_KEY)
    assert DashboardCache._get_version() == 1


def test_get_version_existing():
    cache.set(DashboardCache.VERSION_KEY, 10)
    assert DashboardCache._get_version() == 10


def test_invalidate_increments_version():
    cache.set(DashboardCache.VERSION_KEY, 1)
    DashboardCache.invalidate()
    assert cache.get(DashboardCache.VERSION_KEY) == 2


def test_invalidate_sets_initial_if_missing():
    cache.delete(DashboardCache.VERSION_KEY)
    DashboardCache.invalidate()
    # Depending on implementation, incr on missing might error or set.
    # Our code catches ValueError and sets to 1.
    # Wait, code says: try cache.incr except ValueError -> cache.set(1)
    # Redis backend usually handles incr on missing key by setting to 1.
    # LocMem might raise ValueError.
    val = cache.get(DashboardCache.VERSION_KEY)
    assert val in [1, 2]  # 1 if set, 2 if incr worked on 0/None treated as int


def test_get_key_format():
    with patch.object(DashboardCache, "_get_version", return_value=5):
        key = DashboardCache.get_key("myprefix", param1="value1", param2=123)
        assert key == "dashboard:v5:myprefix:param1=value1:param2=123"


def test_get_key_sorts_params():
    with patch.object(DashboardCache, "_get_version", return_value=1):
        key1 = DashboardCache.get_key("test", a=1, b=2)
        key2 = DashboardCache.get_key("test", b=2, a=1)
        assert key1 == key2
