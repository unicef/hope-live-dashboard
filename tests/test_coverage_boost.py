import importlib
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from django.conf import settings
from streaming.backends.rabbitmq import RabbitMQBackend

from hope_live.__cli__ import cli
from hope_live.models import Office


@pytest.mark.django_db
def test_base_queryset_get_does_not_exist():
    """Test that BaseQuerySet.get raises the custom DoesNotExist exception."""
    with pytest.raises(Office.DoesNotExist) as exc:
        Office.objects.get(id=99999)
    assert "matching query does not exist" in str(exc.value)


@pytest.mark.django_db
@patch("hope_live.models.base.reverse")
def test_base_model_get_change_url(mock_reverse, office_factory):
    """Test that BaseModel.get_change_url returns the correct admin URL."""
    office = office_factory()
    mock_reverse.return_value = "/admin/hope_live/office/1/change/"
    url = office.get_change_url(namespace="admin")
    mock_reverse.assert_called_once_with(
        f"admin:{office._meta.app_label}_{office._meta.model_name}_change", args=[office.pk]
    )
    assert url == "/admin/hope_live/office/1/change/"


def test_urls_debug_true(monkeypatch):
    """Test urls.py when DEBUG is True and browser reload is in middleware."""
    monkeypatch.setattr(settings, "DEBUG", True)
    monkeypatch.setattr(
        settings, "MIDDLEWARE", list(settings.MIDDLEWARE) + ["django_browser_reload.middleware.BrowserReloadMiddleware"]
    )
    import hope_live.config.urls

    importlib.reload(hope_live.config.urls)

    # Verify the reload URL was added
    assert any(getattr(p.pattern, "_route", None) == "__reload__/" for p in hope_live.config.urls.urlpatterns)


def test_cli_listen_callback():
    """Test the inner callback function of the listen command."""
    runner = CliRunner()

    with patch("hope_live.__cli__.initialize_engine") as mock_init:
        mock_backend = MagicMock()
        mock_backend.__class__ = RabbitMQBackend
        mock_backend.host = "localhost"
        mock_backend.port = 5672
        mock_backend.exchange = "test"
        mock_init.return_value.backend = mock_backend

        # Capture the callback function when listen is called
        callback_func = None

        def capture_listen(cb, domains, ack):
            nonlocal callback_func
            callback_func = cb

        mock_backend.listen.side_effect = capture_listen

        runner.invoke(cli, ["listen", "--address", "http://localhost:8000"])

        assert callback_func is not None

        # Test the callback execution
        mock_ch = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        with patch("hope_live.__cli__.requests.post") as mock_post:
            # Success case
            mock_post.return_value.status_code = 200
            res = callback_func("queue", mock_ch, mock_method, None, b'{"test": "data"}')
            assert res is True
            mock_ch.basic_ack.assert_called_once_with(delivery_tag=1)

            # Failure case
            mock_ch.reset_mock()
            mock_post.return_value.status_code = 500
            res = callback_func("queue", mock_ch, mock_method, None, b'{"test": "data"}')
            assert res is True
            mock_ch.basic_reject.assert_called_once_with(1, requeue=True)


def test_cli_listen_keyboard_interrupt():
    """Test KeyboardInterrupt handling in listen command."""
    runner = CliRunner()
    with patch("hope_live.__cli__.initialize_engine") as mock_init:
        mock_backend = MagicMock()
        mock_backend.__class__ = RabbitMQBackend
        mock_backend._connection.is_open = True
        mock_init.return_value.backend = mock_backend

        mock_backend.listen.side_effect = KeyboardInterrupt()

        result = runner.invoke(cli, ["listen", "--local"])
        assert "Stopping listener" in result.output
        mock_backend.disconnect.assert_called_once()


def test_cli_send_invalid_backend():
    """Test send command with invalid backend."""
    runner = CliRunner()
    with patch("hope_live.__cli__.initialize_engine") as mock_init:
        mock_init.return_value.backend = object()  # Not a RabbitMQBackend

        result = runner.invoke(cli, ["send"])
        assert result.exit_code != 0
        assert "RabbitMQ backend is not configured" in result.output
