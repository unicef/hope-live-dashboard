from admin_extra_buttons.api import confirm_action
from admin_extra_buttons.decorators import button
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django_celery_boost.admin import CeleryTaskModelAdmin
from kombu.exceptions import OperationalError

from .models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
    RiskAggregate,
    SyncDailyAggregatesJob,
)
from .tasks import clear_daily_aggregates


@admin.register(SyncDailyAggregatesJob)
class SyncDailyAggregatesJobAdmin(CeleryTaskModelAdmin):  # type: ignore[misc]
    list_display = ("id", "description", "task_status", "datetime_created", "datetime_queued", "error_message")
    list_filter = ("local_status",)
    readonly_fields = ("error_message",)

    @button(permission=lambda r, o, handler: handler.model_admin.has_queue_permission("inspect", r, o))
    def celery_inspect(self, request: HttpRequest, pk: str) -> HttpResponse:
        try:
            return CeleryTaskModelAdmin.celery_inspect(self, request, pk)  # type: ignore[no-any-return]
        except (OperationalError, ConnectionError):
            self.message_user(request, "Celery broker not available.", level=messages.WARNING)
            return HttpResponseRedirect("..")

    @button(
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


class ReadOnlyDeletableAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    date_hierarchy = "date"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return False


@admin.register(FinancialAggregate)
class FinancialAggregateAdmin(ReadOnlyDeletableAdmin):
    list_display = (
        "date",
        "time_grain",
        "country_slug",
        "dimension_type",
        "dimension_value",
        "total_usd",
        "total_qty",
        "payment_count",
    )
    list_filter = ("time_grain", "country_slug", "dimension_type", "date")
    search_fields = ("country_slug", "dimension_type", "dimension_value")


@admin.register(DemographicAggregate)
class DemographicAggregateAdmin(ReadOnlyDeletableAdmin):
    list_display = (
        "date",
        "time_grain",
        "country_slug",
        "dimension_type",
        "dimension_value",
        "total_beneficiaries",
        "total_children",
        "total_pwd",
    )
    list_filter = ("time_grain", "country_slug", "dimension_type", "date")
    search_fields = ("country_slug", "dimension_type", "dimension_value")


@admin.register(CompletionAggregate)
class CompletionAggregateAdmin(ReadOnlyDeletableAdmin):
    list_display = (
        "date",
        "time_grain",
        "country_slug",
        "dimension_type",
        "dimension_value",
        "payment_count",
        "total_usd",
    )
    list_filter = ("time_grain", "country_slug", "dimension_type", "date")
    search_fields = ("country_slug", "dimension_type", "dimension_value")


@admin.register(GrievanceAggregate)
class GrievanceAggregateAdmin(ReadOnlyDeletableAdmin):
    list_display = (
        "date",
        "time_grain",
        "country_slug",
        "dimension_type",
        "dimension_value",
        "ticket_count",
    )
    list_filter = ("time_grain", "country_slug", "dimension_type", "date")
    search_fields = ("country_slug", "dimension_type", "dimension_value")


@admin.register(RiskAggregate)
class RiskAggregateAdmin(ReadOnlyDeletableAdmin):
    list_display = (
        "date",
        "time_grain",
        "country_slug",
        "module",
        "risk_name",
        "issue_count",
        "percentage",
        "severity",
        "trend",
    )
    list_filter = ("time_grain", "severity", "module", "country_slug", "date")
    search_fields = ("country_slug", "module", "risk_code", "risk_name")
