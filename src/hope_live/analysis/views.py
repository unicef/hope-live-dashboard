from typing import Any

from django.db.models import CharField, Sum, Value
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hope_live.analysis.models import DailyAggregate
from hope_live.analysis.serializers import (
    DashboardFilterSerializer,
    DashboardOutputSerializer,
    DashboardTotalsSerializer,
)


class DashboardStatsAPIView(APIView):
    """High-performance API for dashboard analytics.

    Reads from the pre-calculated DailyAggregate table.
    """

    @method_decorator(cache_page(60 * 60))
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        input_serializer = DashboardFilterSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)
        params = input_serializer.validated_data

        dimension = params["dimension"]
        chart_type = params["chart_type"]
        country_office = params.get("country_office")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        queryset = DailyAggregate.objects.all()

        if country_office:
            queryset = queryset.filter(country_slug=country_office)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        if dimension == "total":
            queryset = queryset.filter(dimension_type="sector")

            if chart_type == "timeline":
                data = (
                    queryset.values("date")
                    .annotate(
                        dimension_value=Value("Total", output_field=CharField()),
                        value=Sum("total_usd"),
                        count=Sum("payment_count"),
                    )
                    .order_by("date")
                )
            else:
                total_value = queryset.aggregate(total=Sum("total_usd"))["total"] or 0
                total_count = queryset.aggregate(total_count=Sum("payment_count"))["total_count"] or 0
                data = [{"dimension_value": "Total", "value": total_value, "count": total_count, "date": None}]
        else:
            queryset = queryset.filter(dimension_type=dimension)

            if chart_type == "timeline":
                data = (
                    queryset.values("date", "dimension_value")
                    .annotate(value=Sum("total_usd"), count=Sum("payment_count"))
                    .order_by("date", "dimension_value")
                )
            else:
                data = (
                    queryset.values("dimension_value")
                    .annotate(
                        value=Sum("total_usd"),
                        count=Sum("payment_count"),
                        beneficiaries=Sum("total_beneficiaries"),
                        children=Sum("total_children"),
                        pwd=Sum("total_pwd"),
                    )
                    .order_by("-value")
                )

        output_serializer = DashboardOutputSerializer(data, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class DashboardTotalsAPIView(APIView):
    """Real-time totals API.

    Optimized to read from DailyAggregate instead of raw Payment table for performance.
    """

    @method_decorator(cache_page(60 * 5))
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = DailyAggregate.objects.filter(dimension_type="sector")

        aggregates = queryset.aggregate(
            total_usd=Sum("total_usd"),
            total_count=Sum("payment_count"),
            beneficiaries=Sum("total_beneficiaries"),
            children=Sum("total_children"),
            pwd=Sum("total_pwd"),
        )

        data = {
            "total_usd": aggregates["total_usd"] or 0,
            "total_count": aggregates["total_count"] or 0,
            "beneficiaries": aggregates["beneficiaries"] or 0,
            "children": aggregates["children"] or 0,
            "pwd": aggregates["pwd"] or 0,
            "data_source": "aggregated",
            "last_updated": "Daily",
        }

        serializer = DashboardTotalsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
