import pytest
from django.test import RequestFactory

from hope_live.analysis.models import FinancialAggregate, TimeGrain
from hope_live.web.views import CompletionView, DashboardView, DemographicView


@pytest.mark.django_db
def test_dashboard_view(user_factory):
    user = user_factory()
    FinancialAggregate.objects.create(
        date="2023-01-01",
        time_grain=TimeGrain.DAILY,
        country_slug="test",
        dimension_type="sector",
        dimension_value="health",
        total_usd=100,
        payment_count=5,
    )

    request = RequestFactory().get("/")
    request.user = user

    view = DashboardView.as_view()
    response = view(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_demographic_view(user_factory):
    user = user_factory()
    request = RequestFactory().get("/")
    request.user = user

    view = DemographicView.as_view()
    response = view(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_completion_view(user_factory):
    user = user_factory()
    request = RequestFactory().get("/")
    request.user = user

    view = CompletionView.as_view()
    response = view(request)
    assert response.status_code == 200
