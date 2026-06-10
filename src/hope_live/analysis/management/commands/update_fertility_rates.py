import contextlib
import datetime
import json
import logging
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

import sentry_sdk
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update fertility rates from the World Bank API and write to fertility_rates.json"

    def handle(self, *args: Any, **options: Any) -> None:
        current_year = datetime.datetime.now().year
        start_year = 2020
        url = f"https://api.worldbank.org/v2/countries/all/indicators/SP.DYN.TFRT.IN?date={start_year}:{current_year}&format=json&per_page=2000"

        self.stdout.write(self.style.WARNING(f"Fetching fertility rates from World Bank API: {url}"))

        data = self._fetch_data(url)
        if not data:
            return

        output_list = self._parse_records(data)
        self._write_data(output_list)

    def _fetch_data(self, url: str) -> list[Any] | None:
        # Audit URL open for permitted schemes.
        if not url.lower().startswith(("http://", "https://")):
            raise ValueError(f"URL scheme not permitted: {url}")

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})  # noqa: S310
            with urllib.request.urlopen(req) as response:  # noqa: S310
                raw_content = response.read().decode()
                data = json.loads(raw_content)
        except Exception as e:  # noqa: BLE001
            sentry_sdk.capture_exception(e)
            return None

        min_response_length = 2
        if not isinstance(data, list) or len(data) < min_response_length:
            sentry_sdk.capture_message("Unexpected API response format for fertility rates")
            return None

        return data

    def _parse_records(self, data: list[Any]) -> list[dict[str, Any]]:
        records = data[1]
        country_data: dict[str, dict[str, float]] = defaultdict(dict)

        for record in records:
            iso3 = record.get("countryiso3code")
            if not iso3:
                continue
            iso3 = iso3.strip().upper()

            year = record.get("date")
            val = record.get("value")
            if val is not None:
                with contextlib.suppress(ValueError):
                    country_data[iso3][year] = float(val)

        # Sort countries alphabetically and years chronologically
        output_list = []
        for iso3 in sorted(country_data.keys()):
            years_dict = country_data[iso3]
            if not years_dict:
                continue

            entry: dict[str, Any] = {"Country Code": iso3}
            for yr in sorted(years_dict.keys()):
                entry[yr] = years_dict[yr]
            output_list.append(entry)

        return output_list

    def _write_data(self, output_list: list[dict[str, Any]]) -> None:
        # Write to fertility_rates.json
        rates_dir = Path(__file__).resolve().parent.parent.parent / "rates"
        rates_dir.mkdir(parents=True, exist_ok=True)
        file_path = rates_dir / "fertility_rates.json"

        try:
            with open(file_path, "w") as f:
                json.dump(output_list, f, indent=2)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated {len(output_list)} country fertility rates at {file_path}")
            )
        except Exception as e:  # noqa: BLE001
            sentry_sdk.capture_exception(e)
