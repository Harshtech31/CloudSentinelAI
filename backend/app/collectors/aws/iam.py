"""
AWS IAM Collector for CloudSentinel AI.

Enumerates IAM users, roles, attached and inline policies, access keys,
and MFA device status using boto3 with defensive error handling.
"""

from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.collectors.aws import get_aws_client
from app.collectors.base import BaseCollector
from app.core.logging import logger


class IAMCollector(BaseCollector):
    """Collects IAM users, roles, and policies from an AWS account."""

    provider = "aws"

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect IAM resources via boto3 with graceful failure handling."""
        try:
            iam = get_aws_client("iam")
        except Exception as exc:
            logger.warning("Failed to initialize AWS IAM client: %s", exc)
            self.record("iam_users", [])
            self.record("iam_roles", [])
            self.record("iam_policies", [])
            return self.resources

        users = self._collect_users(iam)
        roles = self._collect_roles(iam)
        policies = self._collect_policies(iam)

        self.record("iam_users", users)
        self.record("iam_roles", roles)
        self.record("iam_policies", policies)
        return self.resources

    def _collect_users(self, iam: Any) -> list[dict[str, Any]]:
        users: list[dict[str, Any]] = []
        try:
            paginator = iam.get_paginator("list_users")
            for page in paginator.paginate():
                for u in page.get("Users", []):
                    username = u["UserName"]
                    arn = u.get("Arn", f"arn:aws:iam:::user/{username}")
                    user_data: dict[str, Any] = {
                        "id": u.get("UserId", username),
                        "name": username,
                        "arn": arn,
                        "created_at": u.get("CreateDate", "").isoformat()
                        if hasattr(u.get("CreateDate", ""), "isoformat")
                        else str(u.get("CreateDate", "")),
                        "password_last_used": u.get("PasswordLastUsed", "").isoformat()
                        if hasattr(u.get("PasswordLastUsed", ""), "isoformat")
                        else str(u.get("PasswordLastUsed", "")),
                        "mfa_active": False,
                        "attached_policies": [],
                        "inline_policies": [],
                        "access_keys": [],
                    }

                    # MFA Devices
                    try:
                        mfa_res = iam.list_mfa_devices(UserName=username)
                        user_data["mfa_active"] = len(mfa_res.get("MFADevices", [])) > 0
                    except (ClientError, BotoCoreError) as exc:
                        logger.debug("Failed listing MFA for %s: %s", username, exc)

                    # Attached Policies
                    try:
                        pol_res = iam.list_attached_user_policies(UserName=username)
                        user_data["attached_policies"] = [
                            p.get("PolicyArn", "") for p in pol_res.get("AttachedPolicies", [])
                        ]
                    except (ClientError, BotoCoreError) as exc:
                        logger.debug("Failed listing attached policies for %s: %s", username, exc)

                    # Inline Policies
                    try:
                        inline_res = iam.list_user_policies(UserName=username)
                        user_data["inline_policies"] = inline_res.get("PolicyNames", [])
                    except (ClientError, BotoCoreError) as exc:
                        logger.debug("Failed listing inline policies for %s: %s", username, exc)

                    # Access Keys
                    try:
                        keys_res = iam.list_access_keys(UserName=username)
                        user_data["access_keys"] = [
                            {
                                "id": k.get("AccessKeyId"),
                                "status": k.get("Status"),
                                "created_at": k.get("CreateDate", "").isoformat()
                                if hasattr(k.get("CreateDate", ""), "isoformat")
                                else str(k.get("CreateDate", "")),
                            }
                            for k in keys_res.get("AccessKeyMetadata", [])
                        ]
                    except (ClientError, BotoCoreError) as exc:
                        logger.debug("Failed listing access keys for %s: %s", username, exc)

                    users.append(user_data)
        except Exception as exc:
            logger.warning("Error enumerating IAM users: %s", exc)

        return users

    def _collect_roles(self, iam: Any) -> list[dict[str, Any]]:
        roles: list[dict[str, Any]] = []
        try:
            paginator = iam.get_paginator("list_roles")
            for page in paginator.paginate():
                for r in page.get("Roles", []):
                    role_name = r["RoleName"]
                    # Skip AWS service-linked roles from risk noise
                    if role_name.startswith("aws-service-role") or role_name.startswith(
                        "AWSServiceRole"
                    ):
                        continue

                    role_data: dict[str, Any] = {
                        "id": r.get("RoleId", role_name),
                        "name": role_name,
                        "arn": r.get("Arn", f"arn:aws:iam:::role/{role_name}"),
                        "assume_role_policy": r.get("AssumeRolePolicyDocument", {}),
                        "attached_policies": [],
                    }

                    try:
                        att_res = iam.list_attached_role_policies(RoleName=role_name)
                        role_data["attached_policies"] = [
                            p.get("PolicyArn", "") for p in att_res.get("AttachedPolicies", [])
                        ]
                    except (ClientError, BotoCoreError) as exc:
                        logger.debug(
                            "Failed listing attached policies for role %s: %s", role_name, exc
                        )

                    roles.append(role_data)
        except Exception as exc:
            logger.warning("Error enumerating IAM roles: %s", exc)

        return roles

    def _collect_policies(self, iam: Any) -> list[dict[str, Any]]:
        policies: list[dict[str, Any]] = []
        try:
            paginator = iam.get_paginator("list_policies")
            # Only enumerate customer-managed or attached policies to avoid pagination overload
            for page in paginator.paginate(Scope="Local"):
                for p in page.get("Policies", []):
                    pol_arn = p.get("Arn", "")
                    pol_name = p.get("PolicyName", "")
                    version_id = p.get("DefaultVersionId")
                    document = {}
                    if version_id:
                        try:
                            v_res = iam.get_policy_version(PolicyArn=pol_arn, VersionId=version_id)
                            document = v_res.get("PolicyVersion", {}).get("Document", {})
                        except Exception:
                            pass

                    policies.append(
                        {
                            "id": p.get("PolicyId", pol_name),
                            "name": pol_name,
                            "arn": pol_arn,
                            "document": document,
                            "is_attachable": p.get("IsAttachable", True),
                        }
                    )
        except Exception as exc:
            logger.warning("Error enumerating customer IAM policies: %s", exc)

        return policies


__all__ = ["IAMCollector"]
