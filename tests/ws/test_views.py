from unittest.mock import patch

from django.urls import reverse

from hope_live.utils.cache import DashboardCache


def test_callback_success(client):
    url = reverse("ws:notify")
    payload = {"message": "update"}

    with patch("hope_live.ws.views.notify_ui") as mock_notify:
        with patch.object(DashboardCache, "invalidate") as mock_invalidate:
            response = client.post(url, data=payload, content_type="application/json")

            assert response.status_code == 200
            mock_invalidate.assert_called_once()
            mock_notify.assert_called_once_with(payload)


def test_callback_invalid_json(client):
    url = reverse("ws:notify")

    with patch("hope_live.ws.views.sentry_sdk.capture_exception") as mock_sentry:
        response = client.post(url, data="not json", content_type="application/json")

        assert response.status_code == 400
        mock_sentry.assert_called_once()
