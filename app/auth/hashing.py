"""Password / secret hashing using bcrypt directly."""

from __future__ import annotations

import bcrypt


def hash_secret(plain: str) -> str:
    """Hash a plaintext secret. Never store plaintext secrets."""
    # bcrypt >= 4.1 requires bytes and returns bytes
    password_bytes = plain.encode("utf-8")[:72]  # bcrypt max length
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_secret(plain: str, hashed: str) -> bool:
    """Verify a plaintext secret against its bcrypt hash."""
    try:
        password_bytes = plain.encode("utf-8")[:72]
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except (ValueError, TypeError):
        return False
