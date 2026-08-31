"""
Attack Path Scoring and CVSS-inspired Risk Metrics Calculation.
"""

from app.attack_engine.attack_graph import AttackGraph


class AttackPathScorer:
    """Calculates cumulative and bottleneck risk scores for multi-stage attack chains."""

    def __init__(self, attack_graph: AttackGraph):
        self.graph = attack_graph

    def score_path(self, path_node_ids: list[str]) -> float:
        """Calculate composite risk score (0.0 - 10.0) for an attack path."""
        if not path_node_ids:
            return 0.0

        # Sum of node risks weighted by path traversal difficulty
        total_risk = 0.0
        for node_id in path_node_ids:
            node = self.graph.nodes.get(node_id)
            if node:
                total_risk += node.risk_score

        # Average normalized to max 10.0 scale
        normalized = min(10.0, (total_risk / len(path_node_ids)) * (1.0 + 0.1 * len(path_node_ids)))
        return round(normalized, 2)
