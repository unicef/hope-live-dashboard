import logging
from datetime import date
from typing import Any

import requests
from celery import shared_task  # type: ignore[import-untyped]
from constance import config
from django.db import transaction

from hope_live.analysis.models import DailyAggregate

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


@shared_task  # type: ignore[untyped-decorator]
def sync_daily_aggregates(target_years: list[int] | None = None) -> None:
    """Fetch DailyAggregate data from Country Report API and update local DB."""
    api_url = config.HOPE_COUNTRY_REPORT_API_URL
    token = config.HOPE_COUNTRY_REPORT_API_TOKEN
    query_id = config.HOPE_COUNTRY_REPORT_QUERY_ID

    # Verify logic:
    # 1. We need to run the query? Or fetch dataset?
    # Country Report Query API usually runs asynchronously.
    # For now, let's assume we can fetch the Latest execution result or trigger a run.
    # Simpler approach: Fetch from `data/dataset/{id}/content/` ? No, Query.
    # The URL pattern for query execution result: /api/queries/{id}/execute/ ?
    # Let's assume we use the Run endpoint.

    if not target_years:
        target_years = [date.today().year]

    headers = {"Authorization": f"Token {token}"}

    # First, fetch the query details to get the office slug
    query_url = f"{api_url}queries/{query_id}/"
    try:
        resp = requests.get(query_url, headers=headers, timeout=10)
        if resp.status_code != requests.codes.ok:
            logger.error(f"Failed to fetch query details: {resp.status_code}")
            return
        query_data = resp.json()
        office_url = query_data.get("office")
        if not office_url:
            logger.error("Query does not have an associated office")
            return

        # Extract slug from office URL (assuming format .../offices/SLUG/)
        office_slug = office_url.rstrip("/").split("/")[-1]
        run_endpoint = f"{api_url}offices/{office_slug}/queries/{query_id}/execute/"

    except Exception as e:
        logger.exception(f"Error preparing query execution: {e}")
        return

    # Warning: sync wait for execution might timeout if dataset is huge.
    # Better: check if recent dataset exists?
    # For now, proceed with execute (synchronous wait usually not supported properly by API if long).

    for year in target_years:
        try:
            # We want to filter by year. Arguments format depends on Parametrizer.
            # Assuming Arguments are passed as payload?
            # Or if it's a simple query without params?
            # Let's try passing arguments.
            payload = {"arguments": {"year": year}}
            logger.info(f"Syncing DailyAggregates for {year}...")

            # Note: This is an assumption on Country Report API.
            response = requests.post(run_endpoint, json=payload, headers=headers, timeout=30)

            if response.status_code == requests.codes.ok:
                raw_data: dict[str, Any] = response.json()
                # Expected format: {"data": [...], ...} or direct list if preview?
                # PQ generic returns usually: { "data": [rows...], "columns": ... }

                rows: list[dict[str, Any]] = raw_data.get("data", [])
                if not rows and isinstance(raw_data, list):
                    rows = raw_data

                if not rows:
                    logger.warning(f"No data returned for Year {year}")
                    continue

                save_aggregates(rows, year)

            else:
                logger.error(f"Failed to run query for {year}: {response.status_code} {response.text}")

        except Exception as e:
            logger.exception(f"Error syncing year {year}: {e}")


def save_aggregates(rows: list[dict[str, Any]], year: int) -> None:
    with transaction.atomic():
        # Clean up existing data for this year to avoid duplicates
        # (Assuming rows cover the whole year)
        # We filter by date__year = year
        DailyAggregate.objects.filter(date__year=year).delete()

        batch = []
        for item in rows:
            # Parse date if string
            item_date = item.get("date")
            if not item_date:
                continue

            batch.append(
                DailyAggregate(
                    date=item_date,
                    country_slug=item.get("country_slug", "unknown"),
                    dimension_type=item.get("dimension_type", "unknown"),
                    dimension_value=item.get("dimension_value", "unknown"),
                    total_usd=item.get("total_usd", 0) or 0,
                    total_qty=item.get("total_qty", 0) or 0,
                    payment_count=item.get("payment_count", 0) or 0,
                    total_beneficiaries=item.get("total_beneficiaries", 0) or 0,
                    total_children=item.get("total_children", 0) or 0,
                    total_pwd=item.get("total_pwd", 0) or 0,
                )
            )

            if len(batch) >= BATCH_SIZE:
                DailyAggregate.objects.bulk_create(batch)
                batch = []

        if batch:
            DailyAggregate.objects.bulk_create(batch)

        logger.info(f"Saved {len(rows)} records for {year}")
