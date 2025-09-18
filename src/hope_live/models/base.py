from typing import Any

from django.db import models
from django.urls import reverse


class BaseQuerySet(models.QuerySet["models.Model"]):
    def get(self, *args: Any, **kwargs: Any) -> "models.Model":
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist as e:  # type: ignore[attr-defined]
            raise self.model.DoesNotExist(  # type: ignore[attr-defined]
                "%s matching query does not exist. Using %s %s", self.model._meta.object_name, args, kwargs
            ) from e


class BaseManager(models.Manager["models.Model"]):
    _queryset_class = BaseQuerySet


class BaseModel(models.Model):
    last_modified = models.DateTimeField(auto_now=True, editable=False)

    objects = BaseManager()

    class Meta:
        abstract = True

    def get_change_url(self, namespace: str = "workspace") -> str:
        return reverse(f"{namespace}:{self._meta.app_label}_{self._meta.model_name}_change", args=[self.pk])
