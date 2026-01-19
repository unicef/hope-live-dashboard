import json

import sentry_sdk
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from hope_live.utils.cache import DashboardCache
from hope_live.ws.utils import notify_ui


@csrf_exempt
def callback(request: HttpRequest) -> HttpResponse:
    try:
        payload = json.loads(request.body)

        DashboardCache.invalidate()

        notify_ui(payload)
        return HttpResponse()
    except json.decoder.JSONDecodeError as e:
        sentry_sdk.capture_exception(e)
        return HttpResponse(status=400)
