import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import Count, F, Min, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

from hope_live.models import Payment

from .models import DailyAggregate

logger = logging.getLogger(__name__)
BULK_CREATE_BATCH_SIZE = 2500


@shared_task()
def refresh_daily_aggregates(days_back: int = 730) -> None:
    """Rebuilds the DailyAggregate table from raw Payment data."""
    dimensions = {
        "sector": "program__sector",
        "program": "program__name",
        "fsp": "financial_service_provider__name",
        "region": "business_area__region_name",
        "status": "status",
        "delivery_mechanism": "delivery_type__name",
    }

    # Use timezone-aware datetime for the filter
    cutoff_dt = timezone.now() - timedelta(days=days_back)

    # 1. Filter Payments by the time window
    base_qs = Payment.objects.filter(
        is_removed=False,
        conflicted=False,
        status_date__gte=cutoff_dt,
    ).annotate(effective_date=TruncDate(Coalesce("delivery_date", "entitlement_date", "status_date")))

    # Helper to sum nullable fields safely
    def sum_coalesce(field: str) -> Sum:
        return Sum(Coalesce(field, 0))

    # Sum of all 10 PWD fields in Household
    pwd_expression = (
        sum_coalesce("household__female_age_group_0_5_disabled_count")
        + sum_coalesce("household__female_age_group_6_11_disabled_count")
        + sum_coalesce("household__female_age_group_12_17_disabled_count")
        + sum_coalesce("household__female_age_group_18_59_disabled_count")
        + sum_coalesce("household__female_age_group_60_disabled_count")
        + sum_coalesce("household__male_age_group_0_5_disabled_count")
        + sum_coalesce("household__male_age_group_6_11_disabled_count")
        + sum_coalesce("household__male_age_group_12_17_disabled_count")
        + sum_coalesce("household__male_age_group_18_59_disabled_count")
        + sum_coalesce("household__male_age_group_60_disabled_count")
    )

    with transaction.atomic():
        # 2. Determine the actual date range affected by these payments
        affected_dates = base_qs.aggregate(min_date=Min("effective_date"))
        min_affected_date = affected_dates["min_date"]

        if min_affected_date:
            logger.info(f"Deleting aggregates from {min_affected_date} onwards")
            DailyAggregate.objects.filter(date__gte=min_affected_date).delete()
        else:
            logger.info("No payments found in window, skipping deletion.")

        for dim_type, db_field in dimensions.items():
            stats = (
                base_qs.values("effective_date", "business_area__slug", val=F(db_field))
                .annotate(
                    usd=Sum("delivered_quantity_usd"),
                    qty=Sum("delivered_quantity"),
                    count=Count("id"),
                    beneficiaries=Sum("household__size"),
                    children=Sum("household__children_count"),
                    pwd=pwd_expression,
                )
                .order_by("effective_date")
            )

            batch = []
            for row in stats:
                if not row["effective_date"] or not row["business_area__slug"]:
                    continue

                dim_value = row["val"] or "Unknown"

                batch.append(
                    DailyAggregate(
                        date=row["effective_date"],
                        country_slug=row["business_area__slug"],
                        dimension_type=dim_type,
                        dimension_value=dim_value,
                        total_usd=row["usd"] or 0,
                        total_qty=row["qty"] or 0,
                        payment_count=row["count"] or 0,
                        total_beneficiaries=row["beneficiaries"] or 0,
                        total_children=row["children"] or 0,
                        total_pwd=row["pwd"] or 0,
                    )
                )

                if len(batch) >= BULK_CREATE_BATCH_SIZE:
                    # Use ignore_conflicts=True to prevent crashing on race conditions
                    DailyAggregate.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []

            if batch:
                DailyAggregate.objects.bulk_create(batch, ignore_conflicts=True)
