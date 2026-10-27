"""Tests for the read-only controlled-baseline evaluator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "collect_baseline_evidence.py"
SPEC = importlib.util.spec_from_file_location("collect_baseline_evidence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def snapshot(*, internet_gateway: bool, subnet: bool, interface: bool) -> dict:
    return {
        "s3": {
            "bucket": "cloudsentinel-eval-test",
            "public_access_block": {
                "block_public_acls": True,
                "ignore_public_acls": True,
                "block_public_policy": True,
                "restrict_public_buckets": True,
            },
            "default_encryption": "AES256",
        },
        "iam": {
            "role_name": "cloudsentinel-eval-role",
            "inline_policy": {},
            "attached_managed_policies": [],
        },
        "network": {
            "internet_gateways": ["igw-test"] if internet_gateway else [],
            "subnets": ["subnet-test"] if subnet else [],
            "network_interfaces": ["eni-test"] if interface else [],
            "security_group": {
                "group_id": "sg-test",
                "ingress": [{"IpRanges": [{"CidrIp": "0.0.0.0/0"}]}],
                "egress": [],
            },
        },
    }


def test_unattached_fixture_is_not_reported_as_candidate_path():
    result = MODULE.evaluate(snapshot(internet_gateway=False, subnet=False, interface=False))

    assert result["finding_count"] == 1
    finding = result["findings"][0]
    assert finding["rule_id"] == "CS-AWS-NET-001"
    assert finding["candidate_path"] is False
    assert finding["missing_candidate_path_preconditions"] == [
        "internet_gateway",
        "subnet",
        "attached_network_interface",
    ]


def test_full_network_preconditions_are_required_for_candidate_path():
    result = MODULE.evaluate(snapshot(internet_gateway=True, subnet=True, interface=True))

    finding = result["findings"][0]
    assert finding["candidate_path"] is True
    assert finding["missing_candidate_path_preconditions"] == []


def test_protected_s3_and_unmanaged_role_are_negative_controls():
    result = MODULE.evaluate(snapshot(internet_gateway=False, subnet=False, interface=False))

    assert result["negative_controls"]["s3_protected"] is True
    assert result["negative_controls"]["iam_role_has_no_attached_managed_policies"] is True
