"""
Unit tests for knowledge graph builder and NetworkX integration.
"""

from app.graph.builder import GraphBuilder
from app.graph.models import EdgeType, NodeType
from app.graph.networkx import NetworkXGraphService
from app.graph.traversals import GraphTraverser


def test_graph_builder_and_networkx_conversion():
    """Verify building nodes/edges and converting to NetworkX & Cytoscape."""
    builder = GraphBuilder()
    builder.add_node(
        node_id="sg-1",
        label="default-sg",
        node_type=NodeType.SECURITY_GROUP,
        region="us-east-1",
    )
    builder.add_node(
        node_id="i-1",
        label="web-instance",
        node_type=NodeType.EC2_INSTANCE,
        region="us-east-1",
    )
    builder.add_edge(
        source_id="sg-1",
        target_id="i-1",
        edge_type=EdgeType.ATTACHED_SG,
    )

    assert len(builder.nodes) == 2
    assert len(builder.edges) == 1

    nx_service = NetworkXGraphService()
    nx_graph = nx_service.build_from_builder(builder)
    assert nx_graph.number_of_nodes() == 2
    assert nx_graph.number_of_edges() == 1

    cytoscape_data = nx_service.to_cytoscape()
    assert len(cytoscape_data["nodes"]) == 2
    assert len(cytoscape_data["edges"]) == 1

    traverser = GraphTraverser(nx_graph)
    reachable = traverser.bfs_reachable("sg-1")
    assert "i-1" in reachable
