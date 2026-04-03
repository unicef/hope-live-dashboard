from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import generics, serializers
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import DailyAggregate
from ..serializers import (
    CompletionAggregateSerializer,
    DailyAggregateSerializer,
    DemographicAggregateSerializer,
    FinancialAggregateSerializer,
)


@method_decorator(cache_page(60 * 60 * 24), name="dispatch")
class DailyAggregateListView(generics.ListAPIView):
    """API endpoint for listing DailyAggregate records with filtering."""

    queryset = DailyAggregate.objects.all()

    def get_serializer_class(self) -> type[serializers.ModelSerializer]:
        dash_type = self.request.query_params.get("dashboard")
        if dash_type == "financial":
            return FinancialAggregateSerializer
        if dash_type == "demographic":
            return DemographicAggregateSerializer
        if dash_type == "completion":
            return CompletionAggregateSerializer
        return DailyAggregateSerializer

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
                name="dashboard",
                description="Filter by dashboard type (financial, demographic, completion)",
                required=False,
                type=str,
                examples=[
                    OpenApiExample("Financial", value="financial"),
                    OpenApiExample("Demographic", value="demographic"),
                    OpenApiExample("Completion", value="completion"),
                ],
            ),
        ],
        description="List DailyAggregate records with optional filtering",
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> models.QuerySet[DailyAggregate]:
        queryset = super().get_queryset()

        year = self.request.query_params.get("year")
        if year:
            queryset = queryset.filter(date__year=int(year))

        dimension_type = self.request.query_params.get("dimension_type")
        if dimension_type:
            queryset = queryset.filter(dimension_type=dimension_type)

        country_slug = self.request.query_params.get("country_slug")
        if country_slug:
            queryset = queryset.filter(country_slug=country_slug)

        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset
