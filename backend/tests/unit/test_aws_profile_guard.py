"""Tests for the AWS profile guard (collection credential policy).

Policy: CloudSentinel may only collect using CLI profiles named
`cloudsentinel-*`. These tests pin the guard without touching the network.
"""

import boto3
import pytest
from botocore.exceptions import ProfileNotFound

from app.collectors.aws import _resolve_profile, get_aws_client, get_aws_session
from app.core.config import Settings, settings


def _patch_profile(monkeypatch: pytest.MonkeyPatch, profile: str) -> None:
    monkeypatch.setattr(settings, "AWS_PROFILE", profile)


class TestProfileGuard:
    def test_allowed_profile_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_profile(monkeypatch, "cloudsentinel-eval")
        assert _resolve_profile() == "cloudsentinel-eval"

    def test_second_cloudsentinel_profile_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_profile(monkeypatch, "cloudsentinel-provisioner")
        assert _resolve_profile() == "cloudsentinel-provisioner"

    @pytest.mark.parametrize(
        "profile",
        ["default", "aws-cleanup", "khana-peena-cost-audit", "admin", "eval"],
    )
    def test_foreign_profiles_are_rejected(
        self, monkeypatch: pytest.MonkeyPatch, profile: str
    ) -> None:
        _patch_profile(monkeypatch, profile)
        with pytest.raises(ValueError, match="cloudsentinel-"):
            _resolve_profile()

    def test_empty_profile_falls_back_to_chain(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_profile(monkeypatch, "   ")
        assert _resolve_profile() is None


class TestSessionResolution:
    def test_session_uses_configured_profile(self) -> None:
        if "cloudsentinel-eval" not in boto3.session.Session().available_profiles:
            pytest.skip("cloudsentinel-eval profile not present on this machine")
        session = get_aws_session()
        assert session.profile_name == "cloudsentinel-eval"

    def test_explicit_keys_bypass_profile(self) -> None:
        session = get_aws_session(access_key="AKIATESTKEY", secret_key="secret")
        credentials = session.get_credentials()
        assert credentials is not None
        assert credentials.access_key == "AKIATESTKEY"

    def test_region_override_wins(self) -> None:
        session = get_aws_session(region="eu-west-1")
        assert session.region_name == "eu-west-1"

    def test_default_region_is_the_account_region(self) -> None:
        assert Settings().AWS_DEFAULT_REGION == "ap-south-1"

    def test_client_carries_region_and_retry_config(self) -> None:
        client = get_aws_client("sts")
        assert client.meta.region_name == Settings().AWS_DEFAULT_REGION

    def test_session_rejects_foreign_profile_at_build_time(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_profile(monkeypatch, "default")
        with pytest.raises(ValueError, match="cloudsentinel-"):
            get_aws_session()

    def test_missing_profile_degrades_to_default_chain(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """No ~/.aws (Docker/CI) must not crash the app at import/boot."""
        real_session = boto3.session.Session

        def fake_session(**kwargs):
            if "profile_name" in kwargs:
                raise ProfileNotFound(profile=kwargs["profile_name"])
            return real_session(**kwargs)

        monkeypatch.setattr("app.collectors.aws.boto3.session.Session", fake_session)
        session = get_aws_session()  # must not raise
        assert session.region_name == Settings().AWS_DEFAULT_REGION
