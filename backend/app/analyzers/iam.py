"""
IAM Security Rule Analyzer for CloudSentinel AI.

Evaluates IAM users, roles, and policies against CIS AWS Benchmark and
CSPM best practices:
- AWS-IAM-001: IAM User MFA Disabled (CIS 1.5)
- AWS-IAM-002: Administrator Wildcard Policy (`Action: "*"` on `Resource: "*"`)
- AWS-IAM-003: Unused / Stale Credentials (> 90 days)
- AWS-IAM-004: Inline Policy Direct Attachment (CIS 1.16)
"""

from datetime import datetime, timezone
from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding
from app.core.constants import Severity


class IAMAnalyzer(BaseAnalyzer):
    """Evaluates IAM users, roles, and policies against security rules."""

    service = "iam"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run all IAM rules over collected IAM resources."""
        findings: list[RawFinding] = []
        findings.extend(self._check_root_mfa(resources))
        findings.extend(self._check_admin_wildcard_policy(resources))
        findings.extend(self._check_unused_credentials(resources))
        findings.extend(self._check_inline_policies(resources))
        return findings

    def _check_root_mfa(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-IAM-001: Multi-Factor Authentication disabled for user."""
        findings: list[RawFinding] = []
        users = resources.get("iam_users", [])

        for u in users:
            if not u.get("mfa_active", False):
                username = u.get("name", "unknown")
                findings.append(
                    RawFinding(
                        rule_id="AWS-IAM-001",
                        title=f"MFA Not Enabled for IAM User: {username}",
                        description=(
                            f"IAM user '{username}' does not have Multi-Factor Authentication "
                            "(MFA) enabled, increasing vulnerability to account compromise."
                        ),
                        severity=Severity.HIGH,
                        resource_type="AWS::IAM::User",
                        resource_id=u.get("id", username),
                        resource_arn=u.get("arn"),
                        region="global",
                        remediation=(
                            f"Enforce virtual or hardware MFA for IAM user '{username}' "
                            "in the AWS IAM Console or CLI via 'aws iam create-virtual-mfa-device'."
                        ),
                        remediation_url="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa.html",
                        metadata={"username": username, "cis_control": "1.5"},
                    )
                )

        return findings

    def _check_admin_wildcard_policy(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """Rule AWS-IAM-002: Policy grants excessive wildcard privileges (Action: "*")."""
        findings: list[RawFinding] = []
        policies = resources.get("iam_policies", [])

        for p in policies:
            doc = p.get("document", {})
            statements = doc.get("Statement", [])
            if isinstance(statements, dict):
                statements = [statements]

            has_admin_wildcard = False
            for stmt in statements:
                if stmt.get("Effect") == "Allow":
                    action = stmt.get("Action", [])
                    resource = stmt.get("Resource", [])

                    action_has_star = action == "*" or (
                        isinstance(action, list) and "*" in action
                    )
                    resource_has_star = resource == "*" or (
                        isinstance(resource, list) and "*" in resource
                    )

                    if action_has_star and resource_has_star:
                        has_admin_wildcard = True
                        break

            if has_admin_wildcard:
                pol_name = p.get("name", "unknown")
                findings.append(
                    RawFinding(
                        rule_id="AWS-IAM-002",
                        title=f"Excessive Admin Wildcard Policy: {pol_name}",
                        description=(
                            f"IAM policy '{pol_name}' grants full administrative access "
                            "with Action: '*' and Resource: '*', violating least privilege."
                        ),
                        severity=Severity.CRITICAL,
                        resource_type="AWS::IAM::Policy",
                        resource_id=p.get("id", pol_name),
                        resource_arn=p.get("arn"),
                        region="global",
                        remediation=(
                            f"Revoke full admin wildcard from '{pol_name}' and scope permissions "
                            "strictly to required service actions and resource ARNs."
                        ),
                        remediation_url="https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege",
                        metadata={"policy_name": pol_name, "cis_control": "1.16"},
                    )
                )

        return findings

    def _check_unused_credentials(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """Rule AWS-IAM-003: Access keys unrotated or unused for over 90 days."""
        findings: list[RawFinding] = []
        now = datetime.now(timezone.utc)
        users = resources.get("iam_users", [])

        for u in users:
            username = u.get("name", "unknown")
            for key in u.get("access_keys", []):
                created_at_str = key.get("created_at")
                if not created_at_str:
                    continue
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    age_days = (now - created_at).days
                    if age_days > 90 and key.get("status") == "Active":
                        key_id = key.get("id", "unknown")
                        findings.append(
                            RawFinding(
                                rule_id="AWS-IAM-003",
                                title=f"IAM Access Key Older than 90 Days ({username})",
                                description=(
                                    f"Access key '{key_id}' for user '{username}' was created "
                                    f"{age_days} days ago and has not been rotated."
                                ),
                                severity=Severity.MEDIUM,
                                resource_type="AWS::IAM::AccessKey",
                                resource_id=key_id,
                                resource_arn=f"arn:aws:iam:::user/{username}/accesskey/{key_id}",
                                region="global",
                                remediation=(
                                    f"Rotate access key '{key_id}' for '{username}' immediately "
                                    "and deactivate any superseded credentials."
                                ),
                                remediation_url="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_RotateAccessKey",
                                metadata={"username": username, "key_id": key_id, "age_days": age_days},
                            )
                        )
                except Exception:
                    pass

        return findings

    def _check_inline_policies(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """Rule AWS-IAM-004: Direct inline policy attachment to IAM users."""
        findings: list[RawFinding] = []
        users = resources.get("iam_users", [])

        for u in users:
            inline = u.get("inline_policies", [])
            if inline:
                username = u.get("name", "unknown")
                findings.append(
                    RawFinding(
                        rule_id="AWS-IAM-004",
                        title=f"Inline Policy Attached to User: {username}",
                        description=(
                            f"User '{username}' has {len(inline)} inline policy/policies directly attached. "
                            "CIS guidelines recommend using managed group policies."
                        ),
                        severity=Severity.LOW,
                        resource_type="AWS::IAM::User",
                        resource_id=u.get("id", username),
                        resource_arn=u.get("arn"),
                        region="global",
                        remediation=(
                            f"Convert inline policies on '{username}' to customer-managed policies "
                            "and attach via an IAM group."
                        ),
                        remediation_url="https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html",
                        metadata={"username": username, "inline_count": len(inline)},
                    )
                )

        return findings


__all__ = ["IAMAnalyzer"]
