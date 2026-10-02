"""
AWS Bedrock Provider for CloudSentinel AI.

Phase 1 stub: lazy boto3 client construction and availability probing.
Useful for deployments already holding AWS credentials; Phase 3
implements the invoke_model round-trip
(roadmap_part3_risk_ai_dashboard.md).
"""

from typing import Any

from app.ai import (
    AIProviderUnavailable,
    BaseAIProvider,
    Explanation,
    ExplanationRequest,
)
from app.core.logging import logger


class BedrockProvider(BaseAIProvider):
    """AWS Bedrock-backed explanation provider (stub)."""

    name = "bedrock"
    model: str = "anthropic.claude-3-haiku-20240307-v1:0"

    def __init__(self, region_name: str = "us-east-1") -> None:
        self.region_name = region_name
        self._client: Any = None

    def _get_client(self) -> Any:
        """Build the boto3 bedrock-runtime client lazily."""
        if self._client is not None:
            return self._client
        try:
            import boto3  # optional dependency at this phase

            self._client = boto3.client("bedrock-runtime", region_name=self.region_name)
        except Exception as exc:  # boto3 missing or no credentials
            raise AIProviderUnavailable(f"Bedrock unavailable: {exc}") from exc
        logger.debug("Bedrock client initialized (region=%s)", self.region_name)
        return self._client

    def is_available(self) -> bool:
        """True when boto3 imports; credential validity is checked at call time."""
        try:
            import boto3  # noqa: F401
        except ImportError:
            return False
        return True

    def explain(self, request: ExplanationRequest) -> Explanation:
        """Generate an explanation via Bedrock (stub; Phase 3 implements)."""
        self._get_client()
        raise AIProviderUnavailable("Bedrock explanation generation lands in Phase 3")


__all__ = ["BedrockProvider"]
