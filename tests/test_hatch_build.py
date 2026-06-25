from unittest.mock import MagicMock, patch

from hatch_build import CustomBuildHook


@patch("hatch_build.Path")
def test_custom_build_hook_initialize_no_locale_dir(mock_path_cls):
    # Setup mock where locale directory does not exist
    mock_locale_dir = MagicMock()
    mock_locale_dir.exists.return_value = False

    # Chain mock for Path(__file__).parent / "src" / "hope_live" / "locale"
    mock_path_cls.return_value.parent.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = (
        mock_locale_dir
    )

    hook = CustomBuildHook(
        root="/tmp",
        config={},
        build_config=MagicMock(),
        metadata=MagicMock(),
        directory="/tmp",
        target_name="wheel",
    )

    hook.initialize("0.1.0", {})

    mock_locale_dir.exists.assert_called_once()
    mock_locale_dir.glob.assert_not_called()


@patch("hatch_build.polib")
@patch("hatch_build.Path")
def test_custom_build_hook_initialize_compiles_po(mock_path_cls, mock_polib):
    # Setup mock where locale directory exists and has a po file
    mock_locale_dir = MagicMock()
    mock_locale_dir.exists.return_value = True

    mock_po_file = MagicMock()
    mock_locale_dir.glob.return_value = [mock_po_file]

    # Chain mock for Path(__file__).parent / "src" / "hope_live" / "locale"
    mock_path_cls.return_value.parent.__truediv__.return_value.__truediv__.return_value.__truediv__.return_value = (
        mock_locale_dir
    )

    mock_mo_path = MagicMock()
    mock_po_file.with_name.return_value = mock_mo_path

    mock_po_object = MagicMock()
    mock_polib.pofile.return_value = mock_po_object

    hook = CustomBuildHook(
        root="/tmp",
        config={},
        build_config=MagicMock(),
        metadata=MagicMock(),
        directory="/tmp",
        target_name="wheel",
    )

    hook.initialize("0.1.0", {})

    mock_polib.pofile.assert_called_once_with(str(mock_po_file))
    mock_po_object.save_as_mofile.assert_called_once_with(str(mock_mo_path))
