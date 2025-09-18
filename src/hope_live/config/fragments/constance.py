from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

from .. import env

CONSTANCE_REDIS_CONNECTION = env("CONSTANCE_REDIS_URL")
CONSTANCE_REDIS_CACHE_TIMEOUT = 1
CONSTANCE_ADDITIONAL_FIELDS = {
    **UNFOLD_CONSTANCE_ADDITIONAL_FIELDS,
    "group_select": [
        "hope_live.utils.constance.GroupChoiceField",
        {"initial": None},
    ],
}

CONSTANCE_DBS = ("default",)
