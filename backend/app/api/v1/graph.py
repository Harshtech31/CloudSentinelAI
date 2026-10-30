"""
Attack graph and cloud topology API endpoints for CloudSentinel AI.

Serves Cytoscape.js formatted infrastructure graphs, topology statistics,
and discovered multi-hop attack trajectories.
"""

from fastapi import APIRouter, Query, status

from app.schemas.graph import (
    AttackChainsResponse,
    GraphResponse,
    GraphStatsResponse,
)
from app.services.graph_service import graph_store

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get(
    "",
    response_model=GraphResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Security Knowledge Graph",
    description="Fetch full multi-cloud topology graph formatted as Cytoscape.js nodes and edges.",
)
async def get_graph(
    scan_id: str | None = Query(None, description="Optional scan ID to retrieve graph for specific run"),
) -> GraphResponse:
    """Fetch security knowledge graph in Cytoscape.js format."""
    return graph_store.get_graph(scan_id=scan_id)


@router.get(
    "/stats",
    response_model=GraphStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Graph Topology Statistics",
    description="Returns aggregate counts of nodes, relationship edges, and detected attack paths.",
)
async def get_graph_stats(
    scan_id: str | None = Query(None, description="Optional scan ID to retrieve stats for"),
) -> GraphStatsResponse:
    """Fetch summary graph statistics."""
    return graph_store.get_stats(scan_id=scan_id)


@router.get(
    "/attack-chains",
    response_model=AttackChainsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Discovered Attack Chains",
    description="Retrieve ranked multi-hop attack trajectories with composite risk scores and hop paths.",
)
async def get_attack_chains(
    scan_id: str | None = Query(None, description="Optional scan ID to retrieve attack chains for"),
) -> AttackChainsResponse:
    """Fetch discovered attack chains."""
    return graph_store.get_attack_chains(scan_id=scan_id)


__all__ = ["router"]
