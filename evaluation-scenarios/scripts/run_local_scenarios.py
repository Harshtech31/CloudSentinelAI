"""Run safe in-memory validation fixtures for the CloudSentinel scenario catalogue.

This script never calls AWS. It exercises the existing backend attack-graph and
path-finding classes against deterministic, non-sensitive fixture data.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCENARIO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SCENARIO_ROOT.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
GROUND_TRUTH_PATH = SCENARIO_ROOT / "ground-truth" / "catalog.json"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.attack_engine.attack_graph import AttackEdge, AttackGraph, AttackNode  # type: ignore[import-not-found]
from app.attack_engine.attack_paths import AttackPathFinder  # type: ignore[import-not-found]
from app.attack_engine.scoring import AttackPathScorer  # type: ignore[import-not-found]


@dataclass(frozen=True)
class FixtureDefinition:
    """Deterministic local fixture used to validate scenario handling."""

    detected_findings: tuple[str, ...]
    nodes: tuple[AttackNode, ...]
    edges: tuple[AttackEdge, ...]


def node(
    identifier: str,
    resource_type: str,
    *,
    entry: bool = False,
    target: bool = False,
    risk: float = 0.0,
) -> AttackNode:
    """Create a non-sensitive in-memory graph node."""
    return AttackNode(
        id=identifier,
        resource_type=resource_type,
        resource_arn=f"fixture:{identifier}",
        name=identifier.replace("-", " ").title(),
        is_entry_point=entry,
        is_target=target,
        risk_score=risk,
    )


def fixture_definitions() -> dict[str, FixtureDefinition]:
    """Return the six local scenario fixtures; none represent live AWS resources."""
    return {
        "S1": FixtureDefinition(
            detected_findings=("storage_public_access",),
            nodes=(node("test-bucket", "S3_BUCKET", target=True, risk=5.0),),
            edges=(),
        ),
        "S2": FixtureDefinition(
            detected_findings=("overly_permissive_test_iam_policy",),
            nodes=(
                node("test-principal", "IAM_PRINCIPAL", entry=True, risk=4.0),
                node("test-resource", "TEST_RESOURCE", target=True, risk=6.0),
            ),
            edges=(
                AttackEdge(
                    source_id="test-principal",
                    target_id="test-resource",
                    relation_type="POLICY_EVIDENCE",
                    is_vulnerable=True,
                    metadata={"fixture_only": True, "precondition": "policy evidence present"},
                ),
            ),
        ),
        "S3": FixtureDefinition(
            detected_findings=("laboratory_security_group_exposure",),
            nodes=(
                node("lab-entry", "LAB_ENTRY", entry=True, risk=3.0),
                node("test-workload", "EC2_INSTANCE", target=True, risk=5.0),
            ),
            edges=(
                AttackEdge(
                    source_id="lab-entry",
                    target_id="test-workload",
                    relation_type="REACHABILITY_EVIDENCE",
                    is_vulnerable=True,
                    metadata={"fixture_only": True, "precondition": "laboratory reachability evidence"},
                ),
            ),
        ),
        "S4": FixtureDefinition(
            detected_findings=("cloudtrail_disabled_in_test_account",),
            nodes=(node("test-cloudtrail", "CLOUDTRAIL", risk=4.0),),
            edges=(),
        ),
        "S5": FixtureDefinition(
            detected_findings=(
                "test_network_condition",
                "test_iam_permission_condition",
                "test_data_access_condition",
            ),
            nodes=(
                node("lab-entry", "LAB_ENTRY", entry=True, risk=4.0),
                node("test-workload", "EC2_INSTANCE", risk=5.0),
                node("test-role", "IAM_ROLE", risk=7.0),
                node("test-bucket", "S3_BUCKET", target=True, risk=8.0),
            ),
            edges=(
                AttackEdge("lab-entry", "test-workload", "ENTRY_EVIDENCE", True),
                AttackEdge("test-workload", "test-role", "IDENTITY_EVIDENCE", True),
                AttackEdge("test-role", "test-bucket", "DATA_ACCESS_EVIDENCE", True),
            ),
        ),
        "S6": FixtureDefinition(
            detected_findings=(
                "instrumented_test_service_condition",
                "test_identity_permission_condition",
            ),
            nodes=(
                node("instrumented-service", "TEST_SERVICE", entry=True, risk=4.0),
                node("test-identity", "IAM_ROLE", risk=6.0),
                node("test-target", "TEST_RESOURCE", target=True, risk=7.0),
            ),
            edges=(
                AttackEdge(
                    "instrumented-service",
                    "test-identity",
                    "INSTRUMENTED_PRECONDITION",
                    True,
                    metadata={"fixture_only": True, "precondition": "approved test-service condition"},
                ),
                AttackEdge(
                    "test-identity",
                    "test-target",
                    "TEST_PERMISSION_EVIDENCE",
                    True,
                    metadata={"fixture_only": True, "precondition": "test identity permission"},
                ),
            ),
        ),
    }


def load_ground_truth() -> dict[str, dict[str, Any]]:
    """Load ground truth indexed by scenario identifier."""
    with GROUND_TRUTH_PATH.open(encoding="utf-8") as source:
        document = json.load(source)
    return {scenario["id"]: scenario for scenario in document["scenarios"]}


def execute_fixture(scenario_id: str, ground_truth: dict[str, Any]) -> dict[str, Any]:
    """Execute one fixture and compare its local outputs with its ground truth."""
    fixture = fixture_definitions()[scenario_id]
    graph = AttackGraph()
    for graph_node in fixture.nodes:
        graph.add_node(graph_node)
    for graph_edge in fixture.edges:
        graph.add_edge(graph_edge)

    path_finder = AttackPathFinder(graph)
    paths = path_finder.find_paths_from_entry_points(max_depth=5)
    scorer = AttackPathScorer(graph)
    scored_paths = [
        {
            "nodes": path["path_nodes"],
            "length": path["length"],
            "local_fixture_score": scorer.score_path(path["path_nodes"]),
        }
        for path in paths
    ]

    expected_findings = set(ground_truth["expected_findings"])
    detected_findings = set(fixture.detected_findings)
    expected_path = bool(ground_truth["expected_candidate_paths"])
    path_expectation_met = bool(scored_paths) == expected_path

    return {
        "scenario_id": scenario_id,
        "execution_type": "local_in_memory_fixture_validation",
        "aws_accessed": False,
        "detected_findings": sorted(detected_findings),
        "expected_findings": sorted(expected_findings),
        "missing_findings": sorted(expected_findings - detected_findings),
        "unexpected_findings": sorted(detected_findings - expected_findings),
        "candidate_paths": scored_paths,
        "path_expectation_met": path_expectation_met,
        "status": "pass"
        if not (expected_findings - detected_findings) and path_expectation_met
        else "fail",
    }


def run(scenario_ids: list[str] | None = None) -> dict[str, Any]:
    """Run selected scenarios and return sanitised local validation results."""
    ground_truth = load_ground_truth()
    selected_ids = scenario_ids or sorted(ground_truth)
    unknown_ids = set(selected_ids) - set(ground_truth)
    if unknown_ids:
        raise ValueError(f"Unknown scenario identifiers: {sorted(unknown_ids)}")

    results = [execute_fixture(scenario_id, ground_truth[scenario_id]) for scenario_id in selected_ids]
    return {
        "execution_type": "local_in_memory_fixture_validation",
        "aws_accessed": False,
        "results": results,
        "passed": sum(result["status"] == "pass" for result in results),
        "total": len(results),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", action="append", dest="scenario_ids", help="Scenario ID to run")
    parser.add_argument("--output", type=Path, help="Optional path for sanitised JSON results")
    arguments = parser.parse_args()

    result = run(arguments.scenario_ids)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(f"{rendered}\n", encoding="utf-8")
    return 0 if result["passed"] == result["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
