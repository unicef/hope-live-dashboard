from unittest.mock import MagicMock, patch

import click
import pytest
from click.testing import CliRunner
from streaming.backends.rabbitmq import RabbitMQBackend

from hope_live.__cli__ import _create_callback, _get_notification_url, _validate_backend, cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "listen" in result.output
    assert "send" in result.output


def test_cli_send():
    runner = CliRunner()
    with patch("hope_live.__cli__.initialize_engine") as mock_init:
        mock_backend = MagicMock(spec=RabbitMQBackend)
        mock_backend.host = "localhost"
        mock_backend.port = 5672
        mock_backend.exchange = "test_exchange"
        mock_init.return_value.backend = mock_backend

        result = runner.invoke(cli, ["send", "--message", "test", "--domain", "test_domain"])

        assert result.exit_code == 0
        mock_backend.connect.assert_called_once()
        mock_backend.publish.assert_called_once()
        assert "Sent:" in result.output


def test_cli_listen():
    runner = CliRunner()
    with patch("hope_live.__cli__.initialize_engine") as mock_init:
        mock_backend = MagicMock(spec=RabbitMQBackend)
        mock_backend.host = "localhost"
        mock_backend.port = 5672
        mock_backend.exchange = "test_exchange"
        mock_init.return_value.backend = mock_backend

        mock_backend.listen.side_effect = KeyboardInterrupt()

        result = runner.invoke(cli, ["listen", "--name", "test", "--domain", "test_domain", "--local"])

        assert result.exit_code == 0
        mock_backend.connect.assert_called_once()
        mock_backend.listen.assert_called_once()
        assert "Stopping listener" in result.output


def test_validate_backend_invalid():
    with pytest.raises(click.ClickException):
        _validate_backend(MagicMock())


def test_get_notification_url_valid():
    can_notify, url = _get_notification_url("http://localhost:8000")
    assert can_notify is True
    assert "http://localhost:8000" in url
    assert "/ws/notify" in url


def test_get_notification_url_invalid():
    can_notify, url = _get_notification_url("")
    assert can_notify is False
    assert url == "---"


def test_callback_success():
    callback = _create_callback("http://example.com")
    mock_ch = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200

        result = callback("queue", mock_ch, mock_method, MagicMock(), b'{"key": "value"}')

        assert result is True
        mock_ch.basic_ack.assert_called_with(delivery_tag=1)


def test_callback_failure():
    callback = _create_callback("http://example.com")
    mock_ch = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 500

        result = callback("queue", mock_ch, mock_method, MagicMock(), b'{"key": "value"}')

        assert result is True
        mock_ch.basic_reject.assert_called_with(1, requeue=True)
