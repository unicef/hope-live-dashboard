from django.http import HttpRequest

from .models import FinancialAggregate


def available_years(request: HttpRequest) -> dict[str, list[int]]:
    """Make the list of years with data available to all templates."""
    years = FinancialAggregate.objects.values_list("date__year", flat=True).distinct().order_by("-date__year")
    return {"available_years": list(years)}
