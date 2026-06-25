from unittest.mock import AsyncMock, Mock, patch

import pytest

from hope_live.ws.utils import notify_ui


@pytest.mark.asyncio
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
async def test_notify_ui(message):
    mock_channel_layer = Mock()
    mock_channel_layer.group_send = AsyncMock()

    with patch("channels.layers.get_channel_layer", return_value=mock_channel_layer):
        await notify_ui(message)
        mock_channel_layer.group_send.assert_called_once_with("ALL", {"type": "ui.message", "payload": message})


@pytest.mark.asyncio
async def test_notify_ui_with_args_kwargs():
    mock_channel_layer = Mock()
    mock_channel_layer.group_send = AsyncMock()

    with patch("channels.layers.get_channel_layer", return_value=mock_channel_layer):
        test_message = {"type": "test.message", "data": {"key": "value"}}
        await notify_ui(test_message, "arg1", "arg2", extra="value")
        mock_channel_layer.group_send.assert_called_once_with("ALL", {"type": "ui.message", "payload": test_message})


@pytest.mark.asyncio
async def test_notify_ui_no_channel_layer():
    with patch("channels.layers.get_channel_layer", return_value=None):
        await notify_ui({"type": "test"})


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
