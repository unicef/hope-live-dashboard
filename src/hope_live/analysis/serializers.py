from rest_framework import serializers  # type: ignore[import-untyped]

from .models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
)


class FinancialAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = FinancialAggregate
        fields = [
            "date",
            "time_grain",  # <-- add this line
            "country_slug",
            "dimension_type",
            "dimension_value",
            "total_usd",
            "total_qty",
            "payment_count",
        ]


class DemographicAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = DemographicAggregate
        fields = [
            "date",
            "time_grain",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "total_beneficiaries",
            "total_children",
            "total_pwd",
        ]


class CompletionAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = CompletionAggregate
        fields = [
            "date",
            "time_grain",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "payment_count",
            "total_usd",
        ]


class GrievanceAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = GrievanceAggregate
        fields = [
            "date",
            "time_grain",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "ticket_count",
        ]
