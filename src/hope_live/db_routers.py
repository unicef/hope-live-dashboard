from typing import Any

from django.apps import apps
from django.conf import settings
from django.db.models import Model


class HopeRouter:
    @staticmethod
    def _is_hope_model(model: type[Model]) -> bool:
        if model._meta.proxy:
            model = model._meta.proxy_for_model
        return model.__module__.startswith("hope_live.models.hope")

    def db_for_read(self, model: type[Model], **hints: Any) -> str | None:
        if self._is_hope_model(model):
            return "hope"
        return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label)

    def db_for_write(self, model: type[Model], **hints: Any) -> str | None:
        if self._is_hope_model(model):
            return None
        return settings.DATABASE_APPS_MAPPING.get(model._meta.app_label)

    def allow_relation(self, obj1: Model, obj2: Model, **hints: Any) -> bool | None:
        is_obj1_hope = self._is_hope_model(obj1.__class__)
        is_obj2_hope = self._is_hope_model(obj2.__class__)

        if is_obj1_hope or is_obj2_hope:
            return is_obj1_hope and is_obj2_hope
        return None

    def allow_migrate(self, db: str, app_label: str, model_name: str | None = None, **hints: Any) -> bool | None:
        if db == "hope":
            return False

        if model_name:
            try:
                model = apps.get_model(app_label, model_name)
                if self._is_hope_model(model):
                    return False
            except LookupError:
                pass  # Model has been removed from code.

        if db == "default" and app_label not in settings.DATABASE_APPS_MAPPING:
            return True

        mapped_db = settings.DATABASE_APPS_MAPPING.get(app_label)
        if mapped_db:
            return bool(mapped_db == db)

        return None
