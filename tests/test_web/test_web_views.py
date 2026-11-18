import pytest
from django.test import RequestFactory

from hope_live.analysis.models import FinancialAggregate, TimeGrain
from hope_live.web.views import CompletionView, DashboardView, DemographicView, RiskView


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


@pytest.mark.django_db
def test_risk_view(user_factory):
    user = user_factory()
    request = RequestFactory().get("/")
    request.user = user

    view = RiskView.as_view()
    response = view(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_landing_page_requires_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert "/login/" in response["Location"]
    assert "next=/" in response["Location"]


@pytest.mark.django_db
def test_landing_page_authenticated_hides_dashboard_launcher(client, user_factory):
    user = user_factory()
    client.force_login(user)

    response = client.get("/")
    assert response.status_code == 200

    content = response.content.decode()

    # The public page does not advertise the dashboard endpoint.
    assert "Go to Dashboards" not in content
    assert 'href="/dashboard/"' not in content


@pytest.mark.django_db
def test_protected_dashboards_redirect_unauthenticated(client):
    protected_urls = ["/dashboard/", "/demographic/", "/completion/", "/grievance/", "/risk/"]
    for url in protected_urls:
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response["Location"]
