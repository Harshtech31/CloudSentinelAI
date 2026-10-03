"""Schema sanity tests for the Phase 2 additive scan schemas (roadmap task 15).

The mappers are exercised end-to-end in the integration suite; these tests
pin the serialization contract itself (field names, enum passthrough,
comma-splitting, duration computation) so accidental breakage of the
frontend contract fails fast.
"""

from datetime import UTC, datetime, timedelta

from app.core.constants import CloudProvider, ScanStatus
from app.schemas.scan import ScanStartRequest, scan_to_list_item


class _FakeScan:
    """Duck-typed stand-in for the Scan ORM row."""

    def __init__(self, **kwargs) -> None:
        defaults = dict(
            id="scn_abc123",
            status=ScanStatus.COMPLETED,
            target_cloud=CloudProvider.AWS,
            regions="us-east-1,us-west-2",
            services="iam,s3",
            progress_percentage=100,
            created_at=datetime.now(UTC),
            started_at=None,
            completed_at=None,
            error_message=None,
        )
        defaults.update(kwargs)
        for key, value in defaults.items():
            setattr(self, key, value)


class TestScanToListItem:
    def test_maps_core_fields(self) -> None:
        item = scan_to_list_item(_FakeScan())
        assert item.scan_id == "scn_abc123"
        assert item.status == ScanStatus.COMPLETED
        assert item.target_cloud == CloudProvider.AWS
        assert item.regions == ["us-east-1", "us-west-2"]
        assert item.services == ["iam", "s3"]
        assert item.progress_percentage == 100

    def test_duration_computed_from_timestamps(self) -> None:
        start = datetime.now(UTC)
        item = scan_to_list_item(
            _FakeScan(started_at=start, completed_at=start + timedelta(seconds=90))
        )
        assert item.duration_seconds == 90.0

    def test_duration_none_when_not_started(self) -> None:
        item = scan_to_list_item(_FakeScan())
        assert item.duration_seconds is None

    def test_error_message_passthrough(self) -> None:
        item = scan_to_list_item(_FakeScan(error_message="boom"))
        assert item.error_message == "boom"


class TestExistingContract:
    def test_scan_start_request_defaults(self) -> None:
        payload = ScanStartRequest()
        assert payload.target_cloud == CloudProvider.AWS
        assert "iam" in payload.services
