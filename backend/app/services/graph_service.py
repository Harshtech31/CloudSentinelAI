"""
Security Knowledge Graph and Attack Path Service for CloudSentinel AI.

Constructs multi-cloud infrastructure graphs, evaluates topological relationships,
discovers multi-hop attack trajectories (e.g. Internet → EC2 → Role → S3), and
computes CVSS-inspired risk scores for Cytoscape.js visualization.
"""

from typing import Any
import uuid

from app.analyzers import RawFinding
from app.attack_engine.attack_graph import AttackEdge, AttackGraph, AttackNode
from app.attack_engine.attack_paths import AttackPathFinder
from app.attack_engine.scoring import AttackPathScorer
from app.core.logging import logger
from app.graph.builder import GraphBuilder
from app.graph.models import EdgeType, NodeType
from app.graph.networkx import NetworkXGraphService
from app.schemas.graph import (
    AttackChainItem,
    AttackChainsResponse,
    CytoscapeEdge,
    CytoscapeEdgeData,
    CytoscapeElements,
    CytoscapeNode,
    CytoscapeNodeData,
    GraphResponse,
    GraphStatsResponse,
)


def build_security_graph(
    resources: dict[str, list[dict[str, Any]]],
    findings: list[RawFinding] | None = None,
) -> tuple[GraphBuilder, AttackGraph, list[dict[str, Any]]]:
    """Construct knowledge graph and attack graph from collected resources and findings."""
    builder = GraphBuilder()
    attack_graph = AttackGraph()

    # Map finding severities to resources
    finding_risks: dict[str, float] = {}
    for f in findings or []:
        res_id = f.resource_id
        weight = 2.0
        if str(f.severity).lower() == "critical":
            weight = 9.5
        elif str(f.severity).lower() == "high":
            weight = 7.5
        elif str(f.severity).lower() == "medium":
            weight = 4.5
        finding_risks[res_id] = max(finding_risks.get(res_id, 0.0), weight)

    # 1. Always create the Internet root node
    builder.add_node(
        "internet",
        label="Public Internet",
        node_type=NodeType.INTERNET,
        region="global",
        properties={"zone": "external", "untrusted": True},
    )
    attack_graph.add_node(
        AttackNode(
            id="internet",
            resource_type="External::Internet",
            resource_arn="internet",
            name="Public Internet",
            is_entry_point=True,
            is_target=False,
            risk_score=0.0,
        )
    )

    # 2. Add VPCs
    for vpc in resources.get("vpcs", []):
        v_id = vpc.get("id", "vpc-unknown")
        builder.add_node(
            v_id,
            label=f"VPC ({vpc.get('region', 'global')})",
            node_type=NodeType.VPC,
            arn=vpc.get("arn"),
            region=vpc.get("region"),
            properties={"cidr": vpc.get("cidr_block", ""), "default": vpc.get("is_default", False)},
        )

    # 3. Add Subnets and link to VPCs
    for sub in resources.get("subnets", []):
        s_id = sub.get("id", "subnet-unknown")
        builder.add_node(
            s_id,
            label=f"Subnet {s_id}",
            node_type=NodeType.SUBNET,
            arn=sub.get("arn"),
            region=sub.get("region"),
            properties={"public_ip_on_launch": sub.get("map_public_ip_on_launch", False)},
        )
        vpc_id = sub.get("vpc_id")
        if vpc_id and vpc_id in builder.nodes:
            builder.add_edge(s_id, vpc_id, EdgeType.MEMBER_OF_VPC)

    # 4. Add Security Groups
    for sg in resources.get("security_groups", []):
        sg_id = sg.get("id", "sg-unknown")
        has_open_ingress = sg.get("has_open_ssh") or sg.get("has_open_rdp") or sg.get("allows_all_traffic")
        builder.add_node(
            sg_id,
            label=sg.get("name", sg_id),
            node_type=NodeType.SECURITY_GROUP,
            arn=sg.get("arn"),
            region=sg.get("region"),
            properties={
                "has_open_ssh": sg.get("has_open_ssh", False),
                "has_open_rdp": sg.get("has_open_rdp", False),
                "allows_all_traffic": sg.get("allows_all_traffic", False),
            },
        )
        attack_graph.add_node(
            AttackNode(
                id=sg_id,
                resource_type="AWS::EC2::SecurityGroup",
                resource_arn=sg.get("arn") or sg_id,
                name=sg.get("name", sg_id),
                is_entry_point=bool(has_open_ingress),
                is_target=False,
                risk_score=8.5 if has_open_ingress else 2.0,
            )
        )
        if has_open_ingress:
            builder.add_edge("internet", sg_id, EdgeType.EXPOSED_TO_INTERNET)
            attack_graph.add_edge(
                AttackEdge(
                    source_id="internet",
                    target_id=sg_id,
                    relation_type="EXPOSES_PORT",
                    is_vulnerable=True,
                    exploit_difficulty=0.2,
                )
            )

    # 5. Add EC2 Instances
    for ec2 in resources.get("ec2_instances", []):
        inst_id = ec2.get("id", "i-unknown")
        is_public = ec2.get("is_public", False) or bool(ec2.get("public_ip"))
        builder.add_node(
            inst_id,
            label=f"EC2 {inst_id}",
            node_type=NodeType.EC2_INSTANCE,
            arn=ec2.get("arn"),
            region=ec2.get("region"),
            properties={
                "public_ip": ec2.get("public_ip"),
                "private_ip": ec2.get("private_ip"),
                "iam_instance_profile": ec2.get("iam_instance_profile"),
            },
        )
        ec2_risk = finding_risks.get(inst_id, 7.0 if is_public else 3.0)
        attack_graph.add_node(
            AttackNode(
                id=inst_id,
                resource_type="AWS::EC2::Instance",
                resource_arn=ec2.get("arn") or inst_id,
                name=f"EC2 {inst_id}",
                is_entry_point=is_public,
                is_target=False,
                risk_score=ec2_risk,
            )
        )

        if is_public:
            builder.add_edge("internet", inst_id, EdgeType.EXPOSED_TO_INTERNET)
            attack_graph.add_edge(
                AttackEdge(
                    source_id="internet",
                    target_id=inst_id,
                    relation_type="PUBLIC_REACHABILITY",
                    is_vulnerable=True,
                    exploit_difficulty=0.3,
                )
            )

        # Attach SGs to EC2
        for sg_id in ec2.get("security_groups", []):
            if sg_id in builder.nodes:
                builder.add_edge(inst_id, sg_id, EdgeType.ATTACHED_SG)
            if sg_id in attack_graph.nodes:
                attack_graph.add_edge(
                    AttackEdge(
                        source_id=sg_id,
                        target_id=inst_id,
                        relation_type="FILTERS_TRAFFIC",
                        is_vulnerable=False,
                    )
                )

        # Link Subnet to EC2
        sub_id = ec2.get("subnet_id")
        if sub_id and sub_id in builder.nodes:
            builder.add_edge(inst_id, sub_id, EdgeType.MEMBER_OF_VPC)

    # 6. Add IAM Roles & Policies
    for role in resources.get("iam_roles", []):
        r_id = role.get("id", role.get("name", "role-unknown"))
        r_arn = role.get("arn", r_id)
        builder.add_node(
            r_id,
            label=f"Role {role.get('name', r_id)}",
            node_type=NodeType.IAM_ROLE,
            arn=r_arn,
            region="global",
        )
        attack_graph.add_node(
            AttackNode(
                id=r_id,
                resource_type="AWS::IAM::Role",
                resource_arn=r_arn,
                name=role.get("name", r_id),
                is_entry_point=False,
                is_target=False,
                risk_score=finding_risks.get(r_id, 6.0),
            )
        )

    # Link EC2 to IAM Roles if instance profile attached
    for ec2 in resources.get("ec2_instances", []):
        inst_id = ec2.get("id")
        profile = ec2.get("iam_instance_profile")
        if profile and inst_id:
            for role in resources.get("iam_roles", []):
                r_id = role.get("id", role.get("name"))
                if r_id and (r_id in profile or role.get("name") in profile):
                    if r_id in builder.nodes:
                        builder.add_edge(inst_id, r_id, EdgeType.ASSUMES_ROLE)
                    if r_id in attack_graph.nodes:
                        attack_graph.add_edge(
                            AttackEdge(
                                source_id=inst_id,
                                target_id=r_id,
                                relation_type="CAN_ASSUME",
                                is_vulnerable=True,
                                exploit_difficulty=0.4,
                            )
                        )

    # 7. Add S3 Buckets (Crown Jewels / Targets)
    for bucket in resources.get("s3_buckets", []):
        b_name = bucket.get("name") or bucket.get("id", "bucket-unknown")
        b_arn = bucket.get("arn") or f"arn:aws:s3:::{b_name}"
        is_pub = bucket.get("is_public", False)
        builder.add_node(
            b_name,
            label=f"S3 {b_name}",
            node_type=NodeType.S3_BUCKET,
            arn=b_arn,
            region=bucket.get("region", "us-east-1"),
            properties={"is_public": is_pub, "encrypted": bucket.get("encrypted", False)},
        )
        b_risk = finding_risks.get(b_name, 9.0 if is_pub else 5.5)
        attack_graph.add_node(
            AttackNode(
                id=b_name,
                resource_type="AWS::S3::Bucket",
                resource_arn=b_arn,
                name=b_name,
                is_entry_point=is_pub,
                is_target=True,
                risk_score=b_risk,
            )
        )

        if is_pub:
            builder.add_edge("internet", b_name, EdgeType.EXPOSED_TO_INTERNET)
            attack_graph.add_edge(
                AttackEdge(
                    source_id="internet",
                    target_id=b_name,
                    relation_type="PUBLIC_READ",
                    is_vulnerable=True,
                    exploit_difficulty=0.1,
                )
            )

        # Allow IAM roles or EC2 instances to reach S3 targets
        for role in resources.get("iam_roles", []):
            r_id = role.get("id", role.get("name"))
            if r_id and r_id in builder.nodes:
                builder.add_edge(r_id, b_name, EdgeType.CAN_ACCESS_S3)
            if r_id and r_id in attack_graph.nodes:
                attack_graph.add_edge(
                    AttackEdge(
                        source_id=r_id,
                        target_id=b_name,
                        relation_type="READS_DATA",
                        is_vulnerable=True,
                        exploit_difficulty=0.5,
                    )
                )

    # 8. Add RDS Instances (Targets)
    for rds in resources.get("rds_instances", []):
        db_id = rds.get("id", "rds-unknown")
        arn = rds.get("arn") or f"arn:aws:rds:::db:{db_id}"
        is_pub = rds.get("publicly_accessible", False)
        builder.add_node(
            db_id,
            label=f"RDS {db_id}",
            node_type=NodeType.RDS_INSTANCE,
            arn=arn,
            region=rds.get("region", "global"),
            properties={"publicly_accessible": is_pub, "storage_encrypted": rds.get("storage_encrypted", False)},
        )
        db_risk = finding_risks.get(db_id, 9.5 if is_pub else 6.0)
        attack_graph.add_node(
            AttackNode(
                id=db_id,
                resource_type="AWS::RDS::DBInstance",
                resource_arn=arn,
                name=db_id,
                is_entry_point=is_pub,
                is_target=True,
                risk_score=db_risk,
            )
        )

        if is_pub:
            builder.add_edge("internet", db_id, EdgeType.EXPOSED_TO_INTERNET)
            attack_graph.add_edge(
                AttackEdge(
                    source_id="internet",
                    target_id=db_id,
                    relation_type="DATABASE_EXPOSURE",
                    is_vulnerable=True,
                    exploit_difficulty=0.2,
                )
            )

        # Link EC2 to RDS
        for ec2 in resources.get("ec2_instances", []):
            inst_id = ec2.get("id")
            if inst_id and inst_id in builder.nodes:
                builder.add_edge(inst_id, db_id, EdgeType.CONNECTS_TO_RDS)
            if inst_id and inst_id in attack_graph.nodes:
                attack_graph.add_edge(
                    AttackEdge(
                        source_id=inst_id,
                        target_id=db_id,
                        relation_type="CONNECTS_TO_DB",
                        is_vulnerable=True,
                        exploit_difficulty=0.6,
                    )
                )

    # 9. Discover Attack Paths & Score
    finder = AttackPathFinder(attack_graph)
    scorer = AttackPathScorer(attack_graph)
    raw_chains = finder.find_paths_from_entry_points(max_depth=5)

    ranked_chains: list[dict[str, Any]] = []
    seen_paths: set[tuple[str, ...]] = set()

    for idx, chain in enumerate(raw_chains):
        path_nodes = tuple(chain["path_nodes"])
        if path_nodes in seen_paths:
            continue
        seen_paths.add(path_nodes)

        score = scorer.score_path(chain["path_nodes"])
        severity = "MEDIUM"
        if score >= 8.5:
            severity = "CRITICAL"
        elif score >= 6.5:
            severity = "HIGH"

        desc = f"Path from {chain['entry_node_id']} across {len(path_nodes)} hop(s) to target asset {chain['target_node_id']}."
        ranked_chains.append(
            {
                "id": f"chain_{idx + 1:02d}_{uuid.uuid4().hex[:6]}",
                "entry_point": chain["entry_node_id"],
                "target": chain["target_node_id"],
                "path": list(path_nodes),
                "length": len(path_nodes),
                "risk_score": score,
                "severity": severity,
                "description": desc,
            }
        )

    # Sort attack chains by risk score descending
    ranked_chains.sort(key=lambda c: c["risk_score"], reverse=True)
    logger.info("Security graph built: %d nodes, %d edges, %d attack chain(s)", len(builder.nodes), len(builder.edges), len(ranked_chains))
    return builder, attack_graph, ranked_chains


class GraphStore:
    """Thread-safe in-memory cache for topology graph responses and attack chains."""

    def __init__(self) -> None:
        self._latest_graph: GraphResponse | None = None
        self._latest_chains: list[AttackChainItem] = []
        self._by_scan: dict[str, tuple[GraphResponse, list[AttackChainItem]]] = {}

    def save_scan_graph(
        self,
        scan_id: str,
        builder: GraphBuilder,
        attack_chains: list[dict[str, Any]],
    ) -> GraphResponse:
        """Serialize GraphBuilder to Cytoscape and store for API retrieval."""
        nx_service = NetworkXGraphService()
        nx_service.build_from_builder(builder)
        cytoscape_dict = nx_service.to_cytoscape()

        nodes = [
            CytoscapeNode(
                data=CytoscapeNodeData(
                    id=n["data"]["id"],
                    label=str(n["data"].get("label") or n["data"]["id"]),
                    type=str(n["data"].get("type") or "UNKNOWN"),
                    arn=str(n["data"].get("arn") or ""),
                    region=str(n["data"].get("region") or ""),
                )
            )
            for n in cytoscape_dict.get("nodes", [])
        ]

        edges = [
            CytoscapeEdge(
                data=CytoscapeEdgeData(
                    id=e["data"]["id"],
                    source=e["data"]["source"],
                    target=e["data"]["target"],
                    type=e["data"].get("type", "RELATION"),
                )
            )
            for e in cytoscape_dict.get("edges", [])
        ]

        stats = GraphStatsResponse(
            total_nodes=len(nodes),
            total_edges=len(edges),
            attack_paths_count=len(attack_chains),
        )

        resp = GraphResponse(
            elements=CytoscapeElements(nodes=nodes, edges=edges),
            stats=stats,
        )

        chain_items = [
            AttackChainItem(
                id=c["id"],
                entry_point=c["entry_point"],
                target=c["target"],
                path=c["path"],
                length=c["length"],
                risk_score=c["risk_score"],
                severity=c["severity"],
                description=c["description"],
            )
            for c in attack_chains
        ]

        self._latest_graph = resp
        self._latest_chains = chain_items
        self._by_scan[scan_id] = (resp, chain_items)
        return resp

    def get_graph(self, scan_id: str | None = None) -> GraphResponse:
        """Fetch graph by scan_id or return latest/empty fallback."""
        if scan_id and scan_id in self._by_scan:
            return self._by_scan[scan_id][0]
        if self._latest_graph is not None:
            return self._latest_graph
        return GraphResponse(
            elements=CytoscapeElements(nodes=[], edges=[]),
            stats=GraphStatsResponse(total_nodes=0, total_edges=0, attack_paths_count=0),
        )

    def get_stats(self, scan_id: str | None = None) -> GraphStatsResponse:
        """Fetch graph stats by scan_id or return latest."""
        return self.get_graph(scan_id).stats

    def get_attack_chains(self, scan_id: str | None = None) -> AttackChainsResponse:
        """Fetch discovered attack chains by scan_id or return latest."""
        if scan_id and scan_id in self._by_scan:
            chains = self._by_scan[scan_id][1]
        else:
            chains = self._latest_chains
        return AttackChainsResponse(total_chains=len(chains), chains=chains)


# Global singleton instance
graph_store = GraphStore()

__all__ = ["build_security_graph", "GraphStore", "graph_store"]
