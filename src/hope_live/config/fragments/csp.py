from .. import env

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["data:", "'self'", "'unsafe-inline'"] + env("CSP_DEFAULT_SRC"),
        "img-src": ["'self'", "data:", "https://www.unicef.org"] + env("CSP_IMG_SRC"),
        "style-src": ["'unsafe-inline'", "'self'"],
        "script-src": [
            "'unsafe-inline'",
            "'self'",
            "'unsafe-eval'",
        ],
        "connect-src": [
            "'self'",
            "ws:",
            "wss:",
        ],
        "frame-src": ["'self'"],
        "object-src": ["'none'"],
        "base-uri": ["'self'"],
    }
}
