"""
Attack Graph construction and representation module.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AttackNode:
    """Represents a node in the attack graph."""

    id: str
    resource_type: str
    resource_arn: str
    name: str
    is_entry_point: bool = False
    is_target: bool = False
    risk_score: float = 0.0
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackEdge:
    """Represents an exploitable transition or relationship between nodes."""

    source_id: str
    target_id: str
    relation_type: str  # e.g., "CAN_ASSUME", "EXPOSES_PORT", "READS_DATA"
    is_vulnerable: bool = False
    exploit_difficulty: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


class AttackGraph:
    """Manages attack graph construction, node lookups, and boundary definitions."""

    def __init__(self):
        self.nodes: dict[str, AttackNode] = {}
        self.edges: list[AttackEdge] = []
        self.adjacency: dict[str, list[str]] = {}

    def add_node(self, node: AttackNode) -> None:
        """Add an asset or exploit node to the attack graph."""
        self.nodes[node.id] = node
        if node.id not in self.adjacency:
            self.adjacency[node.id] = []

    def add_edge(self, edge: AttackEdge) -> None:
        """Add a directed attack edge between two nodes."""
        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} does not exist in graph.")
        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} does not exist in graph.")

        self.edges.append(edge)
        self.adjacency[edge.source_id].append(edge.target_id)

    def get_entry_points(self) -> list[AttackNode]:
        """Retrieve all nodes flagged as entry points (e.g. Internet-facing)."""
        return [node for node in self.nodes.values() if node.is_entry_point]

    def get_target_nodes(self) -> list[AttackNode]:
        """Retrieve all high-value target assets (e.g., sensitive S3, RDS databases)."""
        return [node for node in self.nodes.values() if node.is_target]

    def to_dict(self) -> dict[str, Any]:
        """Export graph structure for serialization."""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "resource_type": n.resource_type,
                    "resource_arn": n.resource_arn,
                    "is_entry_point": n.is_entry_point,
                    "is_target": n.is_target,
                    "risk_score": n.risk_score,
                    "properties": n.properties,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "relation_type": e.relation_type,
                    "is_vulnerable": e.is_vulnerable,
                    "exploit_difficulty": e.exploit_difficulty,
                }
                for e in self.edges
            ],
        }
