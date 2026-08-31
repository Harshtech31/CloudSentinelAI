"""
Attack Path Discovery module via graph traversal algorithms.
"""

from typing import Any

from app.attack_engine.attack_graph import AttackGraph


class AttackPathFinder:
    """Discovers feasible multi-hop attack trajectories across cloud assets."""

    def __init__(self, attack_graph: AttackGraph):
        self.graph = attack_graph

    def find_all_paths(
        self,
        start_node_id: str,
        target_node_id: str,
        max_depth: int = 5,
    ) -> list[list[str]]:
        """Find all directed simple attack paths from start to target using DFS."""
        if start_node_id not in self.graph.nodes or target_node_id not in self.graph.nodes:
            return []

        paths: list[list[str]] = []
        visited: set[str] = set()

        def dfs(current_id: str, path: list[str]):
            if len(path) > max_depth:
                return
            if current_id == target_node_id:
                paths.append(list(path))
                return

            visited.add(current_id)
            for neighbor in self.graph.adjacency.get(current_id, []):
                if neighbor not in visited:
                    path.append(neighbor)
                    dfs(neighbor, path)
                    path.pop()
            visited.remove(current_id)

        dfs(start_node_id, [start_node_id])
        return paths

    def find_paths_from_entry_points(self, max_depth: int = 5) -> list[dict[str, Any]]:
        """Find attack paths starting from any entry point leading to any target node."""
        entry_points = self.graph.get_entry_points()
        targets = self.graph.get_target_nodes()
        discovered_chains: list[dict[str, Any]] = []

        for entry in entry_points:
            for target in targets:
                paths = self.find_all_paths(entry.id, target.id, max_depth=max_depth)
                for path in paths:
                    discovered_chains.append(
                        {
                            "entry_node_id": entry.id,
                            "target_node_id": target.id,
                            "path_nodes": path,
                            "length": len(path),
                        }
                    )

        return discovered_chains
