import contextlib
import datetime
import logging
import re
from typing import Any, cast
from urllib.parse import urlparse

import requests
from constance import config
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Max, Sum
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.translation import activate, get_language_from_path
from django.views.generic import TemplateView
from django.views.i18n import set_language as django_set_language

from hope_live.analysis.models import (
    CompletionAggregate,
    DemographicAggregate,
    FinancialAggregate,
    GrievanceAggregate,
)

logger = logging.getLogger(__name__)


def _parse_news_item_date(dt: Any) -> datetime.date | None:
    if isinstance(dt, datetime.date):
        return dt
    if isinstance(dt, str):
        with contextlib.suppress(ValueError):
            return datetime.datetime.strptime(dt.split("T")[0], "%Y-%m-%d").date()
    return None


SNIPPET_MAX_LEN = 130


def _create_news_item_snippet(desc: str) -> str:
    clean_desc = desc.replace("**", "").replace("\r", "")
    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()

    if len(clean_desc) > SNIPPET_MAX_LEN:
        return clean_desc[:SNIPPET_MAX_LEN].strip() + "..."
    return clean_desc


def _fetch_news_dataset_rows(api_url: str, query_id: int, headers: dict[str, str]) -> list[dict[str, Any]]:
    # 1. Fetch datasets
    dataset_url = f"{api_url}queries/{query_id}/dataset"
    resp = requests.get(dataset_url, headers=headers, timeout=10)
    resp.raise_for_status()
    datasets = resp.json()
    if isinstance(datasets, dict) and "results" in datasets:
        datasets = datasets["results"]

    if not datasets:
        return []

    # Get the first dataset (newest)
    dataset_id = datasets[0]["id"]

    # 2. Fetch data from that dataset
    data_url = f"{api_url}queries/{query_id}/dataset/{dataset_id}/data/"
    all_rows: list[dict[str, Any]] = []
    current_url: str | None = f"{data_url}?page_size=50"

    while current_url:
        r = requests.get(current_url, headers=headers, timeout=10)
        r.raise_for_status()
        raw_data = r.json()
        if isinstance(raw_data, dict):
            if "results" in raw_data:
                rows = raw_data.get("results", []) or []
                current_url = raw_data.get("next")
            else:
                rows = raw_data.get("data", []) or []
                current_url = None
        elif isinstance(raw_data, list):
            rows = raw_data
            current_url = None
        else:
            rows = []
            current_url = None

        if not rows:
            break
        all_rows.extend(rows)

    return all_rows


def fetch_hope_news() -> list[dict[str, Any]]:
    cache_key = "hope_news_updates_list"
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cast("list[dict[str, Any]]", cached_data)

    try:
        api_url = config.HOPE_COUNTRY_REPORT_API_URL
        token = config.HOPE_COUNTRY_REPORT_API_TOKEN
        query_id = getattr(config, "HOPE_NEWS_REPORT_QUERY_ID", 159)

        headers = {"Authorization": f"Token {token}"}
        all_rows = _fetch_news_dataset_rows(api_url, query_id, headers)

        processed = []
        for item in all_rows:
            if not item.get("active", True):
                continue

            processed.append(
                {
                    "version": item.get("version", "Update"),
                    "date": _parse_news_item_date(item.get("date")),
                    "snippet": _create_news_item_snippet(item.get("description", "")),
                    "description": item.get("description", ""),
                }
            )

        # Sort by date descending (newest first)
        processed.sort(key=lambda x: x["date"] or datetime.date.min, reverse=True)

        # Take the top 3
        top_updates = processed[:3]

        # Cache for 1 hour
        cache.set(cache_key, top_updates, 60 * 60)
        return top_updates
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Failed to fetch HOPE news updates: {e}")
        return []


class ContactView(TemplateView):
    template_name = "pages/contacts.html"


class AboutView(TemplateView):
    template_name = "pages/about.html"


BILLION = 1_000_000_000
MILLION = 1_000_000
THOUSAND = 1_000


def format_large_number(num: float) -> str:
    if num >= BILLION:
        val = num / BILLION
        return f"{val:.1f}B".replace(".0B", "B")
    if num >= MILLION:
        val = num / MILLION
        return f"{val:.1f}M".replace(".0M", "M")
    if num >= THOUSAND:
        val = num / THOUSAND
        return f"{val:.1f}K".replace(".0K", "K")
    return str(int(num))


class IndexView(TemplateView):
    template_name = "pages/landing.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Calculate Total Cash Disbursed (filtering by sector to avoid double counting)
        total_usd = (
            FinancialAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_usd"))["total"] or 0
        )

        # Calculate Total Individuals Reached
        total_beneficiaries = (
            DemographicAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_beneficiaries"))[
                "total"
            ]
            or 0
        )

        # Calculate Total Children Reached
        total_children = (
            DemographicAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_children"))["total"]
            or 0
        )

        # Calculate Total Households Reached
        total_households = (
            DemographicAggregate.objects.filter(dimension_type="sector").aggregate(total=Sum("total_households"))[
                "total"
            ]
            or 0
        )

        # Calculate Active Countries Count
        total_countries = FinancialAggregate.objects.values("country_slug").distinct().count()

        # HOPE at a glance sidebar statistics
        # Unique countries across all aggregates
        countries_set = set(FinancialAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.update(DemographicAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.update(CompletionAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.update(GrievanceAggregate.objects.values_list("country_slug", flat=True).distinct())
        countries_set.discard("")
        countries_set.discard(None)
        total_countries_glance = len(countries_set)

        # Unique programs count from FinancialAggregate (where dimension_type is program)
        total_programs_glance = (
            FinancialAggregate.objects.filter(dimension_type="program").values("dimension_value").distinct().count()
        )

        # Data source name
        total_sources_glance = "HOPE Database"

        # Find latest data date
        latest_date_f = FinancialAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        latest_date_d = DemographicAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        latest_date_c = CompletionAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        latest_date_g = GrievanceAggregate.objects.aggregate(max_date=Max("date"))["max_date"]
        dates = [d for d in [latest_date_f, latest_date_d, latest_date_c, latest_date_g] if d]
        latest_data_date = max(dates) if dates else None

        if latest_data_date:
            latest_data_str = latest_data_date.strftime("%B %Y")
        else:
            latest_data_str = "May 2026"

        context["total_cash_disbursed"] = format_large_number(total_usd)
        context["total_individuals_reached"] = format_large_number(total_beneficiaries)
        context["total_children"] = format_large_number(total_children)
        context["total_households"] = format_large_number(total_households)
        context["total_countries"] = total_countries
        # Calculate verification success rate from CompletionAggregate status counts
        reconciled_sum = (
            CompletionAggregate.objects.filter(dimension_type="status", dimension_value="RECONCILED").aggregate(
                total=Sum("payment_count")
            )["total"]
            or 0
        )
        open_sum = (
            CompletionAggregate.objects.filter(dimension_type="status", dimension_value="OPEN").aggregate(
                total=Sum("payment_count")
            )["total"]
            or 0
        )
        total_payments = reconciled_sum + open_sum
        if total_payments > 0:
            context["verification_success_rate"] = round((reconciled_sum / total_payments) * 100, 1)
        else:
            context["verification_success_rate"] = 98.7

        context["total_countries_glance"] = total_countries_glance or 170
        context["total_programs_glance"] = total_programs_glance or 450
        context["total_sources_glance"] = total_sources_glance
        context["latest_data_str"] = latest_data_str
        context["hope_updates"] = fetch_hope_news()

        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)
        # Data is now fetched via REST API by year tabs
        # No server-side metrics or embedded JSON needed


class DemographicView(LoginRequiredMixin, TemplateView):
    template_name = "pages/demographic.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)
        # Data is now fetched via REST API by year tabs
        # No server-side metrics or embedded JSON needed


class CompletionView(LoginRequiredMixin, TemplateView):
    template_name = "pages/completion.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)
        # Data is now fetched via REST API by year tabs
        # No server-side metrics or embedded JSON needed


class GrievanceView(LoginRequiredMixin, TemplateView):
    template_name = "pages/grievance.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)


class RiskView(LoginRequiredMixin, TemplateView):
    template_name = "pages/risk.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return super().get_context_data(**kwargs)


class TransfersView(LoginRequiredMixin, TemplateView):
    template_name = "pages/transfers.html"


class DetailsView(LoginRequiredMixin, TemplateView):
    template_name = "pages/details.html"


def set_language(request: HttpRequest) -> HttpResponseRedirect:
    next_url = request.POST.get("next", request.GET.get("next"))
    if next_url:
        path = urlparse(next_url).path
        lang = get_language_from_path(path)
        if lang:
            activate(lang)
        else:
            activate(settings.LANGUAGE_CODE)
    return django_set_language(request)
