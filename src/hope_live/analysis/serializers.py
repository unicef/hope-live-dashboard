from typing import Any

from rest_framework import serializers


class DashboardFilterSerializer(serializers.Serializer[Any]):
    DIMENSION_CHOICES = [
        ("total", "Total"),
        ("sector", "Sector"),
        ("program", "Program"),
        ("fsp", "Financial Service Provider"),
        ("region", "Region"),
        ("status", "Status"),
        ("delivery_mechanism", "Delivery Mechanism"),
    ]

    CHART_TYPE_CHOICES = [
        ("timeline", "Timeline (Daily)"),
        ("summary", "Summary (Total)"),
    ]

    dimension = serializers.ChoiceField(choices=DIMENSION_CHOICES, required=True)
    chart_type = serializers.ChoiceField(choices=CHART_TYPE_CHOICES, default="summary")
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    country_office = serializers.CharField(required=False, allow_blank=True)


class DashboardOutputSerializer(serializers.Serializer[Any]):
    label = serializers.CharField(source="dimension_value")
    value = serializers.DecimalField(max_digits=20, decimal_places=2)
    count = serializers.IntegerField()
    beneficiaries = serializers.IntegerField(source="total_beneficiaries", required=False)
    children = serializers.IntegerField(source="total_children", required=False)
    pwd = serializers.IntegerField(source="total_pwd", required=False)
    date = serializers.DateField(required=False, allow_null=True)


class DashboardTotalsSerializer(serializers.Serializer[Any]):
    total_usd = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_count = serializers.IntegerField()
    beneficiaries = serializers.IntegerField()
    children = serializers.IntegerField()
    pwd = serializers.IntegerField()
    data_source = serializers.CharField()
    last_updated = serializers.CharField()
