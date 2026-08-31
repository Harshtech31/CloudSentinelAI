"""
Lateral movement detection across networked compute and cloud assets.
"""

from typing import Any

from app.attack_engine.attack_graph import AttackGraph


class LateralMovementDetector:
    """Identifies lateral movement opportunities (e.g., VPC peering, shared security groups)."""

    def __init__(self, attack_graph: AttackGraph):
        self.graph = attack_graph

    def detect_lateral_movement_paths(self) -> list[dict[str, Any]]:
        """Identify potential pivots between compute instances or VPCs."""
        movements: list[dict[str, Any]] = []

        for edge in self.graph.edges:
            if edge.relation_type in ["CAN_PIVOT_TO", "SHARED_SECURITY_GROUP", "VPC_PEERED"]:
                movements.append(
                    {
                        "source_id": edge.source_id,
                        "target_id": edge.target_id,
                        "technique": "Lateral Movement via Network Reachability",
                        "relation": edge.relation_type,
                    }
                )

        return movements
