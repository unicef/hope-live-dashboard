from typing import Any

from django.core.cache import cache


class DashboardCache:
    VERSION_KEY = "dashboard:version"
    TTL = 60 * 60 * 24

    @classmethod
    def _get_version(cls) -> int:
        return cache.get_or_set(cls.VERSION_KEY, 1, timeout=None)

    @classmethod
    def invalidate(cls) -> None:
        try:
            cache.incr(cls.VERSION_KEY)
        except ValueError:
            cache.set(cls.VERSION_KEY, 1, timeout=None)

    @classmethod
    def get_key(cls, prefix: str, **kwargs: Any) -> str:
        version = cls._get_version()
        params = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
        return f"dashboard:v{version}:{prefix}:{params}"
