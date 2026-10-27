"""Evaluate the approved S6 SSRF-to-IAM preconditions without AWS or network access.

This deterministic model represents blocked graph edges only. It does not deploy
or contact a service, metadata endpoint, AWS account, or credential provider.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_SNAPSHOT = {
    "reachable_service_entry_point": False,
    "instrumented_ssrf_transition": False,
    "metadata_access_permitted": False,
    "test_role_target_permission": False,
    "non_sensitive_test_target": True,
}


def evaluate(snapshot: dict[str, bool]) -> dict[str, Any]:
    """Return a candidate-path decision from explicit, local-only preconditions."""
    required = (
        "reachable_service_entry_point",
        "instrumented_ssrf_transition",
        "metadata_access_permitted",
        "test_role_target_permission",
        "non_sensitive_test_target",
    )
    missing = [name for name in required if not snapshot[name]]
    candidate_path = not missing
    return {
        "execution_type": "local_s6_precondition_only_evaluation",
        "aws_accessed": False,
        "network_accessed": False,
        "candidate_path": candidate_path,
        "classification": "candidate_preconditions_satisfied" if candidate_path else "preconditions_absent",
        "missing_candidate_path_preconditions": missing,
        "blocked_edges": [
            "request_input_to_instrumented_service",
            "instrumented_service_to_instance_metadata",
            "instance_metadata_to_role_credentials",
            "role_credentials_to_test_target",
        ]
        if not candidate_path
        else [],
        "interpretation": (
            "No SSRF attempt, metadata request, credential retrieval, or AWS call was performed. "
            "The result is a deterministic precondition decision only."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Sanitised local result path")
    arguments = parser.parse_args()

    result = evaluate(DEFAULT_SNAPSHOT)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
