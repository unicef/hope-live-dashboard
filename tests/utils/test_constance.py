from testutils.factories import GroupFactory

from hope_live.utils.constance import GroupChoiceField, ObfuscatedInput, WriteOnlyInput, WriteOnlyTextarea


def test_obfuscated_input_render():
    widget = ObfuscatedInput()
    output = widget.render("test", "secret")
    assert 'type="hidden"' in output
    assert 'value="secret"' in output
    assert "Set" in output


def test_write_only_input():
    widget = WriteOnlyInput()
    assert widget.format_value("secret") == "***"
    assert widget.value_from_datadict({"name": "new_value"}, {}, "name") == "new_value"
    # assert widget.value_from_datadict({"name": "***"}, {}, "name") == ...


def test_write_only_textarea():
    widget = WriteOnlyTextarea()
    assert widget.format_value("secret") == "***"


def test_group_choice_field(db):
    GroupFactory(name="Group A")
    GroupFactory(name="Group B")

    field = GroupChoiceField()
    choices = dict(field.choices)

    assert "Group A" in choices
    assert "Group B" in choices
    assert choices["Group A"] == "Group A"
