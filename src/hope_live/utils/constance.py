import logging
from collections.abc import Mapping
from typing import Any

from constance import config
from django.contrib.auth.models import Group
from django.forms import ChoiceField, HiddenInput, TextInput, Textarea, Widget
from django.template import Context, Template
from django.utils.safestring import SafeString, mark_safe

logger = logging.getLogger(__name__)


class ObfuscatedInput(HiddenInput):
    def render(
        self,
        name: str,
        value: Any,
        attrs: dict[str, str] | None = None,
        renderer: Any | None = None,
    ) -> "SafeString":
        context = self.get_context(name, value, attrs)
        context["value"] = str(value)
        context["label"] = "Set" if value else "Not Set"

        tpl = Template('<input type="hidden" name="{{ widget.name }}" value="{{ value }}">{{ label }}')
        return mark_safe(tpl.render(Context(context)))  # noqa: S308


class WriteOnlyWidget(Widget):
    def format_value(self, value: Any) -> str | None:
        return super().format_value("***")

    def value_from_datadict(self, data: Mapping[str, Any], files: Any, name: str) -> Any:
        value = data.get(name)
        if value == "***":
            return getattr(config, name)
        return value


class WriteOnlyTextarea(WriteOnlyWidget, Textarea):
    pass


class WriteOnlyInput(WriteOnlyWidget, TextInput):
    pass


class GroupChoiceField(ChoiceField):
    def __init__(self, **kwargs: Any) -> None:
        ret: list[tuple[str | int, str]] = [(c["name"], c["name"]) for c in Group.objects.values("pk", "name")]
        kwargs["choices"] = ret
        super().__init__(**kwargs)
