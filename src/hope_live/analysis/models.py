from django.db import models
from django_celery_boost.models import AsyncJobModel


class DailyAggregate(models.Model):
    """
    Stores pre-calculated totals per day, per country, per dimension.

    Synced from Country Report.
    """

    date = models.DateField(db_index=True)
    country_slug = models.CharField(max_length=100, db_index=True)
    dimension_type = models.CharField(max_length=50, db_index=True)
    dimension_value = models.CharField(max_length=255, db_index=True)

    total_usd = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_qty = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    payment_count = models.IntegerField(default=0)
    total_beneficiaries = models.IntegerField(default=0)
    total_children = models.IntegerField(default=0)
    total_pwd = models.IntegerField(default=0)

    class Meta:
        unique_together = ("date", "country_slug", "dimension_type", "dimension_value")
        indexes = [
            models.Index(fields=["dimension_type", "date"]),
            models.Index(fields=["country_slug", "dimension_type"]),
            models.Index(fields=["dimension_type", "country_slug", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.date} {self.country_slug} {self.dimension_type}:{self.dimension_value}"


class SyncDailyAggregatesJob(AsyncJobModel):
    default_celery_task_name = "hope_live.analysis.tasks.sync_daily_aggregates"
    celery_task_name = "hope_live.analysis.tasks.sync_daily_aggregates"

    class Meta(AsyncJobModel.Meta):
        verbose_name = "Sync Daily Aggregates Job"
        verbose_name_plural = "Sync Daily Aggregates Jobs"
