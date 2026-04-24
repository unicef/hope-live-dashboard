from admin_extra_buttons.api import confirm_action
from admin_extra_buttons.decorators import button
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django_celery_boost.admin import CeleryTaskModelAdmin
from kombu.exceptions import OperationalError

from .models import SyncDailyAggregatesJob
from .tasks import clear_daily_aggregates


@admin.register(SyncDailyAggregatesJob)
class SyncDailyAggregatesJobAdmin(CeleryTaskModelAdmin):  # type: ignore[misc]
    list_display = ("id", "description", "task_status", "datetime_created", "datetime_queued", "error_message")
    list_filter = ("local_status",)
    readonly_fields = ("error_message",)

    @button(permission=lambda r, o, handler: handler.model_admin.has_queue_permission("inspect", r, o))  # type: ignore[arg-type]
    def celery_inspect(self, request: HttpRequest, pk: str) -> HttpResponse:
        try:
            return CeleryTaskModelAdmin.celery_inspect(self, request, pk)  # type: ignore[no-any-return]
        except (OperationalError, ConnectionError):
            self.message_user(request, "Celery broker not available.", level=messages.WARNING)
            return HttpResponseRedirect("..")

    @button(  # type: ignore[arg-type]
        permission=lambda request, obj, **kw: request.user.is_superuser,
        html_attrs={"style": "background-color:#DC6C6C;color:white"},
        label="Clear Daily Aggregates",
    )
    def clear_aggregates(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can clear daily aggregates.")

        def _action(request: HttpRequest) -> None:
            clear_daily_aggregates.delay(request.user.id)

        return confirm_action(
            self,
            request,
            _action,
            message="Are you sure you want to delete ALL Aggregate records? This action cannot be undone.",
            success_message="Clear task has been queued successfully.",
        )
