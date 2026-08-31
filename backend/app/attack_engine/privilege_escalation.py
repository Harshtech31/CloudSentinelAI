"""
Privilege Escalation pattern identification across IAM roles and policies.
"""

from typing import Any

from app.attack_engine.attack_graph import AttackGraph


class PrivilegeEscalationDetector:
    """Detects IAM misconfigurations that allow identity escalation to Admin or higher rights."""

    # Common IAM permissions that allow privilege escalation (Rhino Security Labs / MITRE ATT&CK)
    DANGEROUS_PERMISSIONS = [
        "iam:CreateAccessKey",
        "iam:CreateLoginProfile",
        "iam:UpdateLoginProfile",
        "iam:AttachUserPolicy",
        "iam:AttachGroupPolicy",
        "iam:AttachRolePolicy",
        "iam:PutUserPolicy",
        "iam:PutGroupPolicy",
        "iam:PutRolePolicy",
        "iam:SetDefaultPolicyVersion",
        "iam:PassRole",
        "sts:AssumeRole",
    ]

    def __init__(self, attack_graph: AttackGraph):
        self.graph = attack_graph

    def detect_escalation_paths(self) -> list[dict[str, Any]]:
        """Identify IAM escalation vectors in the graph."""
        escalations: list[dict[str, Any]] = []

        for edge in self.graph.edges:
            if edge.relation_type in [
                "CAN_ASSUME_ROLE",
                "HAS_ADMIN_PRIVILEGES",
                "CAN_ATTACH_POLICY",
            ]:
                escalations.append(
                    {
                        "source_id": edge.source_id,
                        "target_id": edge.target_id,
                        "relation": edge.relation_type,
                        "risk_level": "HIGH",
                    }
                )

        return escalations
