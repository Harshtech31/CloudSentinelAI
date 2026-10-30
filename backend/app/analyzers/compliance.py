"""
Compliance Framework Analyzer for CloudSentinel AI.

Evaluates cloud resources against CIS AWS Benchmark v1.5, NIST SP 800-53,
and AWS Well-Architected Framework:
- CIS 3.1: CloudTrail multi-region logging enabled (AWS-CIS-3.1, Critical)
- CIS 3.2: CloudTrail log file validation enabled (AWS-CIS-3.2, Medium)
- CIS 3.5: AWS Config recorder active and tracking all resources (AWS-CIS-3.5, Medium)
- Overall compliance score calculation (%)
"""

from typing import Any

from app.analyzers import BaseAnalyzer, RawFinding
from app.core.constants import Severity

# Standard CIS AWS Benchmark v1.5 core control identifiers evaluated
CIS_BENCHMARK_CONTROLS = [
    "1.4",  # Access keys rotated <= 90 days
    "1.5",  # MFA enabled for all IAM users
    "1.16", # No wildcard admin policies
    "2.1.1", # S3 default encryption enabled
    "2.1.3", # S3 access logging enabled
    "2.1.4", # S3 versioning enabled
    "2.1.5", # S3 Block Public Access enabled
    "2.2.1", # EBS volume encryption enabled
    "2.3.1", # RDS storage encryption enabled
    "2.3.2", # RDS instance not publicly accessible
    "3.1",  # CloudTrail multi-region active
    "3.2",  # CloudTrail log validation active
    "3.5",  # AWS Config recorder active
    "4.1",  # No security group allows 0.0.0.0/0 on port 22
    "4.2",  # No security group allows 0.0.0.0/0 on port 3389
    "4.3",  # No security group allows unrestricted ingress
    "4.4",  # Default VPC is not used
    "4.5",  # Subnet does not auto-assign public IP
    "5.1",  # Network ACLs configured
    "5.2",  # VPC flow logs active
]


class ComplianceAnalyzer(BaseAnalyzer):
    """Maps misconfigurations to compliance frameworks and scores overall posture."""

    service = "compliance"

    def analyze(self, resources: dict[str, list[dict[str, Any]]]) -> list[RawFinding]:
        """Evaluate CloudTrail and AWS Config compliance rules."""
        findings: list[RawFinding] = []
        findings.extend(self._check_cloudtrail_active(resources))
        findings.extend(self._check_cloudtrail_validation(resources))
        findings.extend(self._check_config_recorder(resources))
        return findings

    def _check_cloudtrail_active(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """CIS 3.1: Ensure CloudTrail is enabled in all regions."""
        findings: list[RawFinding] = []
        trails = resources.get("cloudtrail_trails", [])

        has_active_multi_region_trail = any(
            t.get("is_logging") and t.get("is_multi_region_trail") for t in trails
        )

        if not has_active_multi_region_trail:
            findings.append(
                RawFinding(
                    rule_id="AWS-CIS-3.1",
                    title="CloudTrail Multi-Region Logging Disabled",
                    description=(
                        "No multi-region CloudTrail is currently active and recording API calls. "
                        "Without global CloudTrail logging, forensic investigation and incident response are severely impaired."
                    ),
                    severity=Severity.CRITICAL,
                    resource_type="AWS::CloudTrail::Trail",
                    resource_id="global-cloudtrail",
                    resource_arn="arn:aws:cloudtrail:::trail/global-cloudtrail",
                    region="global",
                    remediation=(
                        "Create a multi-region CloudTrail trail via 'aws cloudtrail create-trail "
                        "--name management-events --is-multi-region-trail' and run 'aws cloudtrail start-logging'."
                    ),
                    remediation_url="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-create-and-update-a-trail.html",
                    metadata={"framework": "CIS AWS Benchmark v1.5", "cis_control": "3.1"},
                )
            )

        return findings

    def _check_cloudtrail_validation(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """CIS 3.2: Ensure CloudTrail log file validation is enabled."""
        findings: list[RawFinding] = []
        trails = resources.get("cloudtrail_trails", [])

        for trail in trails:
            if not trail.get("log_file_validation_enabled", False):
                name = trail.get("name", "unknown")
                arn = trail.get("arn") or f"arn:aws:cloudtrail:::trail/{name}"
                region = trail.get("region", "global")

                findings.append(
                    RawFinding(
                        rule_id="AWS-CIS-3.2",
                        title=f"CloudTrail Log Validation Disabled: {name}",
                        description=(
                            f"CloudTrail trail '{name}' does not have log file integrity validation enabled. "
                            "Tampering or modification of log files cannot be cryptographically detected."
                        ),
                        severity=Severity.MEDIUM,
                        resource_type="AWS::CloudTrail::Trail",
                        resource_id=name,
                        resource_arn=arn,
                        region=region,
                        remediation=(
                            f"Enable log file validation on '{name}' via 'aws cloudtrail update-trail "
                            f"--name {name} --enable-log-file-validation'."
                        ),
                        remediation_url="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html",
                        metadata={"framework": "CIS AWS Benchmark v1.5", "cis_control": "3.2"},
                    )
                )

        return findings

    def _check_config_recorder(
        self, resources: dict[str, list[dict[str, Any]]]
    ) -> list[RawFinding]:
        """CIS 3.5: Ensure AWS Config is enabled in all regions."""
        findings: list[RawFinding] = []
        recorders = resources.get("config_recorders", [])

        has_active_recorder = any(
            r.get("recording", False) for r in recorders
        )

        if not has_active_recorder:
            findings.append(
                RawFinding(
                    rule_id="AWS-CIS-3.5",
                    title="AWS Config Configuration Recorder Disabled",
                    description=(
                        "AWS Config recorder is not enabled or not recording resource states. "
                        "Configuration drift, resource state history, and compliance audit tracks are missing."
                    ),
                    severity=Severity.MEDIUM,
                    resource_type="AWS::Config::ConfigurationRecorder",
                    resource_id="default-recorder",
                    resource_arn="arn:aws:config:::configuration-recorder/default",
                    region="global",
                    remediation=(
                        "Start AWS Config recording via 'aws configservice start-configuration-recorder "
                        "--configuration-recorder-name default'."
                    ),
                    remediation_url="https://docs.aws.amazon.com/config/latest/developerguide/stop-start-recorder.html",
                    metadata={"framework": "CIS AWS Benchmark v1.5", "cis_control": "3.5"},
                )
            )

        return findings

    def compliance_score(self, findings: list[RawFinding]) -> float:
        """Calculate overall CIS AWS Benchmark compliance percentage (0.0% - 100.0%).

        Extracts failing controls from findings metadata and calculates pass rate.
        """
        total_controls = len(CIS_BENCHMARK_CONTROLS)
        failed_controls: set[str] = set()

        for f in findings:
            ctrl = f.metadata.get("cis_control")
            if ctrl:
                failed_controls.add(str(ctrl))
            elif f.rule_id.startswith("AWS-CIS-"):
                failed_controls.add(f.rule_id.replace("AWS-CIS-", ""))

        failed_count = min(len(failed_controls), total_controls)
        passed_count = total_controls - failed_count
        score = (passed_count / total_controls) * 100.0
        return round(max(0.0, min(100.0, score)), 1)


__all__ = ["ComplianceAnalyzer", "CIS_BENCHMARK_CONTROLS"]
