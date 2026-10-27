"""Tests for the local-only S6 SSRF-to-IAM precondition evaluator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evaluate_s6_preconditions.py"
SPEC = importlib.util.spec_from_file_location("evaluate_s6_preconditions", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_approved_s6_design_rejects_a_candidate_path_without_aws_or_network_access():
    result = MODULE.evaluate(MODULE.DEFAULT_SNAPSHOT)

    assert result["aws_accessed"] is False
    assert result["network_accessed"] is False
    assert result["candidate_path"] is False
    assert result["classification"] == "preconditions_absent"
    assert result["missing_candidate_path_preconditions"] == [
        "reachable_service_entry_point",
        "instrumented_ssrf_transition",
        "metadata_access_permitted",
        "test_role_target_permission",
    ]


def test_candidate_path_requires_every_documented_precondition():
    snapshot = {key: True for key in MODULE.DEFAULT_SNAPSHOT}

    result = MODULE.evaluate(snapshot)

    assert result["candidate_path"] is True
    assert result["blocked_edges"] == []


def test_any_missing_precondition_rejects_the_candidate_path():
    snapshot = {key: True for key in MODULE.DEFAULT_SNAPSHOT}
    snapshot["metadata_access_permitted"] = False

    result = MODULE.evaluate(snapshot)

    assert result["candidate_path"] is False
    assert result["missing_candidate_path_preconditions"] == ["metadata_access_permitted"]
