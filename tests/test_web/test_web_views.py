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
def test_landing_page_unauthenticated_no_private_sections(client):
    response = client.get("/")
    assert response.status_code == 200

    content = response.content.decode()

    # Unauthenticated visitor must see public evidence CTA
    assert "Explore evidence" in content
    assert "HOPE Ecosystem Pillars" in content

    # Unauthenticated visitor must NOT see private section grid, links, Sign In, or mentions
    assert "Sign In" not in content
    assert "Explore Dashboards" not in content
    assert 'href="/dashboard/"' not in content
    assert 'href="/demographic/"' not in content
    assert 'href="/completion/"' not in content
    assert 'href="/grievance/"' not in content
    assert 'href="/risk/"' not in content

    # Sidebar must not have Dashboards or Countries fallback link
    assert "<span>Dashboards</span>" not in content
    assert "<span>Countries</span>" not in content


@pytest.mark.django_db
def test_landing_page_authenticated_shows_dashboards(client, user_factory):
    user = user_factory()
    client.force_login(user)

    response = client.get("/")
    assert response.status_code == 200

    content = response.content.decode()

    # Authenticated user sees operational dashboards launcher and sign out
    assert "Go to Dashboards" in content
    assert "Explore Dashboards" in content
    assert "Sign Out" in content
    assert 'href="/dashboard/"' in content
    assert 'href="/risk/"' in content


@pytest.mark.django_db
def test_protected_dashboards_redirect_unauthenticated(client):
    protected_urls = ["/dashboard/", "/demographic/", "/completion/", "/grievance/", "/risk/"]
    for url in protected_urls:
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response["Location"]
