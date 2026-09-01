from django.db import models
from django_celery_boost.models import CeleryTaskModel


class TimeGrain(models.TextChoices):
    DAILY = "daily", "Daily"
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


class BaseAggregate(models.Model):
    """
    Abstract base model for all dashboard aggregates.

    Includes time grain to support explicit pre-aggregated rollups.
    """

    date = models.DateField(db_index=True)
    time_grain = models.CharField(
        max_length=10,
        choices=TimeGrain.choices,
        default=TimeGrain.DAILY,
        db_index=True,
    )
    country_slug = models.CharField(max_length=100, db_index=True)
    dimension_type = models.CharField(max_length=50, db_index=True)
    dimension_value = models.CharField(max_length=255, db_index=True)

    class Meta:
        abstract = True
        unique_together = ("date", "time_grain", "country_slug", "dimension_type", "dimension_value")
        indexes = [
            models.Index(fields=["dimension_type", "date"]),
            models.Index(fields=["country_slug", "dimension_type"]),
            models.Index(fields=["dimension_type", "country_slug", "date", "time_grain"]),
        ]

    def __str__(self) -> str:
        return f"{self.date} ({self.time_grain}) {self.country_slug} {self.dimension_type}:{self.dimension_value}"


class FinancialAggregate(BaseAggregate):
    total_usd = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_qty = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    payment_count = models.IntegerField(default=0)


class DemographicAggregate(BaseAggregate):
    total_beneficiaries = models.IntegerField(default=0)
    total_children = models.IntegerField(default=0)
    total_pwd = models.IntegerField(default=0)
    total_households = models.IntegerField(default=0)


class CompletionAggregate(BaseAggregate):
    payment_count = models.IntegerField(default=0)
    total_usd = models.DecimalField(max_digits=20, decimal_places=2, default=0)


class GrievanceAggregate(BaseAggregate):
    ticket_count = models.IntegerField(default=0)


class RiskSeverity(models.TextChoices):
    CRITICAL = "critical", "Critical"
    WARNING = "warning", "Warning"
    CAUTION = "caution", "Caution"
    NORMAL = "normal", "Normal"


class RiskTrend(models.TextChoices):
    UP = "up", "Increasing"
    DOWN = "down", "Decreasing"
    NEUTRAL = "neutral", "Neutral"


class RiskAggregate(BaseAggregate):
    """Stores risk indicators aggregated across modules, countries, and time grains."""

    module = models.CharField(max_length=50, db_index=True)
    risk_code = models.CharField(max_length=100, db_index=True)
    risk_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

    issue_count = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    unit_label = models.CharField(max_length=50, default="payments")

    severity = models.CharField(max_length=20, choices=RiskSeverity.choices, default=RiskSeverity.NORMAL, db_index=True)
    trend = models.CharField(max_length=20, choices=RiskTrend.choices, default=RiskTrend.NEUTRAL)
    threshold_info = models.CharField(max_length=255, blank=True, default="")
    is_visible_on_dashboard = models.BooleanField(default=True)

    class Meta(BaseAggregate.Meta):
        verbose_name = "Risk Aggregate"
        verbose_name_plural = "Risk Aggregates"
        indexes = [
            *BaseAggregate.Meta.indexes,
            models.Index(fields=["module", "severity"]),
            models.Index(fields=["risk_code", "date"]),
        ]


class SyncDailyAggregatesJob(CeleryTaskModel):  # type: ignore[misc]
    default_celery_task_name = "hope_live.analysis.tasks.sync_daily_aggregates"
    celery_task_name = "hope_live.analysis.tasks.sync_daily_aggregates"

    error_message = models.TextField(blank=True, default="")

    class Meta(CeleryTaskModel.Meta):  # type: ignore[misc]
        verbose_name = "Sync Daily Aggregates Job"
        verbose_name_plural = "Sync Daily Aggregates Jobs"
