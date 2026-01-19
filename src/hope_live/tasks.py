import logging
from typing import Any

from celery import shared_task
from django.db.models import Sum
from django.utils import timezone

from hope_live.models import BusinessArea, Payment
from hope_live.utils.cache import DashboardCache

logger = logging.getLogger(__name__)


@shared_task
def update_dashboard_cache() -> dict[str, Any]:
    try:
        DashboardCache.invalidate()
        logger.info("Dashboard cache invalidated.")

        payments = Payment.objects.all()

        successful_statuses = [
            "Distribution Successful",
            "Partially Distributed",
            "Transaction Successful",
        ]

        successful_payments = payments.filter(status__in=successful_statuses)
        total_delivered = successful_payments.aggregate(total=Sum("delivered_quantity_usd"))["total"] or 0

        logger.info(f"Dashboard cache updated. Total delivered: {total_delivered}")

        return {
            "total_delivered": float(total_delivered),
            "timestamp": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error updating dashboard cache: {e}")
        raise


@shared_task
def refresh_business_area_stats(business_area_slug: str) -> dict[str, Any] | None:
    try:
        DashboardCache.invalidate()

        business_area = BusinessArea.objects.get(slug=business_area_slug)

        payments = Payment.objects.filter(business_area=business_area)

        stats = {
            "business_area": business_area_slug,
            "total_payments": payments.count(),
            "successful_payments": payments.filter(
                status__in=["Distribution Successful", "Transaction Successful"]
            ).count(),
            "total_amount": payments.aggregate(total=Sum("delivered_quantity_usd"))["total"] or 0,
            "updated_at": timezone.now().isoformat(),
        }

        logger.info(f"Refreshed stats for {business_area_slug}: {stats}")
        return stats

    except BusinessArea.DoesNotExist:
        logger.error(f"Business area {business_area_slug} not found")
        return None
    except Exception as e:
        logger.error(f"Error refreshing stats for {business_area_slug}: {e}")
        raise
