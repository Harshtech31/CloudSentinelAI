"""Validate the controlled-scenario catalogue without accessing AWS."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog.json"
GROUND_TRUTH_PATH = ROOT / "ground-truth" / "catalog.json"
REQUIRED_SCENARIO_IDS = {"S1", "S2", "S3", "S4", "S5", "S6"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def scenario_ids(document: dict[str, Any], source_name: str) -> set[str]:
    scenarios = document.get("scenarios")
    if not isinstance(scenarios, list):
        raise TypeError(f"{source_name}: 'scenarios' must be a list")

    ids: set[str] = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict) or not isinstance(scenario.get("id"), str):
            raise TypeError(f"{source_name}: every scenario requires a string 'id'")
        scenario_id = scenario["id"]
        if scenario_id in ids:
            raise ValueError(f"{source_name}: duplicate scenario id {scenario_id}")
        ids.add(scenario_id)
    return ids


def main() -> int:
    try:
        catalog = load_json(CATALOG_PATH)
        ground_truth = load_json(GROUND_TRUTH_PATH)
        catalog_ids = scenario_ids(catalog, CATALOG_PATH.name)
        ground_truth_ids = scenario_ids(ground_truth, GROUND_TRUTH_PATH.name)

        if catalog_ids != REQUIRED_SCENARIO_IDS:
            raise ValueError(f"catalog.json: expected {sorted(REQUIRED_SCENARIO_IDS)}, got {sorted(catalog_ids)}")
        if ground_truth_ids != REQUIRED_SCENARIO_IDS:
            raise ValueError(
                f"ground-truth/catalog.json: expected {sorted(REQUIRED_SCENARIO_IDS)}, "
                f"got {sorted(ground_truth_ids)}"
            )

        for scenario in ground_truth["scenarios"]:
            for field in ("expected_findings", "negative_controls", "required_evidence"):
                if not scenario.get(field):
                    raise ValueError(f"{scenario['id']}: '{field}' must not be empty")
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(f"Scenario catalogue validation failed: {error}", file=sys.stderr)
        return 1

    print("Scenario catalogue validation passed for S1-S6.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
