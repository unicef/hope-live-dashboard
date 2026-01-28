from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from hope_live.analysis.tasks import refresh_daily_aggregates


class Command(BaseCommand):
    help = "Refreshes the daily aggregate statistics for the dashboard."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days back to refresh data for. Default is 30.",
        )
        parser.add_argument(
            "--async",
            action="store_true",
            help="Run the task asynchronously via Celery.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        days_back = options["days"]
        is_async = options["async"]

        self.stdout.write(f"Refreshing daily aggregates for the last {days_back} days...")

        if is_async:
            refresh_daily_aggregates.delay(days_back=days_back)
            self.stdout.write(self.style.SUCCESS("Successfully queued the refresh task to run in the background."))
        else:
            refresh_daily_aggregates(days_back=days_back)
            self.stdout.write(self.style.SUCCESS("Successfully refreshed daily aggregates."))
