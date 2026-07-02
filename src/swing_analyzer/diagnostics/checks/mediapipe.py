from __future__ import annotations

import importlib.metadata

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.version import version_meets_minimum
from swing_analyzer.models.capability import (
    CAPABILITY_SEVERITY,
    CapabilityCheckResult,
    CapabilityName,
    CapabilityStatus,
)


def _detect_mediapipe_version(mp: object) -> str | None:
    module_version = getattr(mp, "__version__", None)
    if module_version:
        return str(module_version)
    try:
        return importlib.metadata.version("mediapipe")
    except importlib.metadata.PackageNotFoundError:
        return None


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

    detected = _detect_mediapipe_version(mp)
    if detected is None:
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            minimum_version=minimum,
            message="Could not determine MediaPipe version",
            remediation="Reinstall mediapipe in the project virtual environment",
        )

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
