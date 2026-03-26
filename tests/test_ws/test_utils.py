from unittest.mock import Mock, patch

import pytest

from hope_live.ws.utils import notify_ui


@pytest.mark.parametrize(
    "message",
    [
        {"type": "test.message", "data": {"key": "value"}},
        {"type": "simple"},
        {"type": "complex", "data": {"nested": "value"}},
        {"custom": "structure"},
        {},
    ],
)
def test_notify_ui(message):
    mock_channel_layer = Mock()
    mock_channel_layer.group_send = Mock()

    with patch("channels.layers.get_channel_layer", return_value=mock_channel_layer):
        with patch("hope_live.ws.utils.async_to_sync") as mock_async_to_sync:
            mock_wrapped = Mock()
            mock_async_to_sync.return_value = mock_wrapped

            notify_ui(message)

            mock_async_to_sync.assert_called_once()
            mock_wrapped.assert_called_once_with("ALL", {"type": "send.json", "payload": message})


def test_notify_ui_with_args_kwargs():
    mock_channel_layer = Mock()
    mock_channel_layer.group_send = Mock()

    with patch("channels.layers.get_channel_layer", return_value=mock_channel_layer):
        with patch("hope_live.ws.utils.async_to_sync") as mock_async_to_sync:
            mock_wrapped = Mock()
            mock_async_to_sync.return_value = mock_wrapped

            test_message = {"type": "test.message", "data": {"key": "value"}}

            notify_ui(test_message, "arg1", "arg2", extra="value")

            mock_wrapped.assert_called_once_with("ALL", {"type": "send.json", "payload": test_message})


def test_notify_ui_no_channel_layer():
    with patch("channels.layers.get_channel_layer", return_value=None):
        notify_ui({"type": "test"})


def test_notify_ui_function_signature():
    import inspect

    from hope_live.ws.utils import notify_ui

    assert callable(notify_ui)
    sig = inspect.signature(notify_ui)
    params = list(sig.parameters.keys())
    assert "msg" in params
    assert "args" in params
    assert "kwargs" in params


def test_notify_ui_module_imports():
    from hope_live.ws.utils import logger

    assert logger is not None
    assert logger.name == "hope_live.ws.utils"
