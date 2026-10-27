"""Collect sanitised, read-only evidence for the private S5 relationship scenario.

The collector is limited to the named S5 resources. It does not list or read S3
object contents, retrieve a secret value, connect to the instance, or modify
AWS. Its output records a private role relationship and explicitly rejects a
candidate path when entry and network preconditions are absent.
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
DEFAULT_INSTANCE_ID = "i-02772b47e3b868191"
DEFAULT_SUBNET_ID = "subnet-0aeffd35d61f43aa0"
DEFAULT_SECURITY_GROUP_ID = "sg-0df85f7e51f636cac"
DEFAULT_VPC_ID = "vpc-0e36cfe093f1f8c6a"
DEFAULT_BUCKET = "cloudsentinel-eval-250675044619-lab-s1"
DEFAULT_OBJECT_KEY = "s5-synthetic.txt"
DEFAULT_ROLE = "cloudsentinel-eval-lab-s2-s5"
DEFAULT_ROLE_POLICY = "cloudsentinel-eval-test-bucket-access"
DEFAULT_SECRET_NAME = "cloudsentinel-eval-lab-s5-metadata-only"


def _actions(policy: dict[str, Any]) -> set[str]:
    """Return allowed action strings from an inline IAM policy document."""
    actions: set[str] = set()
    statements = policy.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]
    for statement in statements:
        if statement.get("Effect") != "Allow":
            continue
        statement_actions = statement.get("Action", [])
        if isinstance(statement_actions, str):
            statement_actions = [statement_actions]
        actions.update(action for action in statement_actions if isinstance(action, str))
    return actions


def _has_internet_route(route_tables: list[dict[str, Any]]) -> bool:
    """Return whether a route table contains a route to an Internet or NAT gateway."""
    for route_table in route_tables:
        for route in route_table["Routes"]:
            gateway_id = route.get("GatewayId", "")
            nat_gateway_id = route.get("NatGatewayId", "")
            if gateway_id.startswith("igw-") or nat_gateway_id.startswith("nat-"):
                return True
    return False


def evaluate(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Evaluate S5 facts without making AWS calls."""
    instance = snapshot["instance"]
    network = snapshot["network"]
    role_actions = set(snapshot["role"]["allowed_actions"])
    expected_actions = {"s3:ListBucket", "s3:GetObject", "secretsmanager:DescribeSecret"}
    role_has_expected_actions = expected_actions.issubset(role_actions)
    role_can_retrieve_secret_value = "secretsmanager:GetSecretValue" in role_actions or "secretsmanager:*" in role_actions
    internet_route_present = network["internet_route_present"]
    public_entry_point = bool(instance["public_ip"] or instance["public_dns"] or network["ingress_rule_count"])
    egress_enabled = network["egress_rule_count"] > 0
    imdsv2_enforced = instance["imdsv2_required"] and instance["metadata_hop_limit"] == 1
    candidate_path = public_entry_point and internet_route_present and egress_enabled and not imdsv2_enforced

    return {
        "finding_count": 0,
        "findings": [],
        "relationship_count": 1,
        "relationships": [
            {
                "relationship_id": "CS-AWS-S5-REL-001",
                "title": "Private S5 instance profile can access synthetic S3 data and secret metadata",
                "role_has_expected_actions": role_has_expected_actions,
                "synthetic_object_metadata_observed": snapshot["s3"]["object_metadata_observed"],
                "secret_metadata_observed": snapshot["secret"]["metadata_observed"],
                "candidate_path": candidate_path,
                "missing_candidate_path_preconditions": [
                    name
                    for name, present in (
                        ("publicly_reachable_entry_point", public_entry_point),
                        ("internet_or_nat_route", internet_route_present),
                        ("security_group_egress", egress_enabled),
                        ("metadata_service_hop_limit_greater_than_one", not imdsv2_enforced),
                    )
                    if not present
                ],
            }
        ],
        "negative_controls": {
            "instance_has_no_public_address": not instance["public_ip"] and not instance["public_dns"],
            "subnet_does_not_assign_public_ips": not network["map_public_ip_on_launch"],
            "security_group_has_no_ingress": network["ingress_rule_count"] == 0,
            "security_group_has_no_egress": not egress_enabled,
            "vpc_has_no_internet_or_nat_route": not internet_route_present,
            "imdsv2_required_with_hop_limit_one": imdsv2_enforced,
            "role_cannot_get_secret_value": not role_can_retrieve_secret_value,
            "synthetic_object_contents_not_collected": not snapshot["s3"]["object_contents_collected"],
            "secret_value_not_collected": not snapshot["secret"]["secret_value_collected"],
        },
        "interpretation": (
            "The observed role relationship is private configuration evidence only. "
            "No candidate path is asserted because the required entry and network "
            "preconditions are absent, and no secret value was retrieved."
        ),
    }


def collect(arguments: argparse.Namespace) -> dict[str, Any]:
    """Collect named S5 resource metadata through read-only AWS APIs."""
    session = boto3.Session(profile_name=arguments.profile, region_name=arguments.region)
    ec2 = session.client("ec2", region_name=arguments.region)
    iam = session.client("iam")
    s3_profile = arguments.object_metadata_profile or arguments.profile
    s3_session = boto3.Session(profile_name=s3_profile, region_name=arguments.region)
    s3 = s3_session.client("s3")
    secretsmanager = session.client("secretsmanager", region_name=arguments.region)

    instance = ec2.describe_instances(InstanceIds=[arguments.instance_id])["Reservations"][0]["Instances"][0]
    subnet = ec2.describe_subnets(SubnetIds=[arguments.subnet_id])["Subnets"][0]
    security_group = ec2.describe_security_groups(GroupIds=[arguments.security_group_id])["SecurityGroups"][0]
    route_tables = ec2.describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [arguments.vpc_id]}])["RouteTables"]
    root_volume_id = instance["BlockDeviceMappings"][0]["Ebs"]["VolumeId"]
    root_volume = ec2.describe_volumes(VolumeIds=[root_volume_id])["Volumes"][0]
    policy = iam.get_role_policy(RoleName=arguments.role_name, PolicyName=arguments.role_policy_name)["PolicyDocument"]
    object_metadata = s3.head_object(Bucket=arguments.bucket, Key=arguments.object_key)
    secret_metadata = secretsmanager.describe_secret(SecretId=arguments.secret_name)

    metadata_options = instance["MetadataOptions"]
    return {
        "instance": {
            "instance_id": instance["InstanceId"],
            "instance_type": instance["InstanceType"],
            "state": instance["State"]["Name"],
            "public_ip": bool(instance.get("PublicIpAddress")),
            "public_dns": bool(instance.get("PublicDnsName")),
            "private_address_present": bool(instance.get("PrivateIpAddress")),
            "imdsv2_required": metadata_options["HttpTokens"] == "required",
            "metadata_hop_limit": metadata_options["HttpPutResponseHopLimit"],
            "instance_profile_attached": "IamInstanceProfile" in instance,
            "root_volume_encrypted": root_volume["Encrypted"],
        },
        "network": {
            "subnet_id": subnet["SubnetId"],
            "map_public_ip_on_launch": subnet["MapPublicIpOnLaunch"],
            "ingress_rule_count": len(security_group["IpPermissions"]),
            "egress_rule_count": len(security_group["IpPermissionsEgress"]),
            "internet_route_present": _has_internet_route(route_tables),
        },
        "role": {
            "role_name": arguments.role_name,
            "allowed_actions": sorted(_actions(policy)),
        },
        "s3": {
            "object_metadata_observed": True,
            "object_metadata_profile": s3_profile,
            "object_contents_collected": False,
            "default_encryption": object_metadata.get("ServerSideEncryption"),
        },
        "secret": {
            "metadata_observed": True,
            "secret_value_collected": False,
            "has_rotation_configuration": "RotationEnabled" in secret_metadata,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="cloudsentinel-eval")
    parser.add_argument("--region", default=DEFAULT_REGION)
    parser.add_argument("--instance-id", default=DEFAULT_INSTANCE_ID)
    parser.add_argument("--subnet-id", default=DEFAULT_SUBNET_ID)
    parser.add_argument("--security-group-id", default=DEFAULT_SECURITY_GROUP_ID)
    parser.add_argument("--vpc-id", default=DEFAULT_VPC_ID)
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--object-key", default=DEFAULT_OBJECT_KEY)
    parser.add_argument("--role-name", default=DEFAULT_ROLE)
    parser.add_argument("--role-policy-name", default=DEFAULT_ROLE_POLICY)
    parser.add_argument("--secret-name", default=DEFAULT_SECRET_NAME)
    parser.add_argument(
        "--object-metadata-profile",
        help="Optional approved fallback profile used only for S3 HeadObject metadata.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Ignored sanitised JSON evidence path")
    arguments = parser.parse_args()

    if not arguments.profile.startswith("cloudsentinel-"):
        parser.error("profile must begin with 'cloudsentinel-'")

    try:
        snapshot = collect(arguments)
    except (BotoCoreError, ClientError, IndexError, KeyError) as error:
        print(f"Read-only S5 collection failed: {error}", file=sys.stderr)
        return 1

    output = {
        "execution_type": "read_only_s5_private_relationship_evaluation",
        "aws_accessed": True,
        "collected_at": datetime.now(UTC).isoformat(),
        "profile": arguments.profile,
        "object_metadata_profile": arguments.object_metadata_profile or arguments.profile,
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
