import datetime
import io
import json
import logging
from pathlib import Path
from typing import Any

import requests
from celery import shared_task  # type: ignore[import-untyped]
from constance import config
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction
from tenacity import retry, stop_after_attempt, wait_exponential

from hope_live.analysis.models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
    SyncDailyAggregatesJob,
)

ISO3_TO_SLUG = {
    "AFG": "afghanistan",
    "AGO": "angola",
    "ARM": "armenia",
    "BGD": "bangladesh",
    "BWA": "botswana",
    "CAF": "central-african-republic",
    "TCD": "chad",
    "COD": "democratic-republic-of-congo",
    "HTI": "haiti",
    "KEN": "kenya",
    "MDG": "madagascar",
    "MMR": "myanmar",
    "NGA": "nigeria",
    "PSE": "palestine-state-of",
    "CMR": "republic-of-cameroon",
    "MOZ": "republic-of-mozambique",
    "SEN": "senegal",
    "SLE": "sierra-leone",
    "SOM": "somalia",
    "SSD": "south-sudan",
    "SDN": "sudan",
    "SYR": "syria",
    "UKR": "ukraine",
    "VNM": "vietnam",
    "YEM": "yemen",
}

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
    if not years:
        years.append(datetime.date.today().year)
    return sorted(set(years))


def _process_year_data(  # noqa: PLR0913
    target_year: int,
    datasets: list[dict[str, Any]],
    base_url: str,
    headers: dict[str, str],
    job_id: str,
    model_name: str,
    update_fields: list[str],
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
    save_aggregates(all_rows, target_year, model_name, update_fields)
    return len(all_rows)


@shared_task(name="hope_live.analysis.tasks.sync_daily_aggregates", bind=True)  # type: ignore[untyped-decorator]
def sync_daily_aggregates(
    self: Any, pk: int | None = None, version: int | None = None, target_years: list[int] | None = None
) -> str:
    """Fetch Aggregate data from Country Report API and update local DB."""
    job = SyncDailyAggregatesJob.objects.filter(pk=pk).first() if pk else None
    job_id = str(job.pk) if job else "N/A"

    if job:
        job.error_message = ""
        job.save(update_fields=["error_message"])

    try:
        api_url = config.HOPE_COUNTRY_REPORT_API_URL
        token = config.HOPE_COUNTRY_REPORT_API_TOKEN
        headers = {"Authorization": f"Token {token}"}

        configs = [
            (config.HOPE_FINANCIAL_REPORT_QUERY_ID, "FinancialAggregate", ["total_usd", "total_qty", "payment_count"]),
            (
                config.HOPE_DEMOGRAPHIC_REPORT_QUERY_ID,
                "DemographicAggregate",
                ["total_beneficiaries", "total_children", "total_pwd", "total_households"],
            ),
            (config.HOPE_COMPLETION_REPORT_QUERY_ID, "CompletionAggregate", ["payment_count", "total_usd"]),
            (config.HOPE_GRIEVANCE_REPORT_QUERY_ID, "GrievanceAggregate", ["ticket_count"]),
        ]

        total_rows = 0
        errors = []

        for query_id, model_name, update_fields in configs:
            if not query_id:
                continue

            context = _prepare_sync_context(api_url, str(query_id), headers, job_id)
            if not context:
                errors.append(f"Failed to prepare sync context for query {query_id}")
                continue

            office_slug, datasets = context
            years_to_sync = _determine_target_years(datasets, target_years)

            base_url = f"{api_url}queries/{query_id}/dataset/"
            for idx, target_year in enumerate(years_to_sync, 1):
                self.update_state(
                    state="PROGRESS",
                    meta={"current_year": target_year, "model": model_name, "progress": f"{idx}/{len(years_to_sync)}"},
                )
                try:
                    total_rows += _process_year_data(
                        target_year, datasets, base_url, headers, job_id, model_name, update_fields
                    )
                except Exception as e:
                    logger.exception(f"[Job {job_id}] Error syncing {model_name} for year {target_year}: {e}")
                    errors.append(f"{model_name} Year {target_year}: {e}")

        if errors and job:
            job.error_message = "\n".join(errors)
            job.save(update_fields=["error_message"])

        return f"Successfully synced {total_rows} rows."

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
    current_url: str | None = f"{data_endpoint}?page_size={BATCH_SIZE}"
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


def get_fertility_rate(country_slug: str, year: int) -> float:
    file_path = Path(__file__).parent / "rates" / "fertility_rates.json"
    if not file_path.exists():
        return 3.0

    try:
        with open(file_path) as f:
            rates_data = json.load(f)
    except (OSError, ValueError):
        return 3.0

    slug_to_iso3 = {v: k for k, v in ISO3_TO_SLUG.items()}
    target_iso3 = slug_to_iso3.get(country_slug.lower())
    if not target_iso3:
        return 3.0

    for entry in rates_data:
        if entry.get("Country Code") == target_iso3:
            if str(year) in entry:
                try:
                    return float(entry[str(year)] or 3.0)
                except ValueError:
                    pass

            # Fallback to the latest available year
            year_keys = [k for k in entry if k.isdigit()]
            if year_keys:
                latest_year = sorted(year_keys, reverse=True)[0]
                try:
                    return float(entry[latest_year] or 3.0)
                except ValueError:
                    pass

    return 3.0


def _calculate_demographic_children(rows: list[dict[str, Any]], default_year: int) -> None:
    for item in rows:
        dim_type = str(item.get("dimension_type", "")).strip().lower()
        dim_value = str(item.get("dimension_value", "")).strip().upper()
        if dim_type != "sector" or dim_value != "MULTI_PURPOSE":
            continue

        children = int(item.get("total_children") or 0)
        if children > 0:
            continue

        households = float(item.get("total_households") or 0)
        if households <= 0:
            continue

        country = str(item.get("country_slug", "")).strip().lower()
        item_date_str = item.get("date")
        if isinstance(item_date_str, str):
            item_year = int(item_date_str.split("-")[0])
        elif item_date_str is not None and hasattr(item_date_str, "year"):
            item_year = item_date_str.year
        else:
            item_year = default_year

        rate = get_fertility_rate(country, item_year)
        item["total_children"] = int(households * rate)


def _transform_completion_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    transformed: list[dict[str, Any]] = []
    for item in rows:
        dim_type = str(item.get("dimension_type", "")).strip().lower()

        if dim_type == "verification_status" or dim_type.startswith("pp_"):
            continue

        if dim_type == "status":
            continue

        if dim_type == "reconciliation_status":
            item["dimension_type"] = "status"
            dv = str(item.get("dimension_value", "")).strip().upper()
            item["dimension_value"] = "Reconciled" if dv == "RECONCILED" else "Open"

        transformed.append(item)
    return transformed


@shared_task(name="hope_live.analysis.tasks.save_aggregates")  # type: ignore[untyped-decorator]
def save_aggregates(rows: list[dict[str, Any]], year: int, model_name: str, update_fields: list[str]) -> None:
    ModelClass = apps.get_model("analysis", model_name)

    if model_name == "DemographicAggregate":
        _calculate_demographic_children(rows, year)
    elif model_name == "CompletionAggregate":
        rows = _transform_completion_rows(rows)

    # Deduplicate rows by unique fields to prevent "ON CONFLICT DO UPDATE command cannot affect row a second time"

    unique_rows = {}
    default_grain = "monthly" if model_name == "DemographicAggregate" else "daily"
    for item in rows:
        item_date = item.get("date")
        if not item_date:
            continue
        raw_dim_val = item.get("dimension_value")
        dim_val = "unknown" if raw_dim_val is None else str(raw_dim_val)

        time_grain = item.get("time_grain") or default_grain

        key = (
            str(item_date),
            time_grain,
            item.get("country_slug", "unknown"),
            item.get("dimension_type", "unknown"),
            dim_val.strip().upper(),
        )
        unique_rows[key] = item

    with transaction.atomic():
        batch = []
        for key, item in unique_rows.items():
            kwargs = {
                "date": key[0],
                "time_grain": key[1],
                "country_slug": key[2],
                "dimension_type": key[3],
                "dimension_value": key[4],
            }
            for field in update_fields:
                kwargs[field] = item.get(field, 0) or 0

            batch.append(ModelClass(**kwargs))

            if len(batch) >= BATCH_SIZE:
                ModelClass.objects.bulk_create(
                    batch,
                    update_conflicts=True,
                    unique_fields=["date", "time_grain", "country_slug", "dimension_type", "dimension_value"],
                    update_fields=update_fields,
                )
                batch = []

        if batch:
            ModelClass.objects.bulk_create(
                batch,
                update_conflicts=True,
                unique_fields=["date", "time_grain", "country_slug", "dimension_type", "dimension_value"],
                update_fields=update_fields,
            )

        logger.info(
            f"Saved {len(unique_rows)} unique records for {year} into {model_name} (out of {len(rows)} total rows)"
        )


@shared_task(name="hope_live.analysis.tasks.schedule_sync_daily_aggregates")  # type: ignore[untyped-decorator]
def schedule_sync_daily_aggregates(target_years: list[int] | None = None) -> None:
    """Periodic task to create and queue a SyncDailyAggregatesJob."""
    job = SyncDailyAggregatesJob.objects.create(description="Scheduled Daily Aggregate Sync")

    # Bypass job.queue() to pass custom kwargs, then manually set the queued state
    res = sync_daily_aggregates.delay(job.pk, job.version, target_years=target_years)
    job.set_queued(res)


@shared_task(name="hope_live.analysis.tasks.clear_daily_aggregates")  # type: ignore[untyped-decorator]
def clear_daily_aggregates(user_id: int) -> str:
    """Delete all aggregate records from the database. Restricted to superusers."""
    user_model = get_user_model()
    try:
        user = user_model.objects.get(pk=user_id)
    except user_model.DoesNotExist as err:
        logger.warning(f"clear_daily_aggregates attempted with invalid user_id: {user_id}")
        raise ValueError("Error: User not found.") from err

    if not user.is_superuser:
        logger.warning(f"clear_daily_aggregates attempted by non-superuser: {user.username}")
        raise PermissionError("Permission denied: Only superusers can clear daily aggregates.")

    count = 0
    for model_class in [FinancialAggregate, DemographicAggregate, CompletionAggregate, GrievanceAggregate]:
        c, _ = model_class.objects.all().delete()  # type: ignore[attr-defined]
        count += c

    logger.info(f"Deleted {count} aggregate records by superuser {user.username}.")
    return f"Successfully deleted {count} aggregate records."


@shared_task(name="hope_live.analysis.tasks.update_fertility_rates")  # type: ignore[untyped-decorator]
def update_fertility_rates() -> str:
    """Task to run management command update_fertility_rates to update local rates."""
    out = io.StringIO()
    call_command("update_fertility_rates", stdout=out)
    return out.getvalue()
