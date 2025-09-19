import json
from typing import Any

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

GROUP = "ALL"


class HopeConsumer(JsonWebsocketConsumer):
    def connect(self) -> None:
        async_to_sync(self.channel_layer.group_add)(GROUP, self.channel_name)
        self.accept()
        self.send(text_data=json.dumps({"message": f"Connected via {self.channel_name}"}))

    def disconnect(self, close_code: int) -> None:
        async_to_sync(self.channel_layer.group_discard)(GROUP, self.channel_name)

    def receive(self, text_data: str | None = None, bytes_data: bytes | None = None, **kwargs: Any) -> None:
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            self.send(text_data=json.dumps({"message": message}))
