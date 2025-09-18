from .. import env

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["data:", "'self'", "'unsafe-inline'", "http://unpkg.com/"] + env("CSP_DEFAULT_SRC"),
        "img-src": ["i.pravatar.cc", "'self'", "data:", "https://img.daisyui.com/"] + env("CSP_IMG_SRC"),
        "style-src": ["'unsafe-inline'", "'self'"] + [],
        "script-src": ["'unsafe-inline'", "'self'", "'unsafe-eval'", "https://cdn.jsdelivr.net", "https://unpkg.com/"]
        + [],
    }
}
