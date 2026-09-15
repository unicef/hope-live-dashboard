import csv
import io
import json

import pytest
from rest_framework.test import APIClient

from tests.extras.testutils.factories.analysis import RiskAggregateFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_export_json_format(api_client):
    RiskAggregateFactory.create_batch(2)

    response = api_client.get("/api/analysis/export/", {"format": "json"})

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert "attachment" in response["Content-Disposition"]

    payload = json.loads(response.content)
    assert len(payload) == 2
    assert "risk_code" in payload[0]


@pytest.mark.django_db
def test_export_csv_format(api_client):
    RiskAggregateFactory(module="registration", severity="critical")

    response = api_client.get("/api/analysis/export/", {"format": "csv"})

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert "attachment" in response["Content-Disposition"]

    reader = csv.DictReader(io.StringIO(response.content.decode()))
    rows = list(reader)
    assert len(rows) == 1
    assert "risk_code" in reader.fieldnames
    assert rows[0]["module"] == "registration"
    assert rows[0]["severity"] == "critical"


@pytest.mark.django_db
def test_export_xlsx_format(api_client):
    RiskAggregateFactory.create_batch(2)

    response = api_client.get("/api/analysis/export/", {"format": "xlsx"})

    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment" in response["Content-Disposition"]
    assert len(response.content) > 0
