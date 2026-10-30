"""
AWS Security Groups Collector for CloudSentinel AI.

Enumerates security groups across configured AWS regions and parses
ingress/egress rules, open CIDRs, and protocol permissions.
"""

from typing import Any

from app.collectors.aws import get_aws_client
from app.collectors.base import BaseCollector
from app.core.config import settings
from app.core.logging import logger


class SecurityGroupCollector(BaseCollector):
    """Collects security groups and their rules from AWS regions."""

    provider = "aws"

    def __init__(self, regions: list[str] | None = None) -> None:
        super().__init__(regions=regions or [settings.AWS_DEFAULT_REGION])

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect security groups across configured regions."""
        security_groups: list[dict[str, Any]] = []

        for region in self.regions:
            try:
                ec2 = get_aws_client("ec2", region=region)
                paginator = ec2.get_paginator("describe_security_groups")
                for page in paginator.paginate():
                    for sg in page.get("SecurityGroups", []):
                        sg_id = sg["GroupId"]
                        sg_name = sg.get("GroupName", sg_id)
                        vpc_id = sg.get("VpcId")
                        arn = f"arn:aws:ec2:{region}:::security-group/{sg_id}"

                        ingress_rules = []
                        has_open_ssh = False
                        has_open_rdp = False
                        allows_all_traffic = False

                        for perm in sg.get("IpPermissions", []):
                            protocol = perm.get("IpProtocol", "")
                            from_port = perm.get("FromPort")
                            to_port = perm.get("ToPort")
                            ip_ranges = [r.get("CidrIp", "") for r in perm.get("IpRanges", [])]
                            ipv6_ranges = [
                                r.get("CidrIpv6", "") for r in perm.get("Ipv6Ranges", [])
                            ]
                            all_cidrs = ip_ranges + ipv6_ranges

                            is_open_to_world = any(
                                cidr in ("0.0.0.0/0", "::/0") for cidr in all_cidrs
                            )

                            if is_open_to_world:
                                if protocol == "-1":
                                    allows_all_traffic = True
                                if (from_port is None or from_port <= 22) and (
                                    to_port is None or to_port >= 22
                                ):
                                    has_open_ssh = True
                                if (from_port is None or from_port <= 3389) and (
                                    to_port is None or to_port >= 3389
                                ):
                                    has_open_rdp = True

                            ingress_rules.append(
                                {
                                    "protocol": protocol,
                                    "from_port": from_port,
                                    "to_port": to_port,
                                    "cidrs": all_cidrs,
                                    "is_open_to_world": is_open_to_world,
                                }
                            )

                        security_groups.append(
                            {
                                "id": sg_id,
                                "name": sg_name,
                                "arn": arn,
                                "region": region,
                                "vpc_id": vpc_id,
                                "description": sg.get("Description", ""),
                                "ingress_rules": ingress_rules,
                                "egress_rules": sg.get("IpPermissionsEgress", []),
                                "has_open_ssh": has_open_ssh,
                                "has_open_rdp": has_open_rdp,
                                "allows_all_traffic": allows_all_traffic,
                            }
                        )
            except Exception as exc:
                logger.warning("Error collecting security groups in %s: %s", region, exc)

        self.record("security_groups", security_groups)
        return self.resources


__all__ = ["SecurityGroupCollector"]
