from __future__ import annotations

from unittest.mock import MagicMock, patch

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.checks.ffmpeg import check_ffmpeg
from swing_analyzer.diagnostics.checks.gpu import check_gpu
from swing_analyzer.diagnostics.checks.mediapipe import check_mediapipe
from swing_analyzer.diagnostics.checks.opencv import check_opencv
from swing_analyzer.diagnostics.checks.storage import check_storage
from swing_analyzer.models.capability import CapabilityName, CapabilityStatus


def test_gpu_warning_when_no_device(config: ApplicationConfiguration) -> None:
    with patch("swing_analyzer.diagnostics.checks.gpu._probe_gpu", return_value=(None, "no gpu")):
        result = check_gpu(config)
    assert result.name == CapabilityName.GPU
    assert result.status == CapabilityStatus.WARNING
    assert result.status != CapabilityStatus.FAIL


def test_gpu_pass_when_detected(config: ApplicationConfiguration) -> None:
    with patch(
        "swing_analyzer.diagnostics.checks.gpu._probe_gpu",
        return_value=("550.0", "gpu ok"),
    ):
        result = check_gpu(config)
    assert result.status == CapabilityStatus.PASS


def test_ffmpeg_fail_when_missing(config: ApplicationConfiguration) -> None:
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = check_ffmpeg(config)
    assert result.status == CapabilityStatus.FAIL
    assert result.remediation


def test_ffmpeg_pass_when_version_ok(config: ApplicationConfiguration) -> None:
    completed = MagicMock()
    completed.returncode = 0
    completed.stdout = "ffmpeg version 6.1.1 Copyright"
    with patch("subprocess.run", return_value=completed):
        result = check_ffmpeg(config)
    assert result.status == CapabilityStatus.PASS


def test_opencv_fail_on_import_error(config: ApplicationConfiguration) -> None:
    with (
        patch.dict("sys.modules", {"cv2": None}),
        patch(
            "swing_analyzer.diagnostics.checks.opencv.check_opencv",
            wraps=check_opencv,
        ),
    ):
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "cv2":
                raise ImportError("no cv2")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            result = check_opencv(config)
    assert result.status == CapabilityStatus.FAIL


def test_mediapipe_pass_with_version(config: ApplicationConfiguration) -> None:
    fake_mp = MagicMock()
    fake_mp.__version__ = "0.10.14"
    with patch.dict("sys.modules", {"mediapipe": fake_mp}):
        result = check_mediapipe(config)
    assert result.status == CapabilityStatus.PASS


def test_storage_pass_when_writable(config: ApplicationConfiguration) -> None:
    result = check_storage(config)
    assert result.status == CapabilityStatus.PASS


def test_storage_fail_when_not_writable(config: ApplicationConfiguration) -> None:
    config.data_dir = config.data_dir / "nested" / "path"
    with patch.object(type(config.data_dir), "mkdir", side_effect=OSError("permission denied")):
        result = check_storage(config)
    assert result.status == CapabilityStatus.FAIL
