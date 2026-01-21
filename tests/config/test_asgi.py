from hope_live.config import asgi


def test_asgi_application():
    assert asgi.application is not None
