import pytest
from channels.testing import WebsocketCommunicator

from hope_live.ws.consumers import HopeConsumer


@pytest.mark.asyncio
async def test_hope_consumer_connect():
    communicator = WebsocketCommunicator(HopeConsumer.as_asgi(), "/ws/listener/")
    connected, subprotocol = await communicator.connect()
    assert connected
    response = await communicator.receive_json_from()
    assert response["message"].startswith("Connected via")
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_hope_consumer_receive():
    communicator = WebsocketCommunicator(HopeConsumer.as_asgi(), "/ws/listener/")
    await communicator.connect()
    await communicator.receive_json_from()

    await communicator.send_json_to({"message": "hello"})
    response = await communicator.receive_json_from()
    assert response == {"message": "hello"}
    await communicator.disconnect()
