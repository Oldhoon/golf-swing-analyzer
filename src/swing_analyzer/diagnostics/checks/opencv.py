from __future__ import annotations

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.version import version_meets_minimum
from swing_analyzer.models.capability import (
    CAPABILITY_SEVERITY,
    CapabilityCheckResult,
    CapabilityName,
    CapabilityStatus,
)


def check_opencv(config: ApplicationConfiguration) -> CapabilityCheckResult:
    name = CapabilityName.OPENCV
    severity = CAPABILITY_SEVERITY[name]
    minimum = config.opencv_minimum_version

    try:
        import cv2
    except ImportError:
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            minimum_version=minimum,
            message="OpenCV (cv2) is not importable",
            remediation="Run `uv sync` to install opencv-python",
        )

    detected = cv2.__version__
    if not version_meets_minimum(detected, minimum):
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            detected_version=detected,
            minimum_version=minimum,
            message=f"OpenCV {detected} is below minimum {minimum}",
            remediation=f"Upgrade opencv-python to meet minimum {minimum}",
        )

    return CapabilityCheckResult(
        name=name,
        severity=severity,
        status=CapabilityStatus.PASS,
        detected_version=detected,
        minimum_version=minimum,
        message=f"OpenCV {detected} meets minimum {minimum}",
    )
