from django.urls import path

from . import views

app_name = "analysis_api"

urlpatterns = [
    path("daily-aggregates/", views.AggregateListView.as_view(), name="daily-aggregates-list"),
]
