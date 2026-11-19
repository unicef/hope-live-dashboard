import re
from pathlib import Path

import pytest

from hope_live.templatetags.icon_names import ICON_NAMES
from hope_live.templatetags.icons import icon

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = REPO_ROOT / "src" / "hope_live" / "templates"
ICON_ROOT = REPO_ROOT / "src" / "hope_live" / "theme" / "icons"
PUBLIC_TEMPLATES = [
    TEMPLATE_ROOT / "public_layout.html",
    TEMPLATE_ROOT / "pages" / "landing.html",
]


def test_every_icon_used_in_public_templates_is_registered():
    used = set()
    for path in PUBLIC_TEMPLATES:
        used.update(re.findall(r'{%\s*icon\s+"([^"]+)"', path.read_text()))

    assert used
    assert used <= ICON_NAMES


def test_every_registered_icon_has_a_sprite_symbol():
    sprite = (TEMPLATE_ROOT / "includes" / "icons_sprite.html").read_text()
    symbols = set(re.findall(r'<symbol id="icon-([^"]+)"', sprite))

    assert symbols == ICON_NAMES


def test_icon_tag_renders_a_sprite_reference():
    rendered = str(icon("baby", "h-4 w-4"))

    assert 'href="#icon-baby"' in rendered
    assert 'aria-hidden="true"' in rendered
    assert 'class="h-4 w-4"' in rendered


def test_unknown_icon_raises():
    with pytest.raises(ValueError, match="Unknown icon"):
        icon("does-not-exist")


def test_source_icons_keep_the_shared_grid_and_current_colour():
    for path in ICON_ROOT.glob("*.svg"):
        root = re.search(r"<svg\b[^>]*>", path.read_text())
        assert root is not None, path
        tag = root.group(0)
        assert 'viewBox="0 0 24 24"' in tag, path
        assert "currentColor" in tag, path
        assert not re.search(r'<svg\b[^>]*\swidth="', tag), path
        assert not re.search(r'<svg\b[^>]*\sheight="', tag), path
