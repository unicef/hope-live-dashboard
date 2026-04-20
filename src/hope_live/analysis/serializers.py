from rest_framework import serializers  # type: ignore[import-untyped]

from .models import DailyAggregate


class DailyAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = DailyAggregate
        fields = [
            "date",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "total_usd",
            "total_qty",
            "payment_count",
            "total_beneficiaries",
            "total_children",
            "total_pwd",
        ]


class FinancialAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = DailyAggregate
        fields = [
            "date",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "total_usd",
            "total_qty",
            "payment_count",
        ]


class DemographicAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = DailyAggregate
        fields = [
            "date",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "total_beneficiaries",
            "total_children",
            "total_pwd",
        ]


class CompletionAggregateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = DailyAggregate
        fields = [
            "date",
            "country_slug",
            "dimension_type",
            "dimension_value",
            "payment_count",
            "total_usd",
        ]
