"""
JWT creation and verification.
Uses HS256 in development; switch to RS256 in production by setting
jwt_private_key_path and jwt_public_key_path in config.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import get_settings
from app.exceptions import AuthenticationError

settings = get_settings()


def create_access_token(
    subject: str,
    tenant_id: str,
    scopes: list[str],
    expires_delta: timedelta | None = None,
) -> str:
    """
    Issue a signed JWT access token.

    Args:
        subject: Typically the client_id.
        tenant_id: The tenant this token belongs to.
        scopes: List of granted scopes.
        expires_delta: Token lifetime. Defaults to settings value.
    """
    now = datetime.now(timezone.utc)
    expires = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "tenant_id": tenant_id,
        "scopes": scopes,
        "iat": now,
        "exp": expires,
        "iss": "behavedrift-api",
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def verify_token(token: str) -> dict[str, Any]:
    """
    Verify and decode a JWT. Raises AuthenticationError on failure.

    Returns the decoded payload dict.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": True},
        )
    except JWTError as exc:
        raise AuthenticationError(f"Invalid or expired token: {exc}") from exc

    if "tenant_id" not in payload:
        raise AuthenticationError("Token is missing tenant_id claim.")

    return payload
