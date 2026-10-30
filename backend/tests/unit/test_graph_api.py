"""
Unit tests for Graph Engine, Cytoscape serialization, and Graph REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.graph_service import build_security_graph, graph_store


@pytest.fixture
def sample_graph_resources():
    return {
        "security_groups": [
            {
                "id": "sg-web",
                "name": "web-tier-sg",
                "region": "us-east-1",
                "has_open_ssh": True,
                "has_open_rdp": False,
                "allows_all_traffic": False,
            }
        ],
        "ec2_instances": [
            {
                "id": "i-web01",
                "is_public": True,
                "public_ip": "54.210.10.5",
                "security_groups": ["sg-web"],
                "iam_instance_profile": "arn:aws:iam:::role/AppServerRole",
                "region": "us-east-1",
            }
        ],
        "iam_roles": [
            {
                "id": "AppServerRole",
                "name": "AppServerRole",
                "arn": "arn:aws:iam:::role/AppServerRole",
            }
        ],
        "s3_buckets": [
            {
                "name": "company-confidential-data",
                "is_public": False,
                "encrypted": False,
                "region": "us-east-1",
            }
        ],
    }


def test_build_security_graph_and_attack_chains(sample_graph_resources):
    builder, attack_graph, chains = build_security_graph(sample_graph_resources)
    assert len(builder.nodes) >= 4  # internet, sg-web, i-web01, AppServerRole, bucket
    assert len(builder.edges) >= 3

    # Verify attack chain discovery
    assert len(chains) > 0
    top_chain = chains[0]
    assert "entry_point" in top_chain
    assert "target" in top_chain
    assert top_chain["risk_score"] > 0.0
    assert any("internet" in c["path"] for c in chains)


def test_graph_store_and_endpoints(sample_graph_resources):
    client = TestClient(app)
    builder, _, chains = build_security_graph(sample_graph_resources)
    scan_id = "scn_test_graph_01"
    graph_store.save_scan_graph(scan_id, builder, chains)

    # 1. GET /api/v1/graph
    res = client.get(f"/api/v1/graph?scan_id={scan_id}")
    assert res.status_code == 200
    data = res.json()
    assert "elements" in data
    assert len(data["elements"]["nodes"]) > 0
    assert len(data["elements"]["edges"]) > 0

    # 2. GET /api/v1/graph/stats
    res_stats = client.get(f"/api/v1/graph/stats?scan_id={scan_id}")
    assert res_stats.status_code == 200
    stats_data = res_stats.json()
    assert stats_data["total_nodes"] > 0
    assert stats_data["total_edges"] > 0
    assert stats_data["attack_paths_count"] > 0

    # 3. GET /api/v1/graph/attack-chains
    res_chains = client.get(f"/api/v1/graph/attack-chains?scan_id={scan_id}")
    assert res_chains.status_code == 200
    chains_data = res_chains.json()
    assert chains_data["total_chains"] > 0
    assert len(chains_data["chains"]) > 0
    assert chains_data["chains"][0]["risk_score"] > 0.0
