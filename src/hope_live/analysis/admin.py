from typing import Any

from admin_extra_buttons.decorators import button
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django_celery_boost.admin import CeleryTaskModelAdmin
from kombu.exceptions import OperationalError

from .models import SyncDailyAggregatesJob


@admin.register(SyncDailyAggregatesJob)
class SyncDailyAggregatesJobAdmin(CeleryTaskModelAdmin):
    list_display = ("id", "description", "task_status", "datetime_created", "datetime_queued", "error_message")
    list_filter = ("local_status",)
    readonly_fields = ("error_message",)

    @button(permission=lambda r, o, handler: handler.model_admin.has_queue_permission("inspect", r, o))
    def celery_inspect(self, request: Any, pk: str) -> Any:
        try:
            return super().celery_inspect.func(self, request, pk)
        except (OperationalError, ConnectionError):
            self.message_user(request, "Celery broker not available.", level=messages.WARNING)
            return HttpResponseRedirect("..")
