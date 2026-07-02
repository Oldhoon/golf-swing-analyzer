from __future__ import annotations

import importlib.metadata
from unittest.mock import MagicMock, patch

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.checks.ffmpeg import check_ffmpeg
from swing_analyzer.diagnostics.checks.mediapipe import check_mediapipe
from swing_analyzer.diagnostics.checks.opencv import check_opencv
from swing_analyzer.models.capability import CapabilityStatus


def test_ffmpeg_command_failure(config: ApplicationConfiguration) -> None:
    completed = MagicMock()
    completed.returncode = 1
    completed.stdout = ""
    with patch("subprocess.run", return_value=completed):
        result = check_ffmpeg(config)
    assert result.status == CapabilityStatus.FAIL


def test_ffmpeg_unparseable_version(config: ApplicationConfiguration) -> None:
    completed = MagicMock()
    completed.returncode = 0
    completed.stdout = "unknown output"
    with patch("subprocess.run", return_value=completed):
        result = check_ffmpeg(config)
    assert result.status == CapabilityStatus.FAIL


def test_ffmpeg_version_too_low(config: ApplicationConfiguration) -> None:
    completed = MagicMock()
    completed.returncode = 0
    completed.stdout = "ffmpeg version 5.0.0 Copyright"
    with patch("subprocess.run", return_value=completed):
        result = check_ffmpeg(config)
    assert result.status == CapabilityStatus.FAIL


def test_opencv_version_too_low(config: ApplicationConfiguration) -> None:
    fake_cv2 = MagicMock()
    fake_cv2.__version__ = "4.0.0"
    with patch.dict("sys.modules", {"cv2": fake_cv2}):
        result = check_opencv(config)
    assert result.status == CapabilityStatus.FAIL


def test_mediapipe_import_fail(config: ApplicationConfiguration) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "mediapipe":
            raise ImportError("no mediapipe")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        result = check_mediapipe(config)
    assert result.status == CapabilityStatus.FAIL


def test_mediapipe_version_too_low(config: ApplicationConfiguration) -> None:
    fake_mp = MagicMock()
    fake_mp.__version__ = "0.9.0"
    with patch.dict("sys.modules", {"mediapipe": fake_mp}):
        result = check_mediapipe(config)
    assert result.status == CapabilityStatus.FAIL


def test_mediapipe_fail_when_version_unknown(config: ApplicationConfiguration) -> None:
    fake_mp = MagicMock(spec=[])
    with (
        patch.dict("sys.modules", {"mediapipe": fake_mp}),
        patch(
            "swing_analyzer.diagnostics.checks.mediapipe.importlib.metadata.version",
            side_effect=importlib.metadata.PackageNotFoundError("mediapipe"),
        ),
    ):
        result = check_mediapipe(config)
    assert result.status == CapabilityStatus.FAIL
    assert "Could not determine MediaPipe version" in result.message


def test_mediapipe_uses_package_metadata_when_module_version_missing(
    config: ApplicationConfiguration,
) -> None:
    fake_mp = MagicMock(spec=[])
    with (
        patch.dict("sys.modules", {"mediapipe": fake_mp}),
        patch(
            "swing_analyzer.diagnostics.checks.mediapipe.importlib.metadata.version",
            return_value="0.10.35",
        ),
    ):
        result = check_mediapipe(config)
    assert result.status == CapabilityStatus.PASS
    assert result.detected_version == "0.10.35"
