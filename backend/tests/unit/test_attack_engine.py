"""
Unit tests for attack engine models and path finding algorithms.
"""

from app.attack_engine.attack_graph import AttackEdge, AttackGraph, AttackNode
from app.attack_engine.attack_paths import AttackPathFinder
from app.attack_engine.scoring import AttackPathScorer


def test_attack_graph_construction():
    """Verify node and edge addition in AttackGraph."""
    graph = AttackGraph()
    n1 = AttackNode(
        id="internet",
        resource_type="INTERNET",
        resource_arn="arn:aws:internet",
        name="Internet",
        is_entry_point=True,
    )
    n2 = AttackNode(
        id="ec2-1",
        resource_type="EC2_INSTANCE",
        resource_arn="arn:aws:ec2:i-1",
        name="Web Server",
        risk_score=7.5,
    )
    n3 = AttackNode(
        id="s3-1",
        resource_type="S3_BUCKET",
        resource_arn="arn:aws:s3:::data",
        name="Sensitive Bucket",
        is_target=True,
        risk_score=9.0,
    )

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_node(n3)

    graph.add_edge(AttackEdge(source_id="internet", target_id="ec2-1", relation_type="EXPOSES_SSH"))
    graph.add_edge(AttackEdge(source_id="ec2-1", target_id="s3-1", relation_type="READS_DATA"))

    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2
    assert len(graph.get_entry_points()) == 1
    assert len(graph.get_target_nodes()) == 1


def test_attack_path_finder():
    """Verify discovery of multi-hop attack paths."""
    graph = AttackGraph()
    n1 = AttackNode(
        id="internet",
        resource_type="INTERNET",
        resource_arn="arn:internet",
        name="Internet",
        is_entry_point=True,
    )
    n2 = AttackNode(
        id="ec2", resource_type="EC2", resource_arn="arn:ec2", name="EC2", risk_score=6.0
    )
    n3 = AttackNode(
        id="role", resource_type="IAM_ROLE", resource_arn="arn:role", name="Role", risk_score=8.0
    )
    n4 = AttackNode(
        id="s3",
        resource_type="S3",
        resource_arn="arn:s3",
        name="S3",
        is_target=True,
        risk_score=9.0,
    )

    for node in [n1, n2, n3, n4]:
        graph.add_node(node)

    graph.add_edge(AttackEdge(source_id="internet", target_id="ec2", relation_type="SSH_OPEN"))
    graph.add_edge(AttackEdge(source_id="ec2", target_id="role", relation_type="CAN_ASSUME"))
    graph.add_edge(AttackEdge(source_id="role", target_id="s3", relation_type="ADMIN_ACCESS"))

    finder = AttackPathFinder(graph)
    paths = finder.find_all_paths("internet", "s3")

    assert len(paths) == 1
    assert paths[0] == ["internet", "ec2", "role", "s3"]

    scorer = AttackPathScorer(graph)
    score = scorer.score_path(paths[0])
    assert 0.0 <= score <= 10.0
