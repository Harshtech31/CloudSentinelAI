"""
Knowledge graph and Cytoscape.js schemas for OpenAPI docs.
"""

from pydantic import BaseModel, Field


class CytoscapeNodeData(BaseModel):
    """Data payload for a Cytoscape.js graph node."""

    id: str = Field(..., description="Unique node ID", example="node_i_0123")
    label: str = Field(..., description="Display label", example="Web-Server-EC2")
    type: str = Field(..., description="Asset node type", example="EC2_INSTANCE")
    arn: str = Field(
        "", description="Resource ARN", example="arn:aws:ec2:us-east-1:123456789012:instance/i-0123"
    )
    region: str = Field("", description="Asset cloud region", example="us-east-1")


class CytoscapeNode(BaseModel):
    """Cytoscape.js node element."""

    data: CytoscapeNodeData


class CytoscapeEdgeData(BaseModel):
    """Data payload for a Cytoscape.js graph edge."""

    id: str = Field(..., description="Unique edge ID", example="edge_0_node_internet_node_i_0123")
    source: str = Field(..., description="Source node ID", example="node_internet")
    target: str = Field(..., description="Target node ID", example="node_i_0123")
    type: str = Field(..., description="Relationship edge type", example="EXPOSES_PORT")


class CytoscapeEdge(BaseModel):
    """Cytoscape.js edge element."""

    data: CytoscapeEdgeData


class CytoscapeElements(BaseModel):
    """Combined elements container for Cytoscape.js canvas."""

    nodes: list[CytoscapeNode] = Field(default_factory=list, description="Graph nodes")
    edges: list[CytoscapeEdge] = Field(default_factory=list, description="Graph edges")


class GraphStatsResponse(BaseModel):
    """Knowledge graph topology statistics."""

    total_nodes: int = Field(0, description="Total infrastructure nodes in graph", example=48)
    total_edges: int = Field(0, description="Total relationship edges in graph", example=62)
    attack_paths_count: int = Field(0, description="Identified attack paths", example=4)


class GraphResponse(BaseModel):
    """Complete graph response with elements and stats."""

    elements: CytoscapeElements
    stats: GraphStatsResponse


class AttackChainItem(BaseModel):
    """Discovered multi-hop attack trajectory."""

    id: str = Field(..., description="Attack chain ID", example="chain_01")
    entry_point: str = Field(..., description="Initial entry asset ID", example="internet")
    target: str = Field(
        ..., description="Crown-jewel asset target ID", example="arn:aws:s3:::confidential"
    )
    path: list[str] = Field(..., description="Ordered list of traversed node IDs")
    length: int = Field(..., description="Number of hops in path", example=4)
    risk_score: float = Field(
        ..., description="Composite CVSS risk score (0.0 - 10.0)", example=8.9
    )
    severity: str = Field(
        "HIGH", description="Attack chain severity classification", example="CRITICAL"
    )
    description: str = Field("", description="Natural language summary of the attack chain")


class AttackChainsResponse(BaseModel):
    """List of all discovered attack chains with risk rankings."""

    total_chains: int = Field(0, description="Total attack chains found")
    chains: list[AttackChainItem] = Field(default_factory=list, description="Ranked attack chains")


__all__ = [
    "CytoscapeNodeData",
    "CytoscapeNode",
    "CytoscapeEdgeData",
    "CytoscapeEdge",
    "CytoscapeElements",
    "GraphStatsResponse",
    "GraphResponse",
    "AttackChainItem",
    "AttackChainsResponse",
]
