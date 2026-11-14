"""Configuration integrity hashing."""

from __future__ import annotations

import hashlib
import hmac

HASH_ALGORITHMS = ("SHA-256", "SHA-512", "SHA3-256")
_NAMES = {"SHA-256": "sha256", "SHA-512": "sha512", "SHA3-256": "sha3_256"}


def compute_hash(data: bytes | str, algorithm: str = "SHA-256") -> str:
    if algorithm not in _NAMES:
        raise ValueError(f"unsupported algorithm: {algorithm!r}")
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.new(_NAMES[algorithm], data).hexdigest()


def verify_hash(data: bytes | str, expected_hex: str, algorithm: str = "SHA-256") -> bool:
    """Constant-time comparison against a known-good digest."""
    return hmac.compare_digest(compute_hash(data, algorithm), expected_hex.strip().lower())
