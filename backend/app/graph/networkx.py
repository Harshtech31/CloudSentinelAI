"""
NetworkX in-memory Graph Service and Cytoscape.js serializer.
"""

from typing import Any

import networkx as nx

from app.graph.builder import GraphBuilder


class NetworkXGraphService:
    """Manages an in-memory NetworkX MultiDiGraph and Cytoscape serialization."""

    def __init__(self):
        self.nx_graph = nx.MultiDiGraph()

    def build_from_builder(self, builder: GraphBuilder) -> nx.MultiDiGraph:
        """Populate NetworkX graph from a GraphBuilder instance."""
        self.nx_graph.clear()

        for node_id, node in builder.nodes.items():
            self.nx_graph.add_node(
                node_id,
                label=node.label,
                type=node.type.value if hasattr(node.type, "value") else str(node.type),
                arn=node.arn,
                region=node.region,
                **node.properties,
            )

        for edge in builder.edges:
            self.nx_graph.add_edge(
                edge.source_id,
                edge.target_id,
                type=edge.type.value if hasattr(edge.type, "value") else str(edge.type),
                **edge.properties,
            )

        return self.nx_graph

    def to_cytoscape(self) -> dict[str, list[dict[str, Any]]]:
        """Export NetworkX graph elements into Cytoscape.js format."""
        cytoscape_nodes: list[dict[str, Any]] = []
        cytoscape_edges: list[dict[str, Any]] = []

        for node_id, data in self.nx_graph.nodes(data=True):
            cytoscape_nodes.append(
                {
                    "data": {
                        "id": node_id,
                        "label": data.get("label", node_id),
                        "type": data.get("type", "UNKNOWN"),
                        "arn": data.get("arn", ""),
                        "region": data.get("region", ""),
                    }
                }
            )

        for idx, (source, target, data) in enumerate(self.nx_graph.edges(data=True)):
            cytoscape_edges.append(
                {
                    "data": {
                        "id": f"edge_{idx}_{source}_{target}",
                        "source": source,
                        "target": target,
                        "type": data.get("type", "RELATION"),
                    }
                }
            )

        return {
            "nodes": cytoscape_nodes,
            "edges": cytoscape_edges,
        }
