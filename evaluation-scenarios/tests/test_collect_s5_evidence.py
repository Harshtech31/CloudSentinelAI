"""Tests for the read-only private S5 relationship evaluator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "collect_s5_evidence.py"
SPEC = importlib.util.spec_from_file_location("collect_s5_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def snapshot(*, public_entry: bool = False, internet_route: bool = False, egress: bool = False, hop_limit: int = 1) -> dict:
    return {
        "instance": {
            "public_ip": public_entry,
            "public_dns": False,
            "imdsv2_required": True,
            "metadata_hop_limit": hop_limit,
        },
        "network": {
            "map_public_ip_on_launch": False,
            "ingress_rule_count": 1 if public_entry else 0,
            "egress_rule_count": 1 if egress else 0,
            "internet_route_present": internet_route,
        },
        "role": {
            "allowed_actions": ["s3:ListBucket", "s3:GetObject", "secretsmanager:DescribeSecret"],
        },
        "s3": {
            "object_metadata_observed": True,
            "object_contents_collected": False,
        },
        "secret": {
            "metadata_observed": True,
            "secret_value_collected": False,
        },
    }


def test_private_s5_relationship_is_not_a_candidate_path():
    result = MODULE.evaluate(snapshot())

    assert result["finding_count"] == 0
    assert result["relationship_count"] == 1
    relationship = result["relationships"][0]
    assert relationship["relationship_id"] == "CS-AWS-S5-REL-001"
    assert relationship["candidate_path"] is False
    assert relationship["missing_candidate_path_preconditions"] == [
        "publicly_reachable_entry_point",
        "internet_or_nat_route",
        "security_group_egress",
        "metadata_service_hop_limit_greater_than_one",
    ]
    assert result["negative_controls"]["role_cannot_get_secret_value"] is True


def test_candidate_path_requires_all_explicit_preconditions():
    data = snapshot(public_entry=True, internet_route=True, egress=True, hop_limit=2)
    data["instance"]["imdsv2_required"] = False

    result = MODULE.evaluate(data)

    assert result["relationships"][0]["candidate_path"] is True
    assert result["relationships"][0]["missing_candidate_path_preconditions"] == []


def test_secret_value_access_is_reported_as_a_negative_control_failure():
    data = snapshot()
    data["role"]["allowed_actions"].append("secretsmanager:GetSecretValue")

    result = MODULE.evaluate(data)

    assert result["negative_controls"]["role_cannot_get_secret_value"] is False
