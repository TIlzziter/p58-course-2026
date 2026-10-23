import hashlib
import hmac

from initdata import secret_key


def test_secret_key_direction():
    token = "123456:TEST-TOKEN-for-lab03"
    assert secret_key(token) == hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()


def test_known_vector():
    assert secret_key("1:A").hex() == hmac.new(b"WebAppData", b"1:A", hashlib.sha256).hexdigest()
    assert len(secret_key("1:A")) == 32
