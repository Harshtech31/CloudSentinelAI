"""
AWS VPC Collector for CloudSentinel AI.

Enumerates VPCs, subnets, and route tables across configured AWS regions.
"""

from typing import Any

from app.collectors.aws import get_aws_client
from app.collectors.base import BaseCollector
from app.core.config import settings
from app.core.logging import logger


class VPCCollector(BaseCollector):
    """Collects VPCs, subnets, and route tables from AWS regions."""

    provider = "aws"

    def __init__(self, regions: list[str] | None = None) -> None:
        super().__init__(regions=regions or [settings.AWS_DEFAULT_REGION])

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect VPC networking assets across configured regions."""
        vpcs: list[dict[str, Any]] = []
        subnets: list[dict[str, Any]] = []
        route_tables: list[dict[str, Any]] = []

        for region in self.regions:
            try:
                ec2 = get_aws_client("ec2", region=region)

                # 1. VPCs
                try:
                    vpc_res = ec2.describe_vpcs()
                    for v in vpc_res.get("Vpcs", []):
                        vpc_id = v["VpcId"]
                        name = vpc_id
                        for t in v.get("Tags", []):
                            if t.get("Key") == "Name" and t.get("Value"):
                                name = t["Value"]
                                break

                        vpcs.append(
                            {
                                "id": vpc_id,
                                "name": name,
                                "arn": f"arn:aws:ec2:{region}:::vpc/{vpc_id}",
                                "region": region,
                                "cidr_block": v.get("CidrBlock"),
                                "is_default": v.get("IsDefault", False),
                                "state": v.get("State", "available"),
                            }
                        )
                except Exception as exc:
                    logger.warning("Error describing VPCs in %s: %s", region, exc)

                # 2. Subnets
                try:
                    subnet_res = ec2.describe_subnets()
                    for s in subnet_res.get("Subnets", []):
                        sub_id = s["SubnetId"]
                        name = sub_id
                        for t in s.get("Tags", []):
                            if t.get("Key") == "Name" and t.get("Value"):
                                name = t["Value"]
                                break

                        subnets.append(
                            {
                                "id": sub_id,
                                "name": name,
                                "arn": f"arn:aws:ec2:{region}:::subnet/{sub_id}",
                                "region": region,
                                "vpc_id": s.get("VpcId"),
                                "cidr_block": s.get("CidrBlock"),
                                "map_public_ip_on_launch": s.get("MapPublicIpOnLaunch", False),
                                "az": s.get("AvailabilityZone"),
                            }
                        )
                except Exception as exc:
                    logger.warning("Error describing subnets in %s: %s", region, exc)

                # 3. Route Tables
                try:
                    rt_res = ec2.describe_route_tables()
                    for rt in rt_res.get("RouteTables", []):
                        rt_id = rt["RouteTableId"]
                        routes = [
                            {
                                "destination": r.get("DestinationCidrBlock")
                                or r.get("DestinationIpv6CidrBlock"),
                                "gateway_id": r.get("GatewayId"),
                                "state": r.get("State"),
                            }
                            for r in rt.get("Routes", [])
                        ]
                        has_igw = any(r.get("gateway_id", "").startswith("igw-") for r in routes)

                        route_tables.append(
                            {
                                "id": rt_id,
                                "arn": f"arn:aws:ec2:{region}:::route-table/{rt_id}",
                                "region": region,
                                "vpc_id": rt.get("VpcId"),
                                "routes": routes,
                                "has_internet_gateway": has_igw,
                            }
                        )
                except Exception as exc:
                    logger.warning("Error describing route tables in %s: %s", region, exc)

            except Exception as exc:
                logger.warning("Error initializing EC2 client for VPC in %s: %s", region, exc)

        self.record("vpcs", vpcs)
        self.record("subnets", subnets)
        self.record("route_tables", route_tables)
        return self.resources


__all__ = ["VPCCollector"]
