from hope_live.ws.routing import websocket_urlpatterns


def test_routing_patterns():
    assert len(websocket_urlpatterns) == 1
    pattern = websocket_urlpatterns[0]
    assert pattern.pattern._regex == "listener/"
    assert pattern.callback is not None


def test_routing_module_imports():
    import hope_live.ws.routing as routing_module

    assert hasattr(routing_module, "re_path")
    assert hasattr(routing_module, "consumers")
    assert hasattr(routing_module, "websocket_urlpatterns")
    assert hasattr(routing_module, "app_name")


def test_websocket_urlpatterns_structure():
    pattern = websocket_urlpatterns[0]
    assert hasattr(pattern, "pattern")
    assert hasattr(pattern, "callback")
    assert hasattr(pattern, "default_args")
    assert pattern.callback is not None
