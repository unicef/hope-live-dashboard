from datetime import date, timedelta

import pytest
from django.db import models
from django.db.utils import IntegrityError

from hope_live.analysis.models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
    TimeGrain,
)


# --------------------- FinancialAggregate ---------------------
@pytest.mark.django_db
def test_financial_aggregate_data_integrity():
    aggregate = FinancialAggregate.objects.create(
        date=date(2024, 1, 15),
        time_grain=TimeGrain.DAILY,
        country_slug="afghanistan",
        dimension_type="sector",
        dimension_value="Health",
        total_usd=12500.75,
        total_qty=250.5,
        payment_count=45,
    )

    assert aggregate.date == date(2024, 1, 15)
    assert aggregate.country_slug == "afghanistan"
    assert aggregate.dimension_type == "sector"
    assert aggregate.dimension_value == "Health"
    assert aggregate.total_usd == 12500.75
    assert aggregate.total_qty == 250.5
    assert aggregate.payment_count == 45


@pytest.mark.django_db
def test_financial_aggregate_composite_unique():
    FinancialAggregate.objects.create(
        date=date(2024, 1, 1),
        time_grain=TimeGrain.DAILY,
        country_slug="afghanistan",
        dimension_type="sector",
        dimension_value="Health",
    )

    with pytest.raises(IntegrityError):
        FinancialAggregate.objects.create(
            date=date(2024, 1, 1),
            time_grain=TimeGrain.DAILY,
            country_slug="afghanistan",
            dimension_type="sector",
            dimension_value="Health",
        )


@pytest.mark.django_db
def test_financial_aggregate_bulk_create():
    aggregates = [
        FinancialAggregate(
            date=date(2024, 1, 1) + timedelta(days=i),
            time_grain=TimeGrain.DAILY,
            country_slug="afghanistan",
            dimension_type="sector",
            dimension_value=f"Sector{i % 3}",
            total_usd=i * 1000.0,
        )
        for i in range(10)
    ]

    FinancialAggregate.objects.bulk_create(aggregates)

    total_usd = sum(agg.total_usd for agg in FinancialAggregate.objects.all())
    assert FinancialAggregate.objects.count() == 10
    assert total_usd == 45000.0


@pytest.mark.django_db
def test_financial_aggregate_filtering():
    test_data = [
        ("afghanistan", "Health", 10000),
        ("afghanistan", "Education", 8000),
        ("syria", "Health", 12000),
        ("syria", "Education", 9000),
    ]

    for i, (country, sector, usd) in enumerate(test_data):
        FinancialAggregate.objects.create(
            date=date(2024, 1, 1) + timedelta(days=i),
            time_grain=TimeGrain.DAILY,
            country_slug=country,
            dimension_type="sector",
            dimension_value=sector,
            total_usd=usd,
        )

    afghanistan_total = FinancialAggregate.objects.filter(country_slug="afghanistan").aggregate(
        total=models.Sum("total_usd")
    )["total_usd"]
    health_total = FinancialAggregate.objects.filter(dimension_value="Health").aggregate(total=models.Sum("total_usd"))[
        "total_usd"
    ]

    assert afghanistan_total == 18000
    assert health_total == 22000
    assert FinancialAggregate.objects.filter(country_slug="syria").count() == 2


# --------------------- DemographicAggregate ---------------------
@pytest.mark.django_db
def test_demographic_aggregate_create():
    agg = DemographicAggregate.objects.create(
        date=date(2024, 1, 15),
        time_grain=TimeGrain.DAILY,
        country_slug="afghanistan",
        dimension_type="sector",
        dimension_value="Education",
        total_beneficiaries=500,
        total_children=200,
        total_pwd=25,
    )
    assert agg.total_beneficiaries == 500
    assert agg.total_children == 200
    assert agg.total_pwd == 25


# --------------------- CompletionAggregate ---------------------
@pytest.mark.django_db
def test_completion_aggregate_create():
    agg = CompletionAggregate.objects.create(
        date=date(2024, 1, 15),
        time_grain=TimeGrain.DAILY,
        country_slug="afghanistan",
        dimension_type="sector",
        dimension_value="Health",
        payment_count=10,
        total_usd=50000.00,
    )
    assert agg.payment_count == 10
    assert agg.total_usd == 50000.00


# --------------------- GrievanceAggregate ---------------------
@pytest.mark.django_db
def test_grievance_aggregate_create():
    agg = GrievanceAggregate.objects.create(
        date=date(2024, 1, 15),
        time_grain=TimeGrain.DAILY,
        country_slug="afghanistan",
        dimension_type="sector",
        dimension_value="Health",
        ticket_count=25,
    )
    assert agg.ticket_count == 25
