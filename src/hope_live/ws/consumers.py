from typing import Any

from channels.generic.websocket import AsyncJsonWebsocketConsumer

GROUP = "ALL"


class HopeConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self) -> None:
        await self.channel_layer.group_add(GROUP, self.channel_name)
        await self.accept()
        await self.send_json({"message": f"Connected via {self.channel_name}"})

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(GROUP, self.channel_name)

    async def receive_json(self, content: dict[str, Any], **kwargs: Any) -> None:
        message = content.get("message", "")
        await self.send_json({"message": message})

    async def ui_message(self, event: dict[str, Any]) -> None:
        await self.send_json(event["payload"])
