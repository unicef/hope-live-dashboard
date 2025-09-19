from django.urls import re_path

from hope_live.ws import consumers

app_name = "ws"


websocket_urlpatterns = [
    re_path("listener/", consumers.HopeConsumer.as_asgi()),  # type: ignore[arg-type]
]
