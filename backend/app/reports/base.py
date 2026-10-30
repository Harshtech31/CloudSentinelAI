"""
Base abstractions and payload model for CloudSentinel AI report generation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.core.constants import ReportFormat


@dataclass
class ScanReportData:
    """Format-agnostic report payload assembled by the scan pipeline."""

    scan_id: str
    account_id: str = "unknown"
    provider: str = "aws"
    generated_at: str = ""
    risk_score: float = 0.0
    compliance_score: float = 0.0
    summary: dict[str, Any] = field(default_factory=dict)
    findings: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)


class BaseRenderer(ABC):
    """Contract for one export format."""

    fmt: ReportFormat

    @abstractmethod
    def render(self, data: ScanReportData) -> bytes:
        """Serialize the report payload to bytes."""
        raise NotImplementedError
