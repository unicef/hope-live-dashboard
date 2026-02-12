from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from hope_live.__cli__ import RabbitMQBackend, cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_group(runner):
    with patch("django.setup"):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "HOPE live dashboard" in result.output


@patch("hope_live.__cli__.initialize_engine")
def test_listen_command_dry_run(mock_initialize_engine, runner):
    mock_backend = Mock(spec=RabbitMQBackend)
    mock_backend.host = "localhost"
    mock_backend.port = 5672
    mock_backend.client_name = ""
    mock_backend.exchange = "test_exchange"
    mock_backend._connection = Mock()
    mock_backend._connection.is_open = False
    mock_manager = Mock()
    mock_manager.backend = mock_backend
    mock_initialize_engine.return_value = mock_manager

    result = runner.invoke(cli, ["listen", "--dry-run", "--address", "http://localhost:8000"])
    assert result.exit_code == 0
    assert "Server   : localhost:5672" in result.output
    assert "Ack      : False" in result.output


@patch("hope_live.__cli__.initialize_engine")
def test_send_command(mock_initialize_engine, runner):
    mock_backend = Mock(spec=RabbitMQBackend)
    mock_backend.host = "localhost"
    mock_backend.port = 5672
    mock_backend.exchange = "test_exchange"
    mock_backend.client_name = "sender"

    mock_manager = Mock()
    mock_manager.backend = mock_backend
    mock_initialize_engine.return_value = mock_manager

    result = runner.invoke(cli, ["send", "--message", '{"test": "data"}', "--domain", "test"])
    assert result.exit_code == 0
    assert "Server    : localhost:5672" in result.output
    assert "Publish to: test_exchange test" in result.output


@patch("hope_live.__cli__.initialize_engine")
def test_send_command_invalid_json(mock_initialize_engine, runner):
    mock_backend = Mock(spec=RabbitMQBackend)
    mock_backend.host = "localhost"
    mock_backend.port = 5672
    mock_backend.exchange = "test_exchange"
    mock_backend.client_name = "sender"

    mock_manager = Mock()
    mock_manager.backend = mock_backend
    mock_initialize_engine.return_value = mock_manager

    result = runner.invoke(cli, ["send", "--message", "plain text", "--domain", "test"])
    assert result.exit_code == 0
    assert "plain text" in result.output


def test_cli_module_imports():
    import hope_live.__cli__ as cli_module

    assert hasattr(cli_module, "datetime")
    assert hasattr(cli_module, "json")
    assert hasattr(cli_module, "logging")
    assert hasattr(cli_module, "click")
    assert hasattr(cli_module, "requests")
    assert hasattr(cli_module, "config")
    assert hasattr(cli_module, "reverse")
    assert hasattr(cli_module, "RabbitMQBackend")
    assert hasattr(cli_module, "initialize_engine")
    assert hasattr(cli_module, "make_event")
    assert hasattr(cli_module, "cli")
