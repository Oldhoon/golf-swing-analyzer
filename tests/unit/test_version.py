from __future__ import annotations

import pytest

from swing_analyzer.diagnostics.version import (
    compare_versions,
    parse_version,
    version_meets_minimum,
)
from swing_analyzer.models.capability import (
    CapabilityCheckResult,
    CapabilityName,
    CapabilitySeverity,
    CapabilityStatus,
)


def test_parse_version_extracts_numeric_parts() -> None:
    assert parse_version("ffmpeg version 6.1.1") == (6, 1, 1)


def test_compare_versions_ordering() -> None:
    assert compare_versions("6.1.0", "6.0.0") == 1
    assert compare_versions("5.9.0", "6.0.0") == -1
    assert compare_versions("6.0.0", "6.0.0") == 0


def test_version_meets_minimum_true() -> None:
    assert version_meets_minimum("4.10.0", "4.8.0") is True


def test_parse_version_invalid_raises() -> None:
    with pytest.raises(ValueError):
        parse_version("no digits")


def test_capability_pass_rejects_remediation() -> None:
    with pytest.raises(ValueError):
        CapabilityCheckResult(
            name=CapabilityName.GPU,
            severity=CapabilitySeverity.RECOMMENDED,
            status=CapabilityStatus.PASS,
            message="ok",
            remediation="should not be set",
        )


def test_capability_fail_requires_mandatory_severity() -> None:
    with pytest.raises(ValueError, match="mandatory severity"):
        CapabilityCheckResult(
            name=CapabilityName.GPU,
            severity=CapabilitySeverity.RECOMMENDED,
            status=CapabilityStatus.FAIL,
            message="bad",
            remediation="fix",
        )


def test_capability_fail_requires_remediation() -> None:
    with pytest.raises(ValueError, match="remediation"):
        CapabilityCheckResult(
            name=CapabilityName.FFMPEG,
            severity=CapabilitySeverity.MANDATORY,
            status=CapabilityStatus.FAIL,
            message="bad",
        )


def test_capability_warning_requires_recommended_severity() -> None:
    with pytest.raises(ValueError, match="recommended severity"):
        CapabilityCheckResult(
            name=CapabilityName.FFMPEG,
            severity=CapabilitySeverity.MANDATORY,
            status=CapabilityStatus.WARNING,
            message="warn",
            remediation="fix",
        )
