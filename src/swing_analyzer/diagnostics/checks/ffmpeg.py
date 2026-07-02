from __future__ import annotations

import subprocess

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.version import version_meets_minimum
from swing_analyzer.models.capability import (
    CAPABILITY_SEVERITY,
    CapabilityCheckResult,
    CapabilityName,
    CapabilityStatus,
)


def check_ffmpeg(config: ApplicationConfiguration) -> CapabilityCheckResult:
    name = CapabilityName.FFMPEG
    severity = CAPABILITY_SEVERITY[name]
    minimum = config.ffmpeg_minimum_version

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            minimum_version=minimum,
            message="FFmpeg not found on PATH",
            remediation="Install FFmpeg 6.0+ (e.g. sudo dnf install ffmpeg)",
        )

    if result.returncode != 0:
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            minimum_version=minimum,
            message="FFmpeg command failed",
            remediation="Install FFmpeg 6.0+ and ensure it is on PATH",
        )

    first_line = result.stdout.splitlines()[0] if result.stdout else ""
    detected = _extract_ffmpeg_version(first_line)
    if detected is None:
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            detected_version=None,
            minimum_version=minimum,
            message="Could not parse FFmpeg version",
            remediation="Install a supported FFmpeg release (6.0+)",
        )

    if not version_meets_minimum(detected, minimum):
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            detected_version=detected,
            minimum_version=minimum,
            message=f"FFmpeg {detected} is below minimum {minimum}",
            remediation=f"Upgrade FFmpeg to {minimum} or newer",
        )

    return CapabilityCheckResult(
        name=name,
        severity=severity,
        status=CapabilityStatus.PASS,
        detected_version=detected,
        minimum_version=minimum,
        message=f"FFmpeg {detected} meets minimum {minimum}",
    )


def _extract_ffmpeg_version(first_line: str) -> str | None:
    # Example: ffmpeg version 6.1.1 Copyright ...
    parts = first_line.split()
    for index, part in enumerate(parts):
        if part == "version" and index + 1 < len(parts):
            return parts[index + 1].rstrip(",")
    return None
