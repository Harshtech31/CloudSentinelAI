"""
Collector registry wiring for CloudSentinel AI.

Bridges Member 2's collector implementations into the scan orchestrator's
registry. Importing this module registers every AWS service collector so
`POST /scan/start` resolves real collectors instead of skipping services.

Stub collectors (Phase 1) return empty structured results, so scans
complete honestly with zero resources until Member 2's Phase 2 boto3
implementations land — registration means "available to the pipeline",
not "able to reach AWS".
"""

from app.collectors.aws.cloudtrail import CloudTrailCollector
from app.collectors.aws.config import AWSConfigCollector
from app.collectors.aws.ec2 import EC2Collector
from app.collectors.aws.iam import IAMCollector
from app.collectors.aws.rds import RDSCollector
from app.collectors.aws.s3 import S3Collector
from app.collectors.aws.security_groups import SecurityGroupCollector
from app.collectors.aws.vpc import VPCCollector
from app.tasks.scan_task import register_collector


def register_default_collectors() -> None:
    """Register every AWS service collector with the orchestrator.

    Service keys match the default `services` list in ScanStartRequest
    and the frontend's service picker — keep them in sync.
    """
    register_collector("iam", IAMCollector)
    register_collector("ec2", EC2Collector)
    register_collector("s3", S3Collector)
    register_collector("vpc", VPCCollector)
    register_collector("security_groups", SecurityGroupCollector)
    register_collector("rds", RDSCollector)
    register_collector("cloudtrail", CloudTrailCollector)
    register_collector("config", AWSConfigCollector)


__all__ = ["register_default_collectors"]
