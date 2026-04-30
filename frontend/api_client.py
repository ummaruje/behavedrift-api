"""
BehaveDrift API Client
Centralised httpx wrapper for all API interactions.
Manages authentication state via Streamlit session_state.
"""

from __future__ import annotations

import httpx
import streamlit as st

DEFAULT_BASE_URL = "https://behavedrift-api.onrender.com"
TIMEOUT = 30.0


def _base_url() -> str:
    return st.session_state.get("api_base_url", DEFAULT_BASE_URL).rstrip("/")


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


# ── Health ───────────────────────────────────────────────────


def check_health() -> dict | None:
    """Check API health (unauthenticated)."""
    try:
        r = httpx.get(f"{_base_url()}/health", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ── Auth ─────────────────────────────────────────────────────


def register_tenant(
    organisation_name: str,
    contact_email: str,
    plan: str = "self_hosted",
) -> dict | None:
    """POST /v1/auth/tenants — provision a new tenant."""
    try:
        r = httpx.post(
            f"{_base_url()}/v1/auth/tenants",
            json={
                "organisation_name": organisation_name,
                "contact_email": contact_email,
                "plan": plan,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _show_api_error(e)
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def get_token(client_id: str, client_secret: str) -> dict | None:
    """POST /v1/auth/token — exchange credentials for a JWT."""
    try:
        r = httpx.post(
            f"{_base_url()}/v1/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _show_api_error(e)
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


# ── Generic Helpers ──────────────────────────────────────────


def api_get(path: str, params: dict | None = None) -> dict | list | None:
    """Authenticated GET request."""
    try:
        r = httpx.get(
            f"{_base_url()}{path}",
            headers=_headers(),
            params=params,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _show_api_error(e)
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def api_post(path: str, json_data: dict | None = None) -> dict | None:
    """Authenticated POST request."""
    try:
        r = httpx.post(
            f"{_base_url()}{path}",
            headers=_headers(),
            json=json_data,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _show_api_error(e)
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def api_put(path: str, json_data: dict | None = None) -> dict | None:
    """Authenticated PUT request."""
    try:
        r = httpx.put(
            f"{_base_url()}{path}",
            headers=_headers(),
            json=json_data,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _show_api_error(e)
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def api_delete(path: str, json_data: dict | None = None) -> dict | None:
    """Authenticated DELETE request."""
    try:
        r = httpx.request(
            "DELETE",
            f"{_base_url()}{path}",
            headers=_headers(),
            json=json_data,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        _show_api_error(e)
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


def api_get_raw(path: str, params: dict | None = None) -> bytes | None:
    """Authenticated GET request returning raw bytes (for file downloads)."""
    try:
        r = httpx.get(
            f"{_base_url()}{path}",
            headers=_headers(),
            params=params,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.content
    except httpx.HTTPStatusError as e:
        _show_api_error(e)
        return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


# ── Error display ────────────────────────────────────────────


def _show_api_error(e: httpx.HTTPStatusError) -> None:
    """Display a user-friendly API error in Streamlit."""
    try:
        detail = e.response.json()
        msg = detail.get("detail", detail.get("message", str(detail)))
    except Exception:
        msg = e.response.text or str(e)
    st.error(f"API Error ({e.response.status_code}): {msg}")


# ── Auth guard ───────────────────────────────────────────────


def require_auth() -> bool:
    """Check if user is authenticated. Shows warning if not. Returns True if OK."""
    if not st.session_state.get("access_token"):
        st.warning("🔒 Please authenticate first using the sidebar.")
        st.stop()
    return True
