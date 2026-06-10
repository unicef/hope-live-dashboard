import pytest
from django.test import RequestFactory

from hope_live.analysis.models import (
    DemographicAggregate,
    FinancialAggregate,
    TimeGrain,
)
from hope_live.web.views import AboutView, ContactView, DetailsView, IndexView, TransfersView, format_large_number


@pytest.mark.django_db
def test_simple_template_views(user_factory):
    user = user_factory()
    request = RequestFactory().get("/")
    request.user = user

    views_to_test = [
        ContactView,
        AboutView,
        TransfersView,
        DetailsView,
    ]

    for view_class in views_to_test:
        view = view_class.as_view()
        response = view(request)
        assert response.status_code == 200


@pytest.mark.django_db
def test_index_view(user_factory):
    user = user_factory()
    request = RequestFactory().get("/")
    request.user = user

    view = IndexView.as_view()
    response = view(request)

    assert response.status_code == 200


def test_format_large_number():
    assert format_large_number(1_200_000_000) == "1.2B"
    assert format_large_number(1_000_000_000) == "1B"
    assert format_large_number(15_400_000) == "15.4M"
    assert format_large_number(15_000_000) == "15M"
    assert format_large_number(450_000) == "450K"
    assert format_large_number(450) == "450"
    assert format_large_number(0) == "0"


@pytest.mark.django_db
def test_index_view_dynamic_context(user_factory):
    # Setup test aggregates
    FinancialAggregate.objects.create(
        date="2026-05-15",
        time_grain=TimeGrain.DAILY,
        country_slug="kenya",
        dimension_type="sector",
        dimension_value="health",
        total_usd=1_500_000,
        payment_count=5,
    )
    FinancialAggregate.objects.create(
        date="2026-06-01",
        time_grain=TimeGrain.DAILY,
        country_slug="somalia",
        dimension_type="program",
        dimension_value="DCT-Somalia",
        total_usd=3_000_000,
        payment_count=10,
    )

    DemographicAggregate.objects.create(
        date="2026-05-20",
        time_grain=TimeGrain.DAILY,
        country_slug="kenya",
        dimension_type="sector",
        dimension_value="health",
        total_beneficiaries=50_000,
        total_children=35_000,
        total_pwd=5_000,
        total_households=10_000,
    )

    user = user_factory()
    request = RequestFactory().get("/")
    request.user = user

    view = IndexView()
    view.setup(request)
    context = view.get_context_data()

    # Assert correct calculations and formatting
    assert context["total_cash_disbursed"] == "1.5M"  # from sector filter
    assert context["total_individuals_reached"] == "50K"  # from sector filter
    assert context["total_children"] == "35K"
    assert context["total_households"] == "10K"
    assert context["total_countries"] == 2  # kenya, somalia
    assert context["total_countries_glance"] == 2
    assert context["total_programs_glance"] == 1  # DCT-Somalia
    assert context["total_sources_glance"] == "HOPE Database"
    assert context["latest_data_str"] == "June 2026"
