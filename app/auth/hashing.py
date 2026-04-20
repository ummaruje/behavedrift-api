"""Password / secret hashing using bcrypt."""

from __future__ import annotations


import bcrypt


def hash_secret(plain: str) -> str:
    """Hash a plaintext secret. Never store plaintext secrets."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_secret(plain: str, hashed: str) -> bool:
    """Verify a plaintext secret against its bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False
