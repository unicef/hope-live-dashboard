from typing import Any

from django.contrib import admin
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.utils.functional import cached_property
from unfold.admin import ModelAdmin

from hope_live.analysis.models import DailyAggregate


class LargeTablePaginator(Paginator):
    """
    Paginator that avoids the expensive COUNT(*) query.

    It returns a fake large count to allow navigation.
    """

    @cached_property
    def count(self) -> int:
        return 9999999999


@admin.register(DailyAggregate)
class DailyAggregateAdmin(ModelAdmin):
    list_display = (
        "date",
        "country_slug",
        "dimension_type",
        "dimension_value",
        "payment_count",
        "total_usd",
    )
    list_filter = ("date", "country_slug", "dimension_type")
    search_fields = ("country_slug", "dimension_value")
    ordering = ("-date", "country_slug")
    paginator = LargeTablePaginator
    show_full_result_count = False

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False
