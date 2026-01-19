from typing import Any


class HopeRouter:
    def db_for_read(self, model: Any, **hints: Any) -> str | None:
        if model.__module__.startswith("hope_live.models.hope"):
            return "hope"
        return None

    def db_for_write(self, model: Any, **hints: Any) -> None:
        return None

    def allow_relation(self, obj1: Any, obj2: Any, **hints: Any) -> bool | None:
        if obj1.__module__.startswith("hope_live.models.hope") and obj2.__module__.startswith("hope_live.models.hope"):
            return True
        return None

    def allow_migrate(self, db: str, app_label: str, model_name: str | None = None, **hints: Any) -> bool | None:
        if app_label == "hope_live" and model_name in [
            "businessarea",
            "hopeprogram",
            "payment",
            "deliverymechanism",
            "financialserviceprovider",
            "household",
            "paymentplan",
            "paymentverification",
        ]:
            return False
        return None
