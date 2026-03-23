from admin_extra_buttons.decorators import button
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django_celery_boost.admin import CeleryTaskModelAdmin
from kombu.exceptions import OperationalError

from .models import SyncDailyAggregatesJob


@admin.register(SyncDailyAggregatesJob)
class SyncDailyAggregatesJobAdmin(CeleryTaskModelAdmin):  # type: ignore[misc]
    list_display = ("id", "description", "task_status", "datetime_created", "datetime_queued", "error_message")
    list_filter = ("local_status",)
    readonly_fields = ("error_message",)

    @button(permission=lambda r, o, handler: handler.model_admin.has_queue_permission("inspect", r, o))
    def celery_inspect(self, request: HttpRequest, pk: str) -> HttpResponse:
        try:
            return super().celery_inspect(request, pk)  # type: ignore[no-any-return]
        except (OperationalError, ConnectionError):
            self.message_user(request, "Celery broker not available.", level=messages.WARNING)
            return HttpResponseRedirect("..")
