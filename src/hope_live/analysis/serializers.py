from rest_framework import serializers  # type: ignore[import-untyped]

from .models import CompletionAggregate, DemographicAggregate, FinancialAggregate, GrievanceAggregate, RiskAggregate


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
            "total_households",
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


class RiskAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = RiskAggregate
        fields = [
            "date",
            "time_grain",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "module",
            "risk_code",
            "risk_name",
            "description",
            "issue_count",
            "percentage",
            "unit_label",
            "severity",
            "trend",
            "threshold_info",
            "is_visible_on_dashboard",
        ]
