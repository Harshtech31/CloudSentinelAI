"""
AWS EC2 Collector for CloudSentinel AI.

Enumerates EC2 instances, metadata, attached IAM profiles, public IPs,
and associated security groups across configured AWS regions.
"""

from typing import Any

from app.collectors.aws import get_aws_client
from app.collectors.base import BaseCollector
from app.core.config import settings
from app.core.logging import logger


class EC2Collector(BaseCollector):
    """Collects EC2 instances and instance metadata from AWS regions."""

    provider = "aws"

    def __init__(self, regions: list[str] | None = None) -> None:
        super().__init__(regions=regions or [settings.AWS_DEFAULT_REGION])

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect EC2 instances across configured regions."""
        instances: list[dict[str, Any]] = []

        for region in self.regions:
            try:
                ec2 = get_aws_client("ec2", region=region)
                paginator = ec2.get_paginator("describe_instances")
                for page in paginator.paginate():
                    for res in page.get("Reservations", []):
                        for inst in res.get("Instances", []):
                            inst_id = inst["InstanceId"]
                            name = inst_id
                            for tag in inst.get("Tags", []):
                                if tag.get("Key") == "Name" and tag.get("Value"):
                                    name = tag["Value"]
                                    break

                            iam_profile = inst.get("IamInstanceProfile", {}).get("Arn")
                            state = inst.get("State", {}).get("Name", "unknown")
                            sgs = [
                                {
                                    "id": sg.get("GroupId"),
                                    "name": sg.get("GroupName"),
                                }
                                for sg in inst.get("SecurityGroups", [])
                            ]

                            instances.append(
                                {
                                    "id": inst_id,
                                    "name": name,
                                    "arn": f"arn:aws:ec2:{region}:::instance/{inst_id}",
                                    "region": region,
                                    "instance_type": inst.get("InstanceType"),
                                    "state": state,
                                    "public_ip": inst.get("PublicIpAddress"),
                                    "private_ip": inst.get("PrivateIpAddress"),
                                    "subnet_id": inst.get("SubnetId"),
                                    "vpc_id": inst.get("VpcId"),
                                    "iam_profile": iam_profile,
                                    "security_groups": sgs,
                                    "launch_time": inst.get("LaunchTime", "").isoformat()
                                    if hasattr(inst.get("LaunchTime", ""), "isoformat")
                                    else str(inst.get("LaunchTime", "")),
                                }
                            )
            except Exception as exc:
                logger.warning("Error collecting EC2 instances in %s: %s", region, exc)

        self.record("ec2_instances", instances)
        return self.resources


__all__ = ["EC2Collector"]
