import logging
from typing import Any

import requests
from celery import shared_task  # type: ignore[import-untyped]
from constance import config
from django.db import transaction

from hope_live.analysis.models import DailyAggregate

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


@shared_task(name="hope_live.analysis.tasks.sync_daily_aggregates")  # type: ignore[untyped-decorator]
def sync_daily_aggregates(target_years: list[int] | None = None) -> None:
    """Fetch DailyAggregate data from Country Report API and update local DB."""
    api_url = config.HOPE_COUNTRY_REPORT_API_URL
    token = config.HOPE_COUNTRY_REPORT_API_TOKEN
    query_id = config.HOPE_COUNTRY_REPORT_QUERY_ID

    headers = {"Authorization": f"Token {token}"}
    context = _prepare_sync_context(api_url, query_id, headers)
    if not context:
        return

    office_slug, datasets = context

    if not target_years:
        target_years = []
        for d in datasets:
            y = d.get("arguments", {}).get("year")
            if y:
                target_years.append(int(y))
        target_years = sorted(set(target_years))

    if not target_years:
        logger.warning("No target years found in datasets.")
        return

    for target_year in target_years:
        try:
            dataset_id = _find_dataset_id_for_year(datasets, target_year)
            if not dataset_id:
                logger.info(f"No dataset found for year {target_year}")
                continue

            logger.info(f"Processing dataset ID {dataset_id} for year {target_year}")
            data_endpoint = f"{api_url}queries/{query_id}/dataset/{dataset_id}/data/"
            all_rows = _fetch_all_pages(data_endpoint, headers)

            if not all_rows:
                logger.warning(f"No data returned for year {target_year}")
                continue

            logger.info(f"Total rows fetched for year {target_year}: {len(all_rows)}")
            save_aggregates(all_rows, target_year)

        except Exception as e:
            logger.exception(f"Error syncing aggregates for year {target_year}: {e}")


def _prepare_sync_context(
    api_url: str, query_id: str, headers: dict[str, str]
) -> tuple[str, list[dict[str, Any]]] | None:
    """Fetch query and available datasets."""
    try:
        url = f"{api_url}queries/{query_id}/dataset"
        logger.info(f"Fetching datasets from: {url}")
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != requests.codes.ok:
            logger.error(f"Failed to fetch datasets: {resp.status_code}")
            logger.error(f"Response: {resp.text}")
            return None

        # API URL usually ends with /offices/<slug>/
        # e.g. https://.../api/offices/global/
        try:
            office_slug = api_url.rstrip("/").split("/")[-1]
        except IndexError:
            office_slug = "global"

        datasets = resp.json()
        if isinstance(datasets, dict) and "results" in datasets:
            datasets = datasets["results"]

        logger.info(f"Found {len(datasets)} datasets for office '{office_slug}'")
        return office_slug, datasets

    except Exception:
        logger.exception("Error preparing sync context")
        return None


def _find_dataset_id_for_year(datasets: list[dict[str, Any]], year: int) -> int | None:
    """Locate the dataset ID matching the target year."""
    for dataset in datasets:
        if dataset.get("arguments", {}).get("year") == year:
            return int(dataset["id"])
    return None


def _fetch_all_pages(data_endpoint: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    """Fetch all rows from the endpoint handling pagination."""
    all_rows: list[dict[str, Any]] = []
    current_url: str | None = f"{data_endpoint}?page_size=500"
    page_count = 0

    while current_url:
        page_count += 1
        logger.info(f"Fetching page {page_count}...")
        try:
            response = requests.get(current_url, headers=headers, timeout=60)
        except Exception as e:
            logger.exception(f"Error fetching page {page_count}: {e}")
            break

        if response.status_code != requests.codes.ok:
            logger.error(f"Failed to fetch page {page_count}: {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
            break

        raw_data: dict[str, Any] = response.json()
        if isinstance(raw_data, dict) and "results" in raw_data:
            rows = raw_data.get("results", [])
            all_rows.extend(rows)
            current_url = raw_data.get("next")
        else:
            rows = raw_data.get("data", []) or (raw_data if isinstance(raw_data, list) else [])
            all_rows.extend(rows)
            logger.info(f"Received {len(rows)} rows (non-paginated)")
            break

    return all_rows


@shared_task(name="hope_live.analysis.tasks.save_aggregates")  # type: ignore[untyped-decorator]
def save_aggregates(rows: list[dict[str, Any]], year: int) -> None:
    with transaction.atomic():
        DailyAggregate.objects.filter(date__year=year).delete()

        batch = []
        for item in rows:
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
