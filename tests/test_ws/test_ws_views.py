import json

from django.test import RequestFactory

from hope_live.ws.views import callback


def test_callback_view():
    request = RequestFactory().post("/", data=json.dumps({"test": "data"}), content_type="application/json")
    response = callback(request)
    assert response.status_code == 200


def test_callback_view_invalid_json():
    request = RequestFactory().post("/", data="invalid json", content_type="application/json")
    response = callback(request)
    assert response.status_code == 400
