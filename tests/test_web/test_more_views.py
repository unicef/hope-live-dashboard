import pytest
from django.test import RequestFactory

from hope_live.web.views import AboutView, ContactView, DetailsView, IndexView, TransfersView


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
