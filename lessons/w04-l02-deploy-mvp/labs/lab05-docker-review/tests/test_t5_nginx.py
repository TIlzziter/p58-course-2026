from conftest import ex
from review import nginx_problems, proxy_targets


def test_targets():
    assert proxy_targets(ex("nginx.conf")) == {"/api/": "app:8000", "/ws/": "app:8000"}


def test_modifiers_and_comments():
    conf = """
    # location /old/ { proxy_pass http://old:1; }
    location = /health { proxy_pass http://app:8000/health; }
    location ~ ^/img/ { root /data; }
    """
    assert proxy_targets(conf) == {"/health": "app:8000"}


def test_known_service_ok():
    assert nginx_problems(ex("nginx.conf"), ex("compose.good.yml")) == []


def test_unknown_upstream():
    conf = "location /api/ { proxy_pass http://backend:8000; }"
    assert nginx_problems(conf, ex("compose.good.yml")) == ["unknown_upstream"]


def test_upstream_block_ok():
    conf = "upstream backend { server app:8000; }\nserver { location /api/ { proxy_pass http://backend; } }"
    assert nginx_problems(conf, ex("compose.good.yml")) == []
