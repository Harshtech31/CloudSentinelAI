"""
Graph Node and Edge dataclasses and models.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class NodeType(StrEnum):
    """Cloud asset node types in knowledge graph."""

    IAM_USER = "IAM_USER"
    IAM_ROLE = "IAM_ROLE"
    IAM_POLICY = "IAM_POLICY"
    EC2_INSTANCE = "EC2_INSTANCE"
    S3_BUCKET = "S3_BUCKET"
    SECURITY_GROUP = "SECURITY_GROUP"
    VPC = "VPC"
    SUBNET = "SUBNET"
    RDS_INSTANCE = "RDS_INSTANCE"
    INTERNET = "INTERNET"


class EdgeType(StrEnum):
    """Relationship edge types in knowledge graph."""

    ASSUMES_ROLE = "ASSUMES_ROLE"
    ATTACHED_POLICY = "ATTACHED_POLICY"
    MEMBER_OF_VPC = "MEMBER_OF_VPC"
    ATTACHED_SG = "ATTACHED_SG"
    ALLOWS_TRAFFIC_TO = "ALLOWS_TRAFFIC_TO"
    CAN_ACCESS_S3 = "CAN_ACCESS_S3"
    CONNECTS_TO_RDS = "CONNECTS_TO_RDS"
    EXPOSED_TO_INTERNET = "EXPOSED_TO_INTERNET"


@dataclass
class Node:
    """Represents an infrastructure node in the security knowledge graph."""

    id: str
    label: str
    type: NodeType
    arn: str | None = None
    account_id: str | None = None
    region: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """Represents a directional relationship edge between infrastructure nodes."""

    source_id: str
    target_id: str
    type: EdgeType
    properties: dict[str, Any] = field(default_factory=dict)
