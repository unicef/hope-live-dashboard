from django.conf import settings

from .. import env

CONSTANCE_REDIS_CONNECTION = env("CONSTANCE_REDIS_URL") or "redis://127.0.0.1:6379/1"
CONSTANCE_REDIS_CACHE_TIMEOUT = 1
CONSTANCE_ADDITIONAL_FIELDS = {
    "group_select": [
        "hope_live.utils.constance.GroupChoiceField",
        {"initial": None, "required": False},
    ],
    "password": [
        "django.forms.fields.CharField",
        {
            "widget": "hope_live.utils.constance.ObfuscatedInput",
            "required": False,
        },
    ],
    "token": [
        "django.forms.fields.CharField",
        {
            "widget": "hope_live.utils.constance.WriteOnlyInput",
            "required": False,
        },
    ],
}

CONSTANCE_DBS = ("default",)

addr = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else ""  # type: ignore[has-type]

CONSTANCE_CONFIG = {
    "NEW_USER_DEFAULT_GROUP": (
        None,
        "Group to assign to any new user",
        "group_select",
    ),
    "SERVER_ADDRESS": (addr, "Public DNS address of this instance (https://<server>:<port>)", str),
    "ROUTING_KEY": (
        "",
        "Secret Key used for internal event notifications",
        "token",
    ),
    "HOPE_COUNTRY_REPORT_API_URL": (
        "https://reporting-hope-dev.unitst.org/api/",
        "Country Report API URL",
        str,
    ),
    "HOPE_COUNTRY_REPORT_API_TOKEN": (
        "8ac98d372760c5db87b73e1c283dcb1bc8c4f0e6",
        "Country Report API Token",
        "token",
    ),
    "HOPE_COUNTRY_REPORT_QUERY_ID": (
        6,
        "Query ID for Country Report Aggregate Dataset",
        int,
    ),
    "HOPE_FINANCIAL_REPORT_QUERY_ID": (
        6,
        "Query ID for Financial Aggregate Dataset",
        int,
    ),
    "HOPE_DEMOGRAPHIC_REPORT_QUERY_ID": (
        7,
        "Query ID for Demographic Aggregate Dataset",
        int,
    ),
    "HOPE_COMPLETION_REPORT_QUERY_ID": (
        8,
        "Query ID for Completion Aggregate Dataset",
        int,
    ),
    "HOPE_GRIEVANCE_REPORT_QUERY_ID": (
        9,
        "Query ID for Grievance Aggregate Dataset",
        int,
    ),
    "HOPE_RISK_REPORT_QUERY_ID": (
        10,
        "Query ID for Risk Aggregate Dataset",
        int,
    ),
    "HOPE_NEWS_REPORT_QUERY_ID": (
        159,
        "Query ID for News Updates/Alerts Dataset",
        int,
    ),
}
