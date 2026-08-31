import csv
import io
import json
from typing import Any

import openpyxl
from django.db import models
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import (  # type: ignore[import-untyped]
    generics,
    serializers,
)
from rest_framework.permissions import AllowAny  # type: ignore[import-untyped]
from rest_framework.renderers import JSONRenderer  # type: ignore[import-untyped]
from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]
from rest_framework.views import APIView  # type: ignore[import-untyped]

from ..models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
    RiskAggregate,
    TimeGrain,
)
from ..serializers import (
    CompletionAggregateSerializer,
    DemographicAggregateSerializer,
    FinancialAggregateSerializer,
    GrievanceAggregateSerializer,
    RiskAggregateSerializer,
)

RISK_EXPORT_FIELDS = RiskAggregateSerializer.Meta.fields


def _apply_common_filters(queryset: models.QuerySet, params: Any, dash_type: str | None) -> models.QuerySet:
    time_grain = params.get("time_grain")
    if not time_grain or time_grain not in TimeGrain.values:
        time_grain = TimeGrain.MONTHLY if dash_type == "demographic" else TimeGrain.DAILY
    queryset = queryset.filter(time_grain=time_grain)

    year = params.get("year")
    if year:
        queryset = queryset.filter(date__year=int(year))

    dimension_type = params.get("dimension_type")
    if dimension_type:
        queryset = queryset.filter(dimension_type=dimension_type)

    country_slug = params.get("country_slug")
    if country_slug:
        queryset = queryset.filter(country_slug=country_slug)

    date_from = params.get("date_from")
    date_to = params.get("date_to")
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    return queryset


def _apply_risk_filters(queryset: models.QuerySet, params: Any) -> models.QuerySet:
    module = params.get("module")
    if module:
        queryset = queryset.filter(module=module)

    severity = params.get("severity")
    if severity:
        queryset = queryset.filter(severity=severity)

    risk_code = params.get("risk_code")
    if risk_code:
        queryset = queryset.filter(risk_code=risk_code)

    return queryset


@method_decorator(cache_page(60 * 60 * 6), name="dispatch")
class AggregateListView(generics.ListAPIView):  # type: ignore[misc]
    """API endpoint for listing Aggregate records with filtering."""

    permission_classes = [AllowAny]

    def get_serializer_class(self) -> type[serializers.ModelSerializer]:
        dash_type = self.request.query_params.get("dashboard")
        if dash_type == "demographic":
            return DemographicAggregateSerializer
        if dash_type == "completion":
            return CompletionAggregateSerializer
        if dash_type == "grievance":
            return GrievanceAggregateSerializer
        if dash_type == "risk":
            return RiskAggregateSerializer
        return FinancialAggregateSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="year",
                description="Filter by year (YYYY)",
                required=False,
                type=int,
                examples=[OpenApiExample("2024", value=2024)],
            ),
            OpenApiParameter(
                name="dimension_type",
                description="Filter by dimension type (sector, program, status, etc.)",
                required=False,
                type=str,
                examples=[
                    OpenApiExample("Sector", value="sector"),
                    OpenApiExample("Program", value="program"),
                    OpenApiExample("Status", value="status"),
                ],
            ),
            OpenApiParameter(
                name="country_slug",
                description="Filter by country slug",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="date_from",
                description="Filter by start date (YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="date_to",
                description="Filter by end date (YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="module",
                description="Filter by risk module (risk dashboard only)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="severity",
                description="Filter by risk severity (risk dashboard only)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="risk_code",
                description="Filter by risk code (risk dashboard only)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="dashboard",
                description="Filter by dashboard type (financial, demographic, completion, grievance, risk)",
                required=False,
                type=str,
                examples=[
                    OpenApiExample("Financial", value="financial"),
                    OpenApiExample("Demographic", value="demographic"),
                    OpenApiExample("Completion", value="completion"),
                    OpenApiExample("Risk", value="risk"),
                ],
            ),
        ],
        description="List Aggregate records with optional filtering",
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> models.QuerySet:  # type: ignore[type-arg]
        dash_type = self.request.query_params.get("dashboard")

        queryset: models.QuerySet[Any]
        if dash_type == "demographic":
            queryset = DemographicAggregate.objects.all()
        elif dash_type == "completion":
            queryset = CompletionAggregate.objects.all()
        elif dash_type == "grievance":
            queryset = GrievanceAggregate.objects.all()
        elif dash_type == "risk":
            queryset = RiskAggregate.objects.all()
        else:
            queryset = FinancialAggregate.objects.exclude(dimension_type="currency")

        queryset = _apply_common_filters(queryset, self.request.query_params, dash_type)

        if dash_type == "risk":
            queryset = _apply_risk_filters(queryset, self.request.query_params)

        return queryset


class ExportReportView(APIView):  # type: ignore[misc]
    """Export Risk Aggregate records in multiple formats (csv, json, xlsx)."""

    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def perform_content_negotiation(self, request: Request, force: bool = False) -> tuple[Any, str]:
        # The `format` query param is used to select the export format, so bypass
        # DRF's default renderer-format override (which would 404 on csv/xlsx).
        renderer = self.get_renderers()[0]
        return renderer, renderer.media_type

    def get(self, request: Request, *args: object, **kwargs: object) -> HttpResponse:
        export_format = (request.query_params.get("format") or "json").lower()

        queryset = RiskAggregate.objects.all()
        queryset = _apply_common_filters(queryset, request.query_params, "risk")
        queryset = _apply_risk_filters(queryset, request.query_params)
        queryset = queryset.filter(is_visible_on_dashboard=True)

        rows = list(RiskAggregateSerializer(queryset, many=True).data)

        if export_format == "csv":
            return self._csv_response(rows)
        if export_format == "xlsx":
            return self._xlsx_response(rows)
        return self._json_response(rows)

    @staticmethod
    def _content_disposition(filename: str) -> str:
        return f'attachment; filename="{filename}"'

    def _json_response(self, rows: list[dict[str, Any]]) -> HttpResponse:
        response = HttpResponse(json.dumps(rows), content_type="application/json")
        response["Content-Disposition"] = self._content_disposition("risk_export.json")
        return response

    def _csv_response(self, rows: list[dict[str, Any]]) -> HttpResponse:
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=RISK_EXPORT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = self._content_disposition("risk_export.csv")
        return response

    def _xlsx_response(self, rows: list[dict[str, Any]]) -> HttpResponse:
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Risk"
        worksheet.append(list(RISK_EXPORT_FIELDS))
        for row in rows:
            worksheet.append([row.get(field) for field in RISK_EXPORT_FIELDS])

        buffer = io.BytesIO()
        workbook.save(buffer)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = self._content_disposition("risk_export.xlsx")
        return response
