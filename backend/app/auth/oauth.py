"""
Google OAuth Stub for CloudSentinel AI.

Placeholder for the Phase 4 SSO track. The shape below documents the
future contract so the frontend can build its "Sign in with Google"
button against a stable interface before any OAuth flow exists.
"""

from dataclasses import dataclass

from app.core.logging import logger


@dataclass
class OAuthUserInfo:
    """Minimal profile returned by a completed OAuth flow."""

    email: str
    full_name: str
    provider: str = "google"
    picture_url: str | None = None


def exchange_code_for_user(code: str) -> OAuthUserInfo:
    """Exchange an OAuth authorization code for a user profile (stub).

    Phase 4 implements the real code→token→userinfo exchange; until then
    this raises so callers fail loudly instead of silently skipping SSO.
    """
    logger.debug("OAuth code exchange requested (len=%s)", len(code))
    raise NotImplementedError("Google OAuth lands in Phase 4")


__all__ = ["OAuthUserInfo", "exchange_code_for_user"]
