"""
Security Knowledge Graph Builder module.
"""

from typing import Any

from app.graph.models import Edge, EdgeType, Node, NodeType


class GraphBuilder:
    """Constructs knowledge graph by ingesting resources from cloud collectors."""

    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: NodeType,
        arn: str | None = None,
        region: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> Node:
        """Add or update an infrastructure node."""
        node = Node(
            id=node_id,
            label=label,
            type=node_type,
            arn=arn,
            region=region,
            properties=properties or {},
        )
        self.nodes[node_id] = node
        return node

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
        properties: dict[str, Any] | None = None,
    ) -> Edge:
        """Add a directional relationship edge between nodes."""
        if source_id not in self.nodes:
            raise ValueError(f"Source node {source_id} not found.")
        if target_id not in self.nodes:
            raise ValueError(f"Target node {target_id} not found.")

        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            type=edge_type,
            properties=properties or {},
        )
        self.edges.append(edge)
        return edge

    def merge(self, other_builder: "GraphBuilder") -> None:
        """Merge another graph builder's nodes and edges into this one."""
        self.nodes.update(other_builder.nodes)
        self.edges.extend(other_builder.edges)

    def to_dict(self) -> dict[str, Any]:
        """Convert graph into serialized dictionary format."""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "label": n.label,
                    "type": n.type.value if hasattr(n.type, "value") else str(n.type),
                    "arn": n.arn,
                    "region": n.region,
                    "properties": n.properties,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.type.value if hasattr(e.type, "value") else str(e.type),
                    "properties": e.properties,
                }
                for e in self.edges
            ],
        }
