from unittest.mock import AsyncMock, patch

from hope_live.ws.utils import notify_ui


def test_notify_ui():
    with patch("hope_live.ws.utils.channels.layers.get_channel_layer") as mock_get_layer:
        mock_layer = mock_get_layer.return_value
        mock_layer.group_send = AsyncMock()

        notify_ui({"key": "value"})

        mock_layer.group_send.assert_called_once()
        call_args = mock_layer.group_send.call_args
        assert call_args[0][0] == "ALL"
        assert call_args[0][1]["type"] == "send.json"
        assert call_args[0][1]["payload"] == {"key": "value"}
