import json
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from hope_live.ws.consumers import HopeConsumer


@pytest.mark.asyncio
async def test_hope_consumer_connect_disconnect_receive():
    consumer = HopeConsumer()
    consumer.base_send = AsyncMock()
    consumer.channel_layer = MagicMock()
    consumer.channel_layer.group_add = AsyncMock()
    consumer.channel_layer.group_discard = AsyncMock()
    consumer.channel_name = "test_channel"

    await consumer.connect()
    consumer.channel_layer.group_add.assert_called_once_with(ANY, "test_channel")
    consumer.base_send.assert_any_call({"type": "websocket.accept", "subprotocol": None})

    if hasattr(consumer, "receive"):
        await consumer.receive(text_data=json.dumps({"message": "hello"}))

    if hasattr(consumer, "disconnect"):
        await consumer.disconnect(1000)
