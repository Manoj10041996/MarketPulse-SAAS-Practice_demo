import hashlib
import secrets


def generate_raw_api_key() -> str:
    """A high-entropy random key, shown to the customer exactly once."""
    return f"mp_{secrets.token_urlsafe(32)}"


def hash_api_key(raw_key: str) -> str:
    """Deterministic hash for storage/lookup.

    Plain sha256, not bcrypt/argon2: those slow KDFs defend against
    brute-forcing low-entropy human passwords. A raw API key here is
    already a 256-bit random secret from generate_raw_api_key() — brute
    force is already infeasible — and a deterministic hash is what allows
    an O(1) indexed lookup instead of scanning every stored key per request.
    """
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
