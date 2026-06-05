import logging
from typing import TYPE_CHECKING, Any

import channels.layers

from .consumers import GROUP

if TYPE_CHECKING:
    from streaming.types import JSON


logger = logging.getLogger(__name__)


async def notify_ui(msg: "JSON", *args: Any, **kwargs: Any) -> None:
    channel_layer = channels.layers.get_channel_layer()
    if channel_layer:
        await channel_layer.group_send(
            GROUP,
            {"type": "ui.message", "payload": msg},
        )
