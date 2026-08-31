"""
Core constants and enumerations for CloudSentinel AI.
"""

from enum import StrEnum


class Severity(StrEnum):
    """Vulnerability and finding severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanStatus(StrEnum):
    """Lifecycle status of a cloud infrastructure security scan."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CloudProvider(StrEnum):
    """Supported cloud infrastructure providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class UserRole(StrEnum):
    """Role-based access control roles."""

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class ReportFormat(StrEnum):
    """Export report formats."""

    JSON = "json"
    CSV = "csv"
    HTML = "html"
    PDF = "pdf"


class AssetType(StrEnum):
    """Recognized cloud asset types."""

    IAM_USER = "iam_user"
    IAM_ROLE = "iam_role"
    IAM_POLICY = "iam_policy"
    EC2_INSTANCE = "ec2_instance"
    S3_BUCKET = "s3_bucket"
    SECURITY_GROUP = "security_group"
    VPC = "vpc"
    SUBNET = "subnet"
    RDS_INSTANCE = "rds_instance"
    CLOUDTRAIL = "cloudtrail"
    INTERNET = "internet"


# Default App Metadata
APP_VERSION = "0.1.0"
APP_NAME = "CloudSentinel AI"
DEFAULT_SCAN_TIMEOUT_SECONDS = 3600
DEFAULT_PAGINATION_LIMIT = 50
MAX_PAGINATION_LIMIT = 200
