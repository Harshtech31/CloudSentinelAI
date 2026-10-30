"""
AWS Config Collector for CloudSentinel AI.

Enumerates AWS Config configuration recorders and delivery channels across
configured AWS regions to assess continuous posture monitoring.
"""

from typing import Any

from botocore.exceptions import BotoCoreError, ClientError

from app.collectors.aws import get_aws_client
from app.collectors.base import BaseCollector
from app.core.config import settings
from app.core.logging import logger


class AWSConfigCollector(BaseCollector):
    """Collects AWS Config recorder status from AWS regions."""

    provider = "aws"

    def __init__(self, regions: list[str] | None = None) -> None:
        super().__init__(regions=regions or [settings.AWS_DEFAULT_REGION])

    def collect(self) -> dict[str, list[dict[str, Any]]]:
        """Collect AWS Config recorders across configured regions."""
        recorders: list[dict[str, Any]] = []

        for region in self.regions:
            try:
                cfg = get_aws_client("config", region=region)
                rec_res = cfg.describe_configuration_recorders()
                status_res = {}
                try:
                    status_res = {
                        s.get("name"): s
                        for s in cfg.describe_configuration_recorder_status().get(
                            "ConfigurationRecordersStatus", []
                        )
                    }
                except (ClientError, BotoCoreError):
                    pass

                for rec in rec_res.get("ConfigurationRecorders", []):
                    name = rec.get("name", "default")
                    rec_status = status_res.get(name, {})
                    is_recording = rec_status.get("recording", False)
                    last_status = rec_status.get("lastStatus", "unknown")

                    recorders.append(
                        {
                            "id": name,
                            "name": name,
                            "arn": f"arn:aws:config:{region}:::config-recorder/{name}",
                            "region": region,
                            "role_arn": rec.get("roleARN"),
                            "recording_group": rec.get("recordingGroup", {}),
                            "is_recording": is_recording,
                            "last_status": last_status,
                        }
                    )
            except Exception as exc:
                logger.warning("Error collecting AWS Config in %s: %s", region, exc)

        self.record("config_recorders", recorders)
        return self.resources


__all__ = ["AWSConfigCollector"]
