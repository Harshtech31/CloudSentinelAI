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
