from unittest.mock import patch

from hope_live.config.celery import app, debug_task


def test_celery_app():
    assert app is not None
    assert hasattr(app, "task")
    assert app.main == "hope_live"
    assert hasattr(app, "config_from_object")
    assert hasattr(app, "autodiscover_tasks")


def test_celery_app_config():
    assert app.conf.task_serializer == "json"
    assert app.conf.accept_content == ("json",)
    assert app.conf.result_serializer == "json"
    assert app.conf.timezone == "UTC"
    assert app.conf.enable_utc is True


def test_debug_task():
    with patch("hope_live.config.celery.logger") as mock_logger:
        debug_task.apply(task_id="test-id-123")

        assert mock_logger.info.called
        log_msg = mock_logger.info.call_args[0][0]
        assert "test-id-123" in log_msg


def test_debug_task_with_different_request():
    with patch("hope_live.config.celery.logger") as mock_logger:
        debug_task.apply(task_id="another-id", delivery_info={"routing_key": "test"})

        assert mock_logger.info.called
        log_msg = mock_logger.info.call_args[0][0]
        assert "another-id" in log_msg


def test_celery_module_imports():
    import hope_live.config.celery as celery_module

    assert hasattr(celery_module, "os")
    assert hasattr(celery_module, "logging")
    assert hasattr(celery_module, "Celery")
    assert hasattr(celery_module, "app")
    assert hasattr(celery_module, "debug_task")
    assert hasattr(celery_module, "logger")


def test_celery_app_autodiscover():
    app.autodiscover_tasks(packages=["hope_live.analysis"], force=True)
    assert "hope_live.analysis.tasks.sync_daily_aggregates" in app.tasks


def test_celery_app_namespace():
    assert hasattr(app.conf, "task_serializer")
    assert hasattr(app.conf, "timezone")


def test_debug_task_decorator():
    assert callable(debug_task)
    assert hasattr(debug_task, "__wrapped__")
    assert debug_task.__name__ == "debug_task"
