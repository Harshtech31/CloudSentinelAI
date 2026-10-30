"""
Networking Security Rule Analyzer for CloudSentinel AI.

Evaluates security groups, VPCs, and network topology against CIS controls:
- AWS-NET-001: Security Group allows inbound SSH (port 22) from 0.0.0.0/0 (CIS 4.1)
- AWS-NET-002: Security Group allows inbound RDP (port 3389) from 0.0.0.0/0 (CIS 4.2)
- AWS-NET-003: Security Group allows unrestricted traffic (all protocols/ports) from anywhere
- AWS-NET-004: Default VPC in active use
- AWS-NET-005: Subnet automatically assigns public IP addresses on launch
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding
from app.core.constants import Severity


class NetworkingAnalyzer(BaseAnalyzer):
    """Evaluates security groups and network topology against security rules."""

    service = "networking"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Run all networking rules over collected resources."""
        findings: list[RawFinding] = []
        findings.extend(self._check_open_ssh_rdp(resources))
        findings.extend(self._check_all_traffic(resources))
        findings.extend(self._check_default_vpc(resources))
        findings.extend(self._check_public_subnets(resources))
        return findings

    def _check_open_ssh_rdp(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rules AWS-NET-001 & AWS-NET-002: Open SSH (22) and RDP (3389) from 0.0.0.0/0."""
        findings: list[RawFinding] = []
        sgs = resources.get("security_groups", [])

        for sg in sgs:
            sg_id = sg.get("id", "unknown")
            sg_name = sg.get("name", sg_id)
            region = sg.get("region", "global")
            arn = sg.get("arn") or f"arn:aws:ec2:{region}:::security-group/{sg_id}"

            if sg.get("has_open_ssh"):
                findings.append(
                    RawFinding(
                        rule_id="AWS-NET-001",
                        title=f"Security Group Allows Public Inbound SSH: {sg_name}",
                        description=(
                            f"Security group '{sg_name}' ({sg_id}) permits ingress on port 22 (SSH) "
                            "from 0.0.0.0/0 or ::/0, exposing instances to brute-force attacks."
                        ),
                        severity=Severity.CRITICAL,
                        resource_type="AWS::EC2::SecurityGroup",
                        resource_id=sg_id,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Remove the 0.0.0.0/0 ingress rule on port 22 from '{sg_name}' "
                            "and restrict SSH access to authorized bastion CIDRs or AWS Systems Manager."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules.html",
                        metadata={"sg_name": sg_name, "port": 22, "cis_control": "4.1"},
                    )
                )

            if sg.get("has_open_rdp"):
                findings.append(
                    RawFinding(
                        rule_id="AWS-NET-002",
                        title=f"Security Group Allows Public Inbound RDP: {sg_name}",
                        description=(
                            f"Security group '{sg_name}' ({sg_id}) permits ingress on port 3389 (RDP) "
                            "from 0.0.0.0/0 or ::/0, creating severe remote access risks."
                        ),
                        severity=Severity.CRITICAL,
                        resource_type="AWS::EC2::SecurityGroup",
                        resource_id=sg_id,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Remove 0.0.0.0/0 rule on port 3389 for '{sg_name}' and route RDP "
                            "through a VPN or private bastion."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules.html",
                        metadata={"sg_name": sg_name, "port": 3389, "cis_control": "4.2"},
                    )
                )

        return findings

    def _check_all_traffic(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-NET-003: SG allows all inbound traffic from 0.0.0.0/0."""
        findings: list[RawFinding] = []
        sgs = resources.get("security_groups", [])

        for sg in sgs:
            if sg.get("allows_all_traffic"):
                sg_id = sg.get("id", "unknown")
                sg_name = sg.get("name", sg_id)
                region = sg.get("region", "global")
                arn = sg.get("arn") or f"arn:aws:ec2:{region}:::security-group/{sg_id}"

                findings.append(
                    RawFinding(
                        rule_id="AWS-NET-003",
                        title=f"Security Group Allows All Traffic From Internet: {sg_name}",
                        description=(
                            f"Security group '{sg_name}' ({sg_id}) allows all protocol traffic (-1) "
                            "from 0.0.0.0/0, completely disabling perimeter firewall protections."
                        ),
                        severity=Severity.CRITICAL,
                        resource_type="AWS::EC2::SecurityGroup",
                        resource_id=sg_id,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Immediately delete the universal ingress rule on '{sg_name}' and define "
                            "explicit ingress rules only for necessary ports."
                        ),
                        remediation_url="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules.html",
                        metadata={"sg_name": sg_name},
                    )
                )

        return findings

    def _check_default_vpc(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-NET-004: Usage of Default VPC."""
        findings: list[RawFinding] = []
        vpcs = resources.get("vpcs", [])

        for vpc in vpcs:
            if vpc.get("is_default"):
                vpc_id = vpc.get("id", "unknown")
                region = vpc.get("region", "global")
                findings.append(
                    RawFinding(
                        rule_id="AWS-NET-004",
                        title=f"Default VPC in Use ({region})",
                        description=(
                            f"Default VPC '{vpc_id}' is active in region {region}. Default VPCs have "
                            "open internet routing and default security groups, violating hardened posture."
                        ),
                        severity=Severity.LOW,
                        resource_type="AWS::EC2::VPC",
                        resource_id=vpc_id,
                        resource_arn=vpc.get("arn"),
                        region=region,
                        remediation="Migrate cloud workloads to custom VPCs with private subnets and NAT gateways.",
                        remediation_url="https://docs.aws.amazon.com/vpc/latest/userguide/default-vpc.html",
                        metadata={"vpc_id": vpc_id},
                    )
                )

        return findings

    def _check_public_subnets(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Rule AWS-NET-005: Auto-assign public IP enabled on subnet."""
        findings: list[RawFinding] = []
        subnets = resources.get("subnets", [])

        for s in subnets:
            if s.get("map_public_ip_on_launch"):
                sub_id = s.get("id", "unknown")
                region = s.get("region", "global")
                findings.append(
                    RawFinding(
                        rule_id="AWS-NET-005",
                        title=f"Subnet Auto-Assigns Public IPs: {sub_id}",
                        description=(
                            f"Subnet '{sub_id}' in {region} automatically assigns public IPv4 addresses "
                            "to newly launched EC2 instances, increasing exposure surface."
                        ),
                        severity=Severity.MEDIUM,
                        resource_type="AWS::EC2::Subnet",
                        resource_id=sub_id,
                        resource_arn=s.get("arn"),
                        region=region,
                        remediation=f"Modify subnet attribute for '{sub_id}' to disable auto-assign public IPv4.",
                        remediation_url="https://docs.aws.amazon.com/vpc/latest/userguide/vpc-ip-addressing.html#subnet-public-ip",
                        metadata={"subnet_id": sub_id},
                    )
                )

        return findings


__all__ = ["NetworkingAnalyzer"]
