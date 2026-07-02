from __future__ import annotations

from swing_analyzer.models.capability import (
    CapabilityCheckResult,
    CapabilityName,
    CapabilitySeverity,
    CapabilityStatus,
)
from swing_analyzer.models.diagnostic import EnvironmentDiagnosticReport, OverallStatus


def _check(
    name: CapabilityName,
    severity: CapabilitySeverity,
    status: CapabilityStatus,
) -> CapabilityCheckResult:
    remediation = "fix it" if status in (CapabilityStatus.FAIL, CapabilityStatus.WARNING) else None
    return CapabilityCheckResult(
        name=name,
        severity=severity,
        status=status,
        message=f"{name.value} is {status.value}",
        remediation=remediation,
    )


def test_overall_status_pass_when_all_pass() -> None:
    checks = [
        _check(CapabilityName.GPU, CapabilitySeverity.RECOMMENDED, CapabilityStatus.PASS),
        _check(CapabilityName.FFMPEG, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.OPENCV, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.MEDIAPIPE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.STORAGE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
    ]
    assert EnvironmentDiagnosticReport.derive_overall_status(checks) == OverallStatus.PASS


def test_overall_status_pass_with_warnings_when_gpu_warns() -> None:
    checks = [
        _check(CapabilityName.GPU, CapabilitySeverity.RECOMMENDED, CapabilityStatus.WARNING),
        _check(CapabilityName.FFMPEG, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.OPENCV, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.MEDIAPIPE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.STORAGE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
    ]
    status = EnvironmentDiagnosticReport.derive_overall_status(checks)
    assert status == OverallStatus.PASS_WITH_WARNINGS


def test_overall_status_fail_when_mandatory_fails() -> None:
    checks = [
        _check(CapabilityName.GPU, CapabilitySeverity.RECOMMENDED, CapabilityStatus.PASS),
        _check(CapabilityName.FFMPEG, CapabilitySeverity.MANDATORY, CapabilityStatus.FAIL),
        _check(CapabilityName.OPENCV, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.MEDIAPIPE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.STORAGE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
    ]
    assert EnvironmentDiagnosticReport.derive_overall_status(checks) == OverallStatus.FAIL


def test_performance_targets_waived_when_gpu_warning() -> None:
    checks = [
        _check(CapabilityName.GPU, CapabilitySeverity.RECOMMENDED, CapabilityStatus.WARNING),
        _check(CapabilityName.FFMPEG, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.OPENCV, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.MEDIAPIPE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.STORAGE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
    ]
    assert EnvironmentDiagnosticReport.performance_targets_waived_from_checks(checks) is True


def test_performance_targets_not_waived_when_gpu_passes() -> None:
    checks = [
        _check(CapabilityName.GPU, CapabilitySeverity.RECOMMENDED, CapabilityStatus.PASS),
        _check(CapabilityName.FFMPEG, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.OPENCV, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.MEDIAPIPE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
        _check(CapabilityName.STORAGE, CapabilitySeverity.MANDATORY, CapabilityStatus.PASS),
    ]
    assert EnvironmentDiagnosticReport.performance_targets_waived_from_checks(checks) is False
