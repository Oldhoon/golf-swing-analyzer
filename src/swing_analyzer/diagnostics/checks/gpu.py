from __future__ import annotations

import subprocess

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.models.capability import (
    CAPABILITY_SEVERITY,
    CapabilityCheckResult,
    CapabilityName,
    CapabilityStatus,
)


def check_gpu(_config: ApplicationConfiguration) -> CapabilityCheckResult:
    name = CapabilityName.GPU
    severity = CAPABILITY_SEVERITY[name]

    detected_version, message = _probe_gpu()
    if detected_version is not None:
        return CapabilityCheckResult(
            name=name,
            severity=severity,
            status=CapabilityStatus.PASS,
            detected_version=detected_version,
            message=message,
        )

    return CapabilityCheckResult(
        name=name,
        severity=severity,
        status=CapabilityStatus.WARNING,
        message=message,
        remediation="Install Nvidia drivers for GPU acceleration, or continue in CPU warning mode",
    )


def _probe_gpu() -> tuple[str | None, str]:
    try:
        import pynvml

        pynvml.nvmlInit()
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count < 1:
                return None, "No Nvidia GPU devices detected"
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name = pynvml.nvmlDeviceGetName(handle)
            driver = pynvml.nvmlSystemGetDriverVersion()
            device_name = name.decode() if isinstance(name, bytes) else str(name)
            driver_version = driver.decode() if isinstance(driver, bytes) else str(driver)
            return driver_version, f"Nvidia GPU available ({device_name}, driver {driver_version})"
        finally:
            pynvml.nvmlShutdown()
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version,name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            line = result.stdout.strip().splitlines()[0]
            parts = [part.strip() for part in line.split(",")]
            driver = parts[0] if parts else "unknown"
            device_name = parts[1] if len(parts) > 1 else "Nvidia GPU"
            return driver, f"Nvidia GPU available ({device_name}, driver {driver})"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None, "No Nvidia GPU acceleration detected"
