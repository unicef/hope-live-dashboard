from hope_live.config.asgi import application


def test_asgi_application():
    assert application is not None
    assert callable(application)
    assert "http" in application.application_mapping
    assert "websocket" in application.application_mapping


def test_asgi_module_imports():
    import hope_live.config.asgi as asgi_module

    assert hasattr(asgi_module, "os")
    assert hasattr(asgi_module, "get_asgi_application")
    assert hasattr(asgi_module, "ProtocolTypeRouter")
    assert hasattr(asgi_module, "URLRouter")
    assert hasattr(asgi_module, "AuthMiddlewareStack")
    assert hasattr(asgi_module, "AllowedHostsOriginValidator")
    assert hasattr(asgi_module, "routing")


def test_asgi_application_structure():
    assert hasattr(application, "application_mapping")
    mapping = application.application_mapping
    assert isinstance(mapping, dict)
    assert "http" in mapping
    assert "websocket" in mapping


def test_asgi_environment():
    import hope_live.config.asgi as asgi_module

    assert "DJANGO_SETTINGS_MODULE" in asgi_module.os.environ
    assert asgi_module.os.environ["DJANGO_SETTINGS_MODULE"] == "hope_live.config.settings"
