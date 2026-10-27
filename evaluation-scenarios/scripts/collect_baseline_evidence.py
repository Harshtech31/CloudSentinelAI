"""Collect and evaluate the deployed CloudSentinel AWS baseline with read-only APIs.

This script is intentionally limited to the approved baseline resources. It does
not enumerate arbitrary account resources, read S3 objects, retrieve secrets,
or modify AWS. Its output is a configuration-evidence record, not proof of
exploitability or an S1--S6 accuracy result.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError


DEFAULT_REGION = "ap-south-2"
DEFAULT_BUCKET = "cloudsentinel-eval-250675044619-lab-s1"
DEFAULT_ROLE = "cloudsentinel-eval-lab-s2-s5"
DEFAULT_ROLE_POLICY = "cloudsentinel-eval-test-bucket-access"
DEFAULT_VPC = "vpc-0e36cfe093f1f8c6a"
DEFAULT_SECURITY_GROUP = "sg-0d33ac555a64a7811"


def _public_access_block(response: dict[str, Any]) -> dict[str, bool]:
    """Normalise AWS S3 public-access-block response keys."""
    configuration = response["PublicAccessBlockConfiguration"]
    return {
        "block_public_acls": configuration["BlockPublicAcls"],
        "ignore_public_acls": configuration["IgnorePublicAcls"],
        "block_public_policy": configuration["BlockPublicPolicy"],
        "restrict_public_buckets": configuration["RestrictPublicBuckets"],
    }


def _default_encryption(response: dict[str, Any]) -> str | None:
    """Return the first default SSE algorithm from an S3 encryption response."""
    rules = response.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
    if not rules:
        return None
    return rules[0].get("ApplyServerSideEncryptionByDefault", {}).get("SSEAlgorithm")


def _is_world_ingress(permission: dict[str, Any]) -> bool:
    """Return whether an ingress permission admits IPv4 traffic from everywhere."""
    return any(item.get("CidrIp") == "0.0.0.0/0" for item in permission.get("IpRanges", []))


def _bucket_policy_allows_public_object_read(policy: dict[str, Any] | None) -> bool:
    """Return whether a bucket policy grants public object reads."""
    if not policy:
        return False
    statements = policy.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]
    for statement in statements:
        if statement.get("Effect") != "Allow" or statement.get("Principal") != "*":
            continue
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]
        if "s3:GetObject" in actions or "s3:*" in actions:
            return True
    return False


def _policy_has_s3_wildcard(policy: dict[str, Any]) -> bool:
    """Return whether any inline-policy statement grants s3:*."""
    statements = policy.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]
    for statement in statements:
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]
        if statement.get("Effect") == "Allow" and "s3:*" in actions:
            return True
    return False


def evaluate(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Evaluate baseline facts without making AWS calls.

    A world-ingress rule is a configuration condition. It becomes a candidate
    path only if a route, attached interface, and workload evidence are all
    present; this approved baseline deliberately lacks those preconditions.
    """
    s3 = snapshot["s3"]
    pab = s3["public_access_block"]
    public_object_read = _bucket_policy_allows_public_object_read(s3.get("bucket_policy"))
    s3_protected = (
        all(pab.values())
        and s3["default_encryption"] is not None
        and not public_object_read
    )
    role = snapshot["iam"]
    role_has_s3_wildcard = _policy_has_s3_wildcard(role["inline_policy"])
    network = snapshot["network"]
    group = network["security_group"]
    world_rules = [permission for permission in group["ingress"] if _is_world_ingress(permission)]
    has_internet_gateway = bool(network["internet_gateways"])
    has_subnet = bool(network["subnets"])
    has_attachment = bool(network["network_interfaces"])
    candidate_path_preconditions_met = has_internet_gateway and has_subnet and has_attachment

    findings: list[dict[str, Any]] = []
    if not s3_protected:
        findings.append(
            {
                "rule_id": "CS-AWS-S3-001",
                "severity": "high",
                "resource": s3["bucket"],
                "title": "S3 public-access controls or bucket policy permit public object reads",
                "evidence": {
                    "public_access_block": pab,
                    "public_object_read_policy": public_object_read,
                    "default_encryption": s3["default_encryption"],
                },
                "candidate_path": False,
            }
        )
    if role_has_s3_wildcard:
        findings.append(
            {
                "rule_id": "CS-AWS-IAM-002",
                "severity": "high",
                "resource": role["role_name"],
                "title": "Test role grants s3:* on the evaluation bucket",
                "candidate_path": False,
            }
        )
    if role["attached_managed_policies"]:
        findings.append(
            {
                "rule_id": "CS-AWS-IAM-001",
                "severity": "medium",
                "resource": role["role_name"],
                "title": "Evaluation role has attached managed policies",
                "candidate_path": False,
            }
        )
    if world_rules:
        findings.append(
            {
                "rule_id": "CS-AWS-NET-001",
                "severity": "medium",
                "resource": group["group_id"],
                "title": "Security-group ingress permits a world source",
                "evidence": {
                    "world_ingress_rule_count": len(world_rules),
                    "internet_gateway_present": has_internet_gateway,
                    "subnet_present": has_subnet,
                    "network_interface_attached": has_attachment,
                },
                "candidate_path": candidate_path_preconditions_met,
                "missing_candidate_path_preconditions": []
                if candidate_path_preconditions_met
                else [
                    name
                    for name, present in (
                        ("internet_gateway", has_internet_gateway),
                        ("subnet", has_subnet),
                        ("attached_network_interface", has_attachment),
                    )
                    if not present
                ],
            }
        )

    return {
        "finding_count": len(findings),
        "findings": findings,
        "negative_controls": {
            "s3_protected": s3_protected,
            "s3_public_object_read_policy": public_object_read,
            "iam_role_has_no_attached_managed_policies": not role["attached_managed_policies"],
            "iam_role_has_s3_wildcard": role_has_s3_wildcard,
            "network_candidate_path_preconditions_met": candidate_path_preconditions_met,
        },
        "interpretation": (
            "Configuration evidence only. A candidate attack path is not asserted "
            "unless all required network and workload preconditions are observed."
        ),
    }


def collect(
    profile: str,
    region: str,
    bucket: str,
    role_name: str,
    role_policy_name: str,
    vpc_id: str,
    security_group_id: str,
) -> dict[str, Any]:
    """Collect the approved baseline resource metadata with read-only AWS calls."""
    session = boto3.Session(profile_name=profile, region_name=region)
    s3 = session.client("s3")
    iam = session.client("iam")
    ec2 = session.client("ec2", region_name=region)

    pab = _public_access_block(s3.get_public_access_block(Bucket=bucket))
    encryption = _default_encryption(s3.get_bucket_encryption(Bucket=bucket))
    try:
        bucket_policy = json.loads(s3.get_bucket_policy(Bucket=bucket)["Policy"])
    except ClientError as error:
        if error.response["Error"]["Code"] != "NoSuchBucketPolicy":
            raise
        bucket_policy = None
    inline_policy = iam.get_role_policy(RoleName=role_name, PolicyName=role_policy_name)["PolicyDocument"]
    attached_policies = iam.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]
    security_group = ec2.describe_security_groups(GroupIds=[security_group_id])["SecurityGroups"][0]
    internet_gateways = ec2.describe_internet_gateways(
        Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
    )["InternetGateways"]
    subnets = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]
    interfaces = ec2.describe_network_interfaces(
        Filters=[{"Name": "group-id", "Values": [security_group_id]}]
    )["NetworkInterfaces"]
    route_tables = ec2.describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["RouteTables"]

    snapshot = {
        "s3": {
            "bucket": bucket,
            "public_access_block": pab,
            "default_encryption": encryption,
            "bucket_policy": bucket_policy,
            "object_contents_collected": False,
            "collection_limitation": "The read-only evaluator does not request S3 object listing or object reads.",
        },
        "iam": {
            "role_name": role_name,
            "inline_policy": inline_policy,
            "attached_managed_policies": [policy["PolicyName"] for policy in attached_policies],
        },
        "network": {
            "vpc_id": vpc_id,
            "internet_gateways": [gateway["InternetGatewayId"] for gateway in internet_gateways],
            "subnets": [subnet["SubnetId"] for subnet in subnets],
            "network_interfaces": [interface["NetworkInterfaceId"] for interface in interfaces],
            "route_tables": [
                {
                    "route_table_id": table["RouteTableId"],
                    "routes": [
                        {
                            "destination": route.get("DestinationCidrBlock"),
                            "gateway_id": route.get("GatewayId"),
                            "state": route.get("State"),
                        }
                        for route in table["Routes"]
                    ],
                }
                for table in route_tables
            ],
            "security_group": {
                "group_id": security_group["GroupId"],
                "ingress": security_group["IpPermissions"],
                "egress": security_group["IpPermissionsEgress"],
            },
        },
    }
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="cloudsentinel-eval")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--role-name", default=DEFAULT_ROLE)
    parser.add_argument("--role-policy-name", default=DEFAULT_ROLE_POLICY)
    parser.add_argument("--vpc-id", default=DEFAULT_VPC)
    parser.add_argument("--security-group-id", default=DEFAULT_SECURITY_GROUP)
    parser.add_argument("--output", type=Path, required=True, help="Ignored, sanitised JSON evidence path")
    arguments = parser.parse_args()

    if not arguments.profile.startswith("cloudsentinel-"):
        parser.error("profile must begin with 'cloudsentinel-'")

    try:
        snapshot = collect(
            arguments.profile,
            arguments.region,
            arguments.bucket,
            arguments.role_name,
            arguments.role_policy_name,
            arguments.vpc_id,
            arguments.security_group_id,
        )
    except (BotoCoreError, ClientError) as error:
        print(f"Read-only baseline collection failed: {error}", file=sys.stderr)
        return 1

    output = {
        "execution_type": "read_only_controlled_baseline_evaluation",
        "aws_accessed": True,
        "collected_at": datetime.now(UTC).isoformat(),
        "profile": arguments.profile,
        "region": arguments.region,
        "snapshot": snapshot,
        "evaluation": evaluate(snapshot),
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output["evaluation"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
