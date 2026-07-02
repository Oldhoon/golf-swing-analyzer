from __future__ import annotations

import uuid

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.models.capability import (
    CAPABILITY_SEVERITY,
    CapabilityCheckResult,
    CapabilityName,
    CapabilityStatus,
)


def check_storage(config: ApplicationConfiguration) -> CapabilityCheckResult:
    name = CapabilityName.STORAGE
    severity = CAPABILITY_SEVERITY[name]
    data_dir = config.data_dir

    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / f".write_probe_{uuid.uuid4().hex}"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.FAIL,
            message=f"Storage not writable at {data_dir}: {exc}",
            remediation="Ensure data_dir exists and is writable; check disk space and permissions",
        )

    return CapabilityCheckResult(
        name=name,
        severity=severity,
        status=CapabilityStatus.PASS,
        message=f"Local storage writable at {data_dir}",
    )
