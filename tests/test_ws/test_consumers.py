import json
from unittest.mock import MagicMock, patch

from hope_live.ws.consumers import HopeConsumer


def test_hope_consumer_connect_disconnect_receive():
    consumer = HopeConsumer()
    consumer.channel_layer = MagicMock()
    consumer.channel_name = "test_channel"
    consumer.accept = MagicMock()
    consumer.send = MagicMock()

    with patch("hope_live.ws.consumers.async_to_sync") as mock_async_to_sync:
        consumer.connect()
        mock_async_to_sync.assert_called_with(consumer.channel_layer.group_add)
        consumer.accept.assert_called_once()
        consumer.send.assert_called_with(text_data=json.dumps({"message": "Connected via test_channel"}))

        consumer.receive(text_data=json.dumps({"message": "hello"}))
        consumer.send.assert_called_with(text_data=json.dumps({"message": "hello"}))

        consumer.disconnect(1000)
        mock_async_to_sync.assert_called_with(consumer.channel_layer.group_discard)
