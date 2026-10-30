import json
from typing import Any

from app.ai import (
    AIProviderResponseError,
    AIProviderUnavailable,
    BaseAIProvider,
    Explanation,
    ExplanationRequest,
)
from app.ai.parser import parse_recommendations
from app.ai.prompts import (
    ATTACK_PATH_PROMPT,
    AUDIENCES,
    FINDING_PROMPT,
    SYSTEM_PROMPT,
)
from app.core.config import settings
from app.core.logging import logger


class BedrockProvider(BaseAIProvider):
    """AWS Bedrock explanation provider supporting Claude Haiku 4.5 and Amazon Nova."""

    name = "bedrock"

    def __init__(
        self,
        region_name: str | None = None,
        profile_name: str | None = None,
        model: str | None = None,
    ) -> None:
        self.region_name = region_name or getattr(settings, "AWS_BEDROCK_REGION", "us-east-1")
        self.profile_name = profile_name or getattr(settings, "AWS_BEDROCK_PROFILE", "swirl-old-3k")
        self.model = model or getattr(
            settings, "BEDROCK_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        )
        self._client: Any = None

    def _get_client(self) -> Any:
        """Build the boto3 bedrock-runtime client lazily."""
        if self._client is not None:
            return self._client
        try:
            import boto3
            from botocore.config import Config as BotoConfig

            boto_config = BotoConfig(
                region_name=self.region_name,
                retries={"max_attempts": 3, "mode": "standard"},
            )

            # 1. Prioritize explicit direct keys if configured
            access_key = getattr(settings, "AWS_BEDROCK_ACCESS_KEY_ID", "") or ""
            secret_key = getattr(settings, "AWS_BEDROCK_SECRET_ACCESS_KEY", "") or ""

            if access_key and secret_key:
                self._client = boto3.client(
                    "bedrock-runtime",
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    config=boto_config,
                )
            # 2. Try named profile if configured
            elif self.profile_name:
                try:
                    session = boto3.Session(profile_name=self.profile_name)
                    self._client = session.client("bedrock-runtime", config=boto_config)
                except Exception as profile_err:
                    logger.warning(
                        "Could not load Bedrock profile '%s', falling back to default session: %s",
                        self.profile_name,
                        profile_err,
                    )
                    self._client = boto3.client("bedrock-runtime", config=boto_config)
            else:
                self._client = boto3.client("bedrock-runtime", config=boto_config)

        except Exception as exc:
            raise AIProviderUnavailable(f"Bedrock unavailable: {exc}") from exc

        logger.debug(
            "Bedrock client initialized (profile=%s, region=%s, model=%s)",
            self.profile_name,
            self.region_name,
            self.model,
        )
        return self._client

    def is_available(self) -> bool:
        """Check if Bedrock client can be created."""
        try:
            self._get_client()
            return True
        except Exception:
            return False

    def explain(self, request: ExplanationRequest) -> Explanation:
        """Generate an explanation via Amazon Bedrock."""
        client = self._get_client()
        prompt_text = self._build_prompt(request)

        tokens_used = 0
        try:
            if "anthropic" in self.model or "claude" in self.model:
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "temperature": 0.2,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": prompt_text}],
                }
                response = client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(payload),
                    contentType="application/json",
                )
                res_body = json.loads(response["body"].read().decode("utf-8"))
                content_blocks = res_body.get("content", [])
                raw_text = content_blocks[0].get("text", "") if content_blocks else ""
                usage = res_body.get("usage", {})
                tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)

            elif "nova" in self.model:
                payload = {
                    "messages": [
                        {"role": "user", "content": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt_text}"}]}
                    ],
                    "inferenceConfig": {"temperature": 0.2, "max_new_tokens": 1024},
                }
                response = client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(payload),
                    contentType="application/json",
                )
                res_body = json.loads(response["body"].read().decode("utf-8"))
                raw_text = (
                    res_body.get("output", {})
                    .get("message", {})
                    .get("content", [{}])[0]
                    .get("text", "")
                )
                tokens_used = res_body.get("usage", {}).get("totalTokens", 0)
            else:
                # Default JSON payload for generic text completion
                payload = {
                    "inputText": f"{SYSTEM_PROMPT}\n\n{prompt_text}",
                    "textGenerationConfig": {"maxTokenCount": 1024, "temperature": 0.2},
                }
                response = client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(payload),
                    contentType="application/json",
                )
                res_body = json.loads(response["body"].read().decode("utf-8"))
                raw_text = res_body.get("results", [{}])[0].get("outputText", "")
                tokens_used = 0

        except Exception as exc:
            logger.error("Bedrock invocation failed for model %s: %s", self.model, exc)
            raise AIProviderResponseError(f"Bedrock invocation failed: {exc}") from exc

        if not raw_text.strip():
            raise AIProviderResponseError("Bedrock returned empty response")

        recommendations = parse_recommendations(raw_text)
        return Explanation(
            text=raw_text,
            provider="bedrock",
            model=self.model,
            tokens_used=tokens_used,
            cached=False,
            metadata={"recommendations": recommendations},
        )

    def _build_prompt(self, request: ExplanationRequest) -> str:
        ctx = request.context
        audience_desc = AUDIENCES.get(request.audience, AUDIENCES["analyst"])

        if request.kind == "finding":
            return FINDING_PROMPT.substitute(
                audience=audience_desc,
                rule_id=ctx.get("rule_id", "N/A"),
                title=request.title,
                severity=str(ctx.get("severity", "MEDIUM")),
                resource_type=ctx.get("resource_type", "AWS Resource"),
                resource_id=ctx.get("resource_id", "unknown"),
                region=ctx.get("region", "global"),
                description=ctx.get("description", request.title),
                risk_context=ctx.get("risk_context", "Potential cloud security risk exposure."),
                remediation=ctx.get("remediation", "Review and restrict resource permissions."),
            )

        if request.kind == "attack_path":
            steps = ctx.get("steps", [])
            steps_str = " -> ".join(steps) if isinstance(steps, list) else str(steps)
            return ATTACK_PATH_PROMPT.substitute(
                audience=audience_desc,
                score=str(ctx.get("score", 7.5)),
                band=str(ctx.get("band", "HIGH")),
                steps=steps_str,
                entry=ctx.get("entry", "Internet"),
                target=ctx.get("target", "Sensitive Data Asset"),
                weakest_link=ctx.get("weakest_link", "Overly permissive security group"),
            )

        return f"Explain this cloud security item for {audience_desc}:\nTitle: {request.title}\nContext: {json.dumps(ctx)}"


__all__ = ["BedrockProvider"]
