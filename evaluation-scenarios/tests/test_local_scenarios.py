"""Tests for safe local CloudSentinel evaluation fixtures."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

SCENARIO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = SCENARIO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

run = importlib.import_module("run_local_scenarios").run


def test_all_local_fixtures_match_catalogue_expectations() -> None:
    result = run()

    assert result["execution_type"] == "local_in_memory_fixture_validation"
    assert result["aws_accessed"] is False
    assert result["total"] == 6
    assert result["passed"] == 6
    assert all(scenario["status"] == "pass" for scenario in result["results"])


def test_s5_returns_one_multi_stage_candidate_path() -> None:
    result = run(["S5"])
    scenario = result["results"][0]

    assert scenario["status"] == "pass"
    assert scenario["path_expectation_met"] is True
    assert scenario["candidate_paths"][0]["nodes"] == [
        "lab-entry",
        "test-workload",
        "test-role",
        "test-bucket",
    ]


def test_s6_is_explicitly_local_and_never_accesses_aws() -> None:
    result = run(["S6"])
    scenario = result["results"][0]

    assert result["aws_accessed"] is False
    assert scenario["aws_accessed"] is False
    assert scenario["status"] == "pass"
