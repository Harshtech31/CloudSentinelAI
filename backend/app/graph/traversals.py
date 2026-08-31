"""
Graph traversal and search utilities (BFS, DFS, shortest path).
"""

import networkx as nx


class GraphTraverser:
    """Provides algorithmic graph traversals over NetworkX structures."""

    def __init__(self, nx_graph: nx.MultiDiGraph):
        self.graph = nx_graph

    def bfs_reachable(self, source_node: str, max_depth: int = 5) -> set[str]:
        """Return all nodes reachable from source node within max_depth via BFS."""
        if source_node not in self.graph:
            return set()

        visited: set[str] = {source_node}
        queue: list[tuple[str, int]] = [(source_node, 0)]

        while queue:
            current, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            for neighbor in self.graph.successors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

        return visited

    def shortest_path(self, source: str, target: str) -> list[str] | None:
        """Calculate shortest directed path from source to target."""
        if source not in self.graph or target not in self.graph:
            return None
        try:
            return nx.shortest_path(self.graph, source=source, target=target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
