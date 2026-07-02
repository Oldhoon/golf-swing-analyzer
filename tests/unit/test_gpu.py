from __future__ import annotations

from unittest.mock import MagicMock, patch

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.checks.gpu import _probe_gpu, check_gpu
from swing_analyzer.models.capability import CapabilityStatus


def test_probe_gpu_no_devices_via_pynvml() -> None:
    fake_pynvml = type(
        "NVML",
        (),
        {
            "nvmlInit": staticmethod(lambda: None),
            "nvmlShutdown": staticmethod(lambda: None),
            "nvmlDeviceGetCount": staticmethod(lambda: 0),
        },
    )()
    with patch.dict("sys.modules", {"pynvml": fake_pynvml}):
        version, message = _probe_gpu()
    assert version is None
    assert "No Nvidia GPU devices" in message


def test_probe_gpu_via_nvidia_smi() -> None:
    completed = MagicMock()
    completed.returncode = 0
    completed.stdout = "550.54.15, NVIDIA GeForce RTX 3080\n"

    with (
        patch("swing_analyzer.diagnostics.checks.gpu.subprocess.run", return_value=completed),
        patch.dict("sys.modules", {"pynvml": None}),
    ):
        version, message = _probe_gpu()

    assert version == "550.54.15"
    assert "RTX 3080" in message


def test_probe_gpu_nvidia_smi_not_found() -> None:
    with (
        patch(
            "swing_analyzer.diagnostics.checks.gpu.subprocess.run",
            side_effect=FileNotFoundError,
        ),
        patch.dict("sys.modules", {"pynvml": None}),
    ):
        version, message = _probe_gpu()

    assert version is None
    assert "No Nvidia GPU" in message


def test_check_gpu_passes_when_probe_succeeds(config: ApplicationConfiguration) -> None:
    with patch(
        "swing_analyzer.diagnostics.checks.gpu._probe_gpu",
        return_value=("550.0", "gpu ok"),
    ):
        result = check_gpu(config)
    assert result.status == CapabilityStatus.PASS
    assert result.detected_version == "550.0"
