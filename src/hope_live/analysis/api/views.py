from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import generics, serializers  # type: ignore[import-untyped]
from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]

from ..models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
)
from ..serializers import (
    CompletionAggregateSerializer,
    DemographicAggregateSerializer,
    FinancialAggregateSerializer,
    GrievanceAggregateSerializer,
)


@method_decorator(cache_page(60 * 60 * 6), name="dispatch")
class AggregateListView(generics.ListAPIView):  # type: ignore[misc]
    """API endpoint for listing Aggregate records with filtering."""

    def get_serializer_class(self) -> type[serializers.ModelSerializer]:
        dash_type = self.request.query_params.get("dashboard")
        if dash_type == "demographic":
            return DemographicAggregateSerializer
        if dash_type == "completion":
            return CompletionAggregateSerializer
        if dash_type == "grievance":
            return GrievanceAggregateSerializer
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
        description="List Aggregate records with optional filtering",
    )
    def get(self, request: Request, *args: object, **kwargs: object) -> Response:
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> models.QuerySet:  # type: ignore[type-arg]
        dash_type = self.request.query_params.get("dashboard")
        if dash_type == "demographic":
            queryset = DemographicAggregate.objects.all()
        elif dash_type == "completion":
            queryset = CompletionAggregate.objects.all()
        elif dash_type == "grievance":
            queryset = GrievanceAggregate.objects.all()
        else:
            queryset = FinancialAggregate.objects.exclude(dimension_type="currency")

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

        return queryset  # type: ignore[no-any-return]
