from app.core.security import generate_raw_api_key, hash_api_key


def test_generate_raw_api_key_has_prefix_and_is_long():
    key = generate_raw_api_key()
    assert key.startswith("mp_")
    assert len(key) > 30


def test_generate_raw_api_key_is_unique():
    keys = {generate_raw_api_key() for _ in range(100)}
    assert len(keys) == 100


def test_hash_api_key_is_deterministic():
    key = generate_raw_api_key()
    assert hash_api_key(key) == hash_api_key(key)


def test_hash_api_key_is_fixed_length_hex():
    digest = hash_api_key("anything")
    assert len(digest) == 64
    int(digest, 16)  # raises if not valid hex


def test_different_keys_hash_differently():
    assert hash_api_key("a") != hash_api_key("b")
