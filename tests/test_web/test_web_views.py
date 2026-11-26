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
def test_landing_page_authenticated_shows_sidebar_without_public_launcher(client, user_factory):
    user = user_factory()
    client.force_login(user)

    response = client.get("/")
    assert response.status_code == 200

    content = response.content.decode()

    # The public header no longer advertises a dashboard launcher, but the
    # authenticated sidebar links to every internal dashboard.
    assert "Go to Dashboards" not in content
    assert 'aria-label="Sidebar"' in content
    for path in ("/dashboard/", "/demographic/", "/completion/", "/grievance/", "/risk/"):
        assert path in content


@pytest.mark.django_db
def test_protected_dashboards_redirect_unauthenticated(client):
    protected_urls = ["/dashboard/", "/demographic/", "/completion/", "/grievance/", "/risk/"]
    for url in protected_urls:
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response["Location"]


@pytest.mark.django_db
def test_sidebar_is_present_on_all_authenticated_pages(client, user_factory, monkeypatch):
    client.force_login(user_factory())
    from hope_live.web import views

    monkeypatch.setattr(
        views,
        "fetch_hope_news",
        lambda limit=None: [
            {
                "version": "HOPE v1",
                "slug": "hope-v1",
                "date": None,
                "snippet": "",
                "description": "Update body",
            }
        ],
    )

    for url in ("/", "/about/", "/contacts/", "/updates/hope-v1/"):
        response = client.get(url)
        assert response.status_code == 200, url
        content = response.content.decode()
        assert 'aria-label="Sidebar"' in content, url
        assert "/dashboard/" in content, url


@pytest.mark.django_db
def test_login_page_does_not_show_the_sidebar(client):
    response = client.get("/login/")
    assert response.status_code == 200
    assert 'aria-label="Sidebar"' not in response.content.decode()
