import datetime
import json
import logging
from typing import TYPE_CHECKING
from urllib.parse import ParseResult, urlparse

import click
import requests
from constance import config
from django.urls import reverse
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from streaming.utils import make_event

if TYPE_CHECKING:
    from streaming.types import EventType

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """HOPE live dashboard."""
    import django

    django.setup()


@cli.command()
@click.option("--name", default=None, help="Consumer name")
@click.option("--domain", default="", help="Domain name")
@click.option("--local", default=False, is_flag=True)
@click.option("--address", default="")
def listen(name: str, domain: str, local: bool, address: str = "") -> None:
    from streaming.backends.rabbitmq import RabbitMQBackend
    from streaming.manager import initialize_engine

    manager = initialize_engine(True)
    backend = manager.backend

    if not isinstance(backend, RabbitMQBackend):
        raise click.ClickException("RabbitMQ backend is not configured. Please set BROKER_URL to a rabbit:// URL.")

    web_address = address or config.SERVER_ADDRESS
    can_notify = False
    notification_url = "---"
    if web_address:
        parsed_url: ParseResult = urlparse(web_address)
        if not (parsed_url.scheme and parsed_url.netloc):
            can_notify = False
        else:
            can_notify = True
            notification_url = f"{web_address}{reverse('ws:notify')}"
    backend.connection_name = web_address
    backend.connect()

    click.secho(f"Server   : {backend.host}:{backend.port}")
    click.secho(f"Consumer : {backend.connection_name}")
    click.secho(f"Listen on: {backend.exchange} {domain}")

    if can_notify or local:
        click.secho(f"Url      : {notification_url}")
    else:
        click.secho("Server address is invalid. Live Notifications will not work. Aborting.", fg="red")
        click.get_current_context().exit()

    def callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        click.echo(f"web_address {notification_url}")
        click.echo(f"Received {body.decode()}")
        requests.post(notification_url, json=json.loads(body.decode()), timeout=2)

    try:
        backend.listen([domain], callback, ack=not local)
    except KeyboardInterrupt:
        click.secho("\nStopping listener.", fg="yellow")
    finally:
        if backend.connection and backend.connection.is_open:
            backend.connection.close()


@cli.command()
@click.option("--message", default="Test Message", help="Message to send")
@click.option("--domain", default="", help="Consumer name")
def send(message: str, domain: str) -> None:
    from streaming.backends.rabbitmq import RabbitMQBackend
    from streaming.manager import initialize_engine

    manager = initialize_engine(True)

    backend = manager.backend
    if not isinstance(backend, RabbitMQBackend):
        raise click.ClickException("RabbitMQ backend is not configured. Please set BROKER_URL to a rabbit:// URL.")

    backend.connection_name = "sender"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    try:
        payload = json.loads(message)
    except json.decoder.JSONDecodeError:
        payload = {
            "timestamp": timestamp,
            "message": message,
        }
    msg: EventType = make_event(payload, event="Test", domain=domain)
    click.secho(f"Server    : {backend.host}:{backend.port}")
    click.secho(f"Publish to: {backend.exchange} {domain}")
    backend.connect()
    backend.publish(msg)
    click.secho(f"Sent: {msg}")
    backend.connection.close()  # type: ignore[union-attr]
