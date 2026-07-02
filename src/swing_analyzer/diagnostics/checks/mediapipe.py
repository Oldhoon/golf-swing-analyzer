from __future__ import annotations

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.version import version_meets_minimum
from swing_analyzer.models.capability import (
    CAPABILITY_SEVERITY,
    CapabilityCheckResult,
    CapabilityName,
    CapabilityStatus,
)


def check_mediapipe(config: ApplicationConfiguration) -> CapabilityCheckResult:
    name = CapabilityName.MEDIAPIPE
    severity = CAPABILITY_SEVERITY[name]
    minimum = config.mediapipe_minimum_version

    try:
        import mediapipe as mp
    except ImportError:
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            minimum_version=minimum,
            message="MediaPipe is not importable",
            remediation="Run `uv sync` to install mediapipe",
        )

    detected = getattr(mp, "__version__", "0.10.0")
    if not version_meets_minimum(detected, minimum):
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            detected_version=detected,
            minimum_version=minimum,
            message=f"MediaPipe {detected} is below minimum {minimum}",
            remediation=f"Upgrade mediapipe to meet minimum {minimum}",
        )

    return CapabilityCheckResult(
        name=name,
        severity=severity,
        status=CapabilityStatus.PASS,
        detected_version=detected,
        minimum_version=minimum,
        message=f"MediaPipe {detected} meets minimum {minimum}",
    )
