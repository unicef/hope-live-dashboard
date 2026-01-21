import datetime
import json
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any
from urllib.parse import ParseResult, urlparse

import click
import django
import requests
from constance import config
from django.urls import reverse
from streaming.backends.rabbitmq import RabbitMQBackend
from streaming.manager import initialize_engine
from streaming.utils import make_event

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    django.setup()


def _validate_backend(backend: Any) -> None:
    if not isinstance(backend, RabbitMQBackend):
        raise click.ClickException("RabbitMQ backend is not configured. Please set BROKER_URL to a rabbit:// URL.")


def _get_notification_url(web_address: str) -> tuple[bool, str]:
    can_notify = False
    notification_url = "---"
    if web_address:
        parsed_url: ParseResult = urlparse(web_address)
        can_notify = bool(parsed_url.scheme and parsed_url.netloc)
        if can_notify:
            notification_url = f"{web_address}{reverse('ws:notify')}"
    return can_notify, notification_url


def _create_callback(
    notification_url: str,
) -> Callable[[str, "BlockingChannel", "Basic.Deliver", "BasicProperties", bytes], bool]:
    def callback(
        queue_name: str, ch: "BlockingChannel", method: "Basic.Deliver", properties: "BasicProperties", body: bytes
    ) -> bool:
        click.echo(f"web_address {notification_url}")
        click.echo(f"Received {body.decode()}")
        try:
            res = requests.post(notification_url, json=json.loads(body.decode()), timeout=2)
            if res.status_code != requests.codes.ok:
                raise requests.exceptions.RequestException("Request failed with status code: " + str(res.status_code))
            if method.delivery_tag is not None:
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except requests.exceptions.RequestException:
            if method.delivery_tag is not None:
                ch.basic_reject(method.delivery_tag, requeue=True)
        return True

    return callback


@cli.command()
@click.option("--name", default=None, help="Consumer name")
@click.option("--domain", default="", help="Domain name")
@click.option("--local", default=False, is_flag=True)
@click.option("--dry-run", default=False, is_flag=True)
@click.option("--address", default="")
def listen(name: str, domain: str, local: bool, address: str = "", dry_run: bool = False) -> None:
    manager = initialize_engine(True)
    backend = manager.backend

    _validate_backend(backend)

    web_address = address or config.SERVER_ADDRESS
    can_notify, notification_url = _get_notification_url(web_address)

    backend.connect()
    consume_message = not dry_run

    click.secho(f"Server   : {backend.host}:{backend.port}")
    click.secho(f"Listen on: {backend.exchange} {domain}")
    click.secho(f"Ack      : {consume_message}")

    if can_notify or local:
        click.secho(f"Url      : {notification_url}")
    else:
        click.secho("Server address is invalid. Live Notifications will not work. Aborting.", fg="red")
        click.get_current_context().exit()

    callback = _create_callback(notification_url)

    try:
        backend.listen(callback, [domain], ack=consume_message)
    except KeyboardInterrupt:
        click.secho("\nStopping listener.", fg="yellow")


@cli.command()
@click.option("--message", default="Test Message", help="Message to send")
@click.option("--domain", default="", help="Consumer name")
def send(message: str, domain: str) -> None:
    manager = initialize_engine(True)
    backend = manager.backend
    _validate_backend(backend)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    try:
        payload = json.loads(message)
    except json.decoder.JSONDecodeError:
        payload = {
            "timestamp": timestamp,
            "message": message,
        }
    msg = make_event(payload)
    click.secho(f"Server    : {backend.host}:{backend.port}")
    click.secho(f"Publish to: {backend.exchange} {domain}")

    backend.connect()
    backend.publish(domain, msg)
    click.secho(f"Sent: {msg}")
