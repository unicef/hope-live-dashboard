from datetime import date, timedelta

import pytest
from django.db.utils import IntegrityError

from hope_live.analysis.models import DailyAggregate


@pytest.mark.django_db
def test_daily_aggregate_data_integrity():
    aggregate = DailyAggregate.objects.create(
        date=date(2024, 1, 15),
        country_slug="afghanistan",
        dimension_type="sector",
        dimension_value="Health",
        total_usd=12500.75,
        total_qty=250.5,
        payment_count=45,
        total_beneficiaries=500,
        total_children=200,
        total_pwd=25,
    )

    assert aggregate.date == date(2024, 1, 15)
    assert aggregate.country_slug == "afghanistan"
    assert aggregate.dimension_type == "sector"
    assert aggregate.dimension_value == "Health"
    assert aggregate.total_usd == 12500.75
    assert aggregate.total_beneficiaries == 500


@pytest.mark.django_db
def test_daily_aggregate_composite_unique_constraint():
    DailyAggregate.objects.create(
        date=date(2024, 1, 1), country_slug="afghanistan", dimension_type="sector", dimension_value="Health"
    )

    with pytest.raises(IntegrityError):
        DailyAggregate.objects.create(
            date=date(2024, 1, 1), country_slug="afghanistan", dimension_type="sector", dimension_value="Health"
        )


@pytest.mark.django_db
def test_bulk_daily_aggregate_operations():
    aggregates = [
        DailyAggregate(
            date=date(2024, 1, 1) + timedelta(days=i),
            country_slug="afghanistan",
            dimension_type="sector",
            dimension_value=f"Sector{i % 3}",
            total_usd=i * 1000.0,
            total_beneficiaries=i * 50,
        )
        for i in range(10)
    ]

    DailyAggregate.objects.bulk_create(aggregates)

    total_usd = sum(agg.total_usd for agg in DailyAggregate.objects.all())
    total_beneficiaries = sum(agg.total_beneficiaries for agg in DailyAggregate.objects.all())

    assert DailyAggregate.objects.count() == 10
    assert total_usd == 45000.0
    assert total_beneficiaries == 2250


@pytest.mark.django_db
def test_daily_aggregate_filtering_and_aggregation():
    test_data = [
        ("afghanistan", "Health", 10000, 200),
        ("afghanistan", "Education", 8000, 150),
        ("syria", "Health", 12000, 250),
        ("syria", "Education", 9000, 180),
    ]

    for i, (country, sector, usd, beneficiaries) in enumerate(test_data):
        DailyAggregate.objects.create(
            date=date(2024, 1, 1) + timedelta(days=i),
            country_slug=country,
            dimension_type="sector",
            dimension_value=sector,
            total_usd=usd,
            total_beneficiaries=beneficiaries,
        )

    afghanistan_total = sum(agg.total_usd for agg in DailyAggregate.objects.filter(country_slug="afghanistan"))
    health_sector_total = sum(agg.total_usd for agg in DailyAggregate.objects.filter(dimension_value="Health"))

    assert afghanistan_total == 18000
    assert health_sector_total == 22000
    assert DailyAggregate.objects.filter(country_slug="syria").count() == 2
