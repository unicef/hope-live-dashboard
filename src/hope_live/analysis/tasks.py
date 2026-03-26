import logging
from typing import Any

import requests
from celery import shared_task  # type: ignore[import-untyped]
from constance import config
from django.db import transaction
from tenacity import retry, stop_after_attempt, wait_exponential

from hope_live.analysis.models import DailyAggregate, SyncDailyAggregatesJob

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _fetch_url_with_retry(url: str, headers: dict[str, str], timeout: int) -> requests.Response:
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response


def _determine_target_years(datasets: list[dict[str, Any]], requested_years: list[int] | None) -> list[int]:
    if requested_years:
        return requested_years
    years = []
    for d in datasets:
        y = d.get("arguments", {}).get("year")
        if y:
            years.append(int(y))
    return sorted(set(years))


def _process_year_data(
    target_year: int, datasets: list[dict[str, Any]], base_url: str, headers: dict[str, str], job_id: str
) -> int:
    dataset_id = _find_dataset_id_for_year(datasets, target_year)
    if not dataset_id:
        logger.info(f"[Job {job_id}] No dataset found for year {target_year}")
        return 0

    logger.info(f"[Job {job_id}] Processing dataset ID {dataset_id} for year {target_year}")
    data_endpoint = f"{base_url}{dataset_id}/data/"
    all_rows = _fetch_all_pages(data_endpoint, headers, job_id)

    if not all_rows:
        logger.warning(f"[Job {job_id}] No data returned for year {target_year}")
        return 0

    logger.info(f"[Job {job_id}] Total rows fetched for year {target_year}: {len(all_rows)}")
    save_aggregates(all_rows, target_year)
    return len(all_rows)


@shared_task(name="hope_live.analysis.tasks.sync_daily_aggregates", bind=True)  # type: ignore[untyped-decorator]
def sync_daily_aggregates(
    self: Any, pk: int | None = None, version: int | None = None, target_years: list[int] | None = None
) -> str:
    """Fetch DailyAggregate data from Country Report API and update local DB."""
    job = SyncDailyAggregatesJob.objects.filter(pk=pk).first() if pk else None
    job_id = str(job.pk) if job else "N/A"

    if job:
        job.error_message = None
        job.save(update_fields=["error_message"])

    try:
        api_url = config.HOPE_COUNTRY_REPORT_API_URL
        token = config.HOPE_COUNTRY_REPORT_API_TOKEN
        query_id = config.HOPE_COUNTRY_REPORT_QUERY_ID
        headers = {"Authorization": f"Token {token}"}

        context = _prepare_sync_context(api_url, query_id, headers, job_id)
        if not context:
            msg = f"[Job {job_id}] Failed to prepare sync context."
            if job:
                job.error_message = msg
                job.save(update_fields=["error_message"])
            return msg

        office_slug, datasets = context
        years_to_sync = _determine_target_years(datasets, target_years)

        if not years_to_sync:
            logger.warning(f"[Job {job_id}] No target years found in datasets.")
            return "No target years found."

        total_rows = 0
        errors = []
        base_url = f"{api_url}queries/{query_id}/dataset/"
        for idx, target_year in enumerate(years_to_sync, 1):
            self.update_state(
                state="PROGRESS", meta={"current_year": target_year, "progress": f"{idx}/{len(years_to_sync)}"}
            )
            try:
                total_rows += _process_year_data(target_year, datasets, base_url, headers, job_id)
            except Exception as e:
                logger.exception(f"[Job {job_id}] Error syncing aggregates for year {target_year}: {e}")
                errors.append(f"Year {target_year}: {e}")

        if errors and job:
            job.error_message = "\n".join(errors)
            job.save(update_fields=["error_message"])

        return f"Successfully synced {total_rows} rows for years: {years_to_sync}"

    except Exception as e:
        if job:
            job.error_message = str(e)
            job.save(update_fields=["error_message"])
        raise


def _prepare_sync_context(
    api_url: str, query_id: str, headers: dict[str, str], job_id: str
) -> tuple[str, list[dict[str, Any]]] | None:
    """Fetch query and available datasets."""
    try:
        url = f"{api_url}queries/{query_id}/dataset"
        logger.info(f"[Job {job_id}] Fetching datasets from: {url}")
        resp = _fetch_url_with_retry(url, headers, 10)

        # API URL usually ends with /offices/<slug>/
        # e.g. https://.../api/offices/global/
        try:
            office_slug = api_url.rstrip("/").split("/")[-1]
        except IndexError:
            office_slug = "global"

        datasets = resp.json()
        if isinstance(datasets, dict) and "results" in datasets:
            datasets = datasets["results"]

        logger.info(f"[Job {job_id}] Found {len(datasets)} datasets for office '{office_slug}'")
        return office_slug, datasets

    except Exception:
        logger.exception(f"[Job {job_id}] Error preparing sync context")
        return None


def _find_dataset_id_for_year(datasets: list[dict[str, Any]], year: int) -> int | None:
    """Locate the dataset ID matching the target year."""
    for dataset in datasets:
        if dataset.get("arguments", {}).get("year") == year:
            return int(dataset["id"])
    return None


def _fetch_all_pages(data_endpoint: str, headers: dict[str, str], job_id: str) -> list[dict[str, Any]]:
    """Fetch all rows from the endpoint handling pagination."""
    all_rows: list[dict[str, Any]] = []
    current_url: str | None = f"{data_endpoint}?page_size=500"
    page_count = 0

    while current_url:
        page_count += 1
        logger.info(f"[Job {job_id}] Fetching page {page_count}...")
        try:
            response = _fetch_url_with_retry(current_url, headers, 60)
        except Exception as e:
            logger.exception(f"[Job {job_id}] Error fetching page {page_count}: {e}")
            break

        raw_data: dict[str, Any] = response.json()
        if isinstance(raw_data, dict) and "results" in raw_data:
            rows = raw_data.get("results", [])
            if not rows:
                break
            all_rows.extend(rows)
            current_url = raw_data.get("next")
        else:
            rows = raw_data.get("data", []) or (raw_data if isinstance(raw_data, list) else [])
            if not rows:
                break
            all_rows.extend(rows)
            logger.info(f"[Job {job_id}] Received {len(rows)} rows (non-paginated)")
            break

    return all_rows


@shared_task(name="hope_live.analysis.tasks.save_aggregates")  # type: ignore[untyped-decorator]
def save_aggregates(rows: list[dict[str, Any]], year: int) -> None:
    with transaction.atomic():
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
                DailyAggregate.objects.bulk_create(
                    batch,
                    update_conflicts=True,
                    unique_fields=["date", "country_slug", "dimension_type", "dimension_value"],
                    update_fields=[
                        "total_usd",
                        "total_qty",
                        "payment_count",
                        "total_beneficiaries",
                        "total_children",
                        "total_pwd",
                    ],
                )
                batch = []

        if batch:
            DailyAggregate.objects.bulk_create(
                batch,
                update_conflicts=True,
                unique_fields=["date", "country_slug", "dimension_type", "dimension_value"],
                update_fields=[
                    "total_usd",
                    "total_qty",
                    "payment_count",
                    "total_beneficiaries",
                    "total_children",
                    "total_pwd",
                ],
            )

        logger.info(f"Saved {len(rows)} records for {year}")


@shared_task(name="hope_live.analysis.tasks.schedule_sync_daily_aggregates")  # type: ignore[untyped-decorator]
def schedule_sync_daily_aggregates() -> None:
    """Periodic task to create and queue a SyncDailyAggregatesJob."""
    job = SyncDailyAggregatesJob.objects.create(description="Scheduled Daily Aggregate Sync")
    job.queue()
