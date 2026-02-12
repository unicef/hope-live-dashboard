from unittest.mock import patch

import pytest
from django import forms
from django.contrib.auth.models import Group

from hope_live.utils.constance import (
    GroupChoiceField,
    ObfuscatedInput,
    WriteOnlyInput,
    WriteOnlyTextarea,
    WriteOnlyWidget,
)


def test_obfuscated_input_hides_values():
    widget = ObfuscatedInput()

    result_with_value = widget.render("secret_field", "actual_password", {})
    result_empty = widget.render("secret_field", "", {})
    result_none = widget.render("secret_field", None, {})

    assert "actual_password" not in result_with_value
    assert "Set" in result_with_value
    assert "Not Set" in result_empty
    assert "Not Set" in result_none


def test_write_only_widget_obfuscation_logic():
    widget = WriteOnlyWidget()

    assert widget.format_value("super_secret") == "***"
    assert widget.format_value(None) == "***"
    assert widget.format_value("") == "***"


def test_write_only_widget_config_retrieval():
    widget = WriteOnlyWidget()

    with patch("hope_live.utils.constance.config") as mock_config:
        mock_config.api_key = "original_key"

        unchanged_data = {"api_key": "***"}
        changed_data = {"api_key": "new_key"}

        assert widget.value_from_datadict(unchanged_data, None, "api_key") == "original_key"
        assert widget.value_from_datadict(changed_data, None, "api_key") == "new_key"


@pytest.mark.django_db
def test_group_choice_field_dynamic_choices():
    Group.objects.create(name="Admins")
    Group.objects.create(name="Users")
    Group.objects.create(name="Viewers")

    field = GroupChoiceField()

    assert len(field.choices) == 3
    assert ("Admins", "Admins") in field.choices
    assert ("Users", "Users") in field.choices
    assert ("Viewers", "Viewers") in field.choices


def test_write_only_widget_inheritance_hierarchy():
    textarea = WriteOnlyTextarea()
    textinput = WriteOnlyInput()

    assert isinstance(textarea, WriteOnlyWidget)
    assert isinstance(textarea, forms.Textarea)
    assert isinstance(textinput, WriteOnlyWidget)
    assert isinstance(textinput, forms.TextInput)

    assert hasattr(textarea, "value_from_datadict")
    assert hasattr(textinput, "value_from_datadict")
