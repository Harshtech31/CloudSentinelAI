"""
Evaluation scenarios API endpoint for CloudSentinel AI.

Serves cataloged evaluation scenarios (S1-S6) for benchmark testing,
demo verification, and comparative security posture evaluation.
"""

import json
from pathlib import Path

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/eval", tags=["Evaluation"])

CATALOG_PATH = Path("evaluation-scenarios/catalog.json")


class ScenarioItem(BaseModel):
    id: str = Field(
        ..., description="Scenario identifier (e.g. S1, S2)", json_schema_extra={"example": "S1"}
    )
    name: str = Field(
        ...,
        description="Scenario descriptive title",
        json_schema_extra={"example": "Public S3 storage exposure"},
    )
    status: str = Field(
        ...,
        description="Execution and evaluation status",
        json_schema_extra={"example": "executed_and_restored"},
    )
    focus: list[str] = Field(default_factory=list, description="Core evaluation objectives")
    deployment_boundary: str | None = Field(None, description="Scope and isolation boundary")
    execution_note: str | None = Field(None, description="Detailed runtime evidence note")


class ScenariosCatalogResponse(BaseModel):
    schema_version: str = Field("1.0", description="Catalog schema version")
    purpose: str = Field(..., description="Evaluation framework purpose statement")
    safety_requirements: list[str] = Field(default_factory=list, description="Safeguard criteria")
    scenarios: list[ScenarioItem] = Field(
        default_factory=list, description="Cataloged test scenarios"
    )


@router.get(
    "/scenarios",
    response_model=ScenariosCatalogResponse,
    status_code=status.HTTP_200_OK,
    summary="List Evaluation Scenarios",
    description="Loads the cataloged CSPM and attack path evaluation scenarios for demo and research benchmarking.",
)
async def list_evaluation_scenarios() -> ScenariosCatalogResponse:
    """Load and return evaluation scenarios from catalog.json."""
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return ScenariosCatalogResponse(**data)

    # Fallback default catalog if file is not found
    return ScenariosCatalogResponse(
        schema_version="1.0",
        purpose="Controlled evaluation of CloudSentinel findings and attack paths.",
        safety_requirements=["authorised_non_production_aws_account"],
        scenarios=[
            ScenarioItem(
                id="S1",
                name="Public S3 storage exposure",
                status="partial_account_safeguard_blocked_and_restored",
                focus=["finding_detection", "evidence_capture"],
            ),
            ScenarioItem(
                id="S2",
                name="Overly permissive IAM policy",
                status="executed_and_restored",
                focus=["finding_detection", "identity_relationships"],
            ),
            ScenarioItem(
                id="S5",
                name="Multi-stage candidate path",
                status="executed_evidence_collected_and_torn_down",
                focus=["relationship_evidence", "candidate_path_precondition_rejection"],
            ),
        ],
    )


__all__ = ["router"]
