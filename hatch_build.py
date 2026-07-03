# ruff: noqa
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import polib


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict) -> None:
        locale_dir = Path(__file__).parent / "src" / "hope_live" / "locale"
        if not locale_dir.exists():
            return

        po_files = list(locale_dir.glob("**/*.po"))
        for po_path in po_files:
            mo_path = po_path.with_suffix(".mo")
            po = polib.pofile(str(po_path))
            po.save_as_mofile(str(mo_path))
