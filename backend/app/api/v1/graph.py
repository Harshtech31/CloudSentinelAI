"""
Attack graph and cloud topology API endpoints for OpenAPI docs.
"""

from fastapi import APIRouter, status

from app.schemas.graph import (
    CytoscapeElements,
    GraphResponse,
    GraphStatsResponse,
)

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get(
    "",
    response_model=GraphResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Security Knowledge Graph",
    description="Fetch full multi-cloud topology graph formatted as Cytoscape.js nodes and edges.",
)
async def get_graph() -> GraphResponse:
    """Fetch security knowledge graph in Cytoscape.js format (Scaffold stub)."""
    return GraphResponse(
        elements=CytoscapeElements(
            nodes=[],
            edges=[],
        ),
        stats=GraphStatsResponse(
            total_nodes=0,
            total_edges=0,
            attack_paths_count=0,
        ),
    )


@router.get(
    "/stats",
    response_model=GraphStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Graph Topology Statistics",
    description="Returns aggregate counts of nodes, relationship edges, and detected attack paths.",
)
async def get_graph_stats() -> GraphStatsResponse:
    """Fetch summary graph statistics (Scaffold stub)."""
    return GraphStatsResponse(
        total_nodes=0,
        total_edges=0,
        attack_paths_count=0,
    )
