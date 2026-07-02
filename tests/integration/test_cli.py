from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from swing_analyzer.cli import app
from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.report import report_to_json
from swing_analyzer.diagnostics.runner import run_diagnostics
from swing_analyzer.logging.setup import configure_logging, get_logger
from swing_analyzer.models.diagnostic import (
    EffectiveConfigSummary,
    EnvironmentDiagnosticReport,
    OverallStatus,
)

runner = CliRunner()


def _fast_report(tmp_path: Path) -> EnvironmentDiagnosticReport:
    data_dir = tmp_path / "data"
    return EnvironmentDiagnosticReport(
        overall_status=OverallStatus.PASS,
        performance_targets_waived=False,
        checks=[],
        effective_config_summary=EffectiveConfigSummary(
            data_dir=str(data_dir),
            log_dir=str(data_dir / "logs"),
            config_file=None,
        ),
    )


def test_diagnose_command_outputs_json(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    data_dir = tmp_path / "data"
    config_path.write_text(f'data_dir = "{data_dir}"\n', encoding="utf-8")

    with patch("swing_analyzer.cli.run_diagnostics", return_value=_fast_report(tmp_path)):
        result = runner.invoke(app, ["diagnose", "--config", str(config_path), "--pretty"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["overall_status"] == "pass"


def test_diagnose_invalid_config_exits_one(tmp_path: Path) -> None:
    missing = tmp_path / "nope.toml"
    result = runner.invoke(app, ["diagnose", "--config", str(missing)])
    assert result.exit_code == 1
    assert "not found" in (result.stderr or result.output).lower()


def test_diagnose_logs_failed_mandatory_checks(tmp_path: Path) -> None:
    from swing_analyzer.models.capability import (
        CapabilityCheckResult,
        CapabilityName,
        CapabilitySeverity,
        CapabilityStatus,
    )

    config_path = tmp_path / "config.toml"
    data_dir = tmp_path / "data"
    config_path.write_text(f'data_dir = "{data_dir}"\n', encoding="utf-8")

    fail_check = CapabilityCheckResult(
        name=CapabilityName.FFMPEG,
        severity=CapabilitySeverity.MANDATORY,
        status=CapabilityStatus.FAIL,
        message="missing",
        remediation="install ffmpeg",
    )
    report = EnvironmentDiagnosticReport(
        overall_status=OverallStatus.FAIL,
        performance_targets_waived=False,
        checks=[fail_check],
        effective_config_summary=EffectiveConfigSummary(
            data_dir=str(data_dir),
            log_dir=str(data_dir / "logs"),
            config_file=str(config_path),
        ),
    )

    with patch("swing_analyzer.cli.run_diagnostics", return_value=report):
        result = runner.invoke(app, ["diagnose", "--config", str(config_path)])
    assert result.exit_code == 1
    assert "fail" in result.stdout


def test_diagnose_internal_error_exits_one(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text('log_level = "INFO"\n', encoding="utf-8")

    with patch("swing_analyzer.cli.run_diagnostics", side_effect=RuntimeError("boom")):
        result = runner.invoke(app, ["diagnose", "--config", str(config_path)])
    assert result.exit_code == 1
    assert "internal error" in (result.stderr or result.output).lower()


def test_cli_main_entrypoint() -> None:
    with patch("swing_analyzer.cli.app") as mock_app:
        from swing_analyzer.cli import main

        main()
        mock_app.assert_called_once()


def test_report_to_json_compact_and_pretty(tmp_path: Path) -> None:
    config = ApplicationConfiguration(data_dir=tmp_path / "data")
    report = run_diagnostics(config)
    compact = report_to_json(report, pretty=False)
    pretty = report_to_json(report, pretty=True)
    assert "\n" not in compact
    assert "\n" in pretty


def test_logging_setup_writes_file(tmp_path: Path) -> None:
    config = ApplicationConfiguration(data_dir=tmp_path / "data")
    configure_logging(config)
    logger = get_logger("test")
    logger.info("hello", operation="test")
    log_file = tmp_path / "data" / "logs" / "swing-analyzer.log"
    assert log_file.exists()


def test_gpu_pynvml_success_path() -> None:
    from swing_analyzer.diagnostics.checks.gpu import _probe_gpu

    fake_pynvml = type(
        "NVML",
        (),
        {
            "nvmlInit": staticmethod(lambda: None),
            "nvmlShutdown": staticmethod(lambda: None),
            "nvmlDeviceGetCount": staticmethod(lambda: 1),
            "nvmlDeviceGetHandleByIndex": staticmethod(lambda i: "handle"),
            "nvmlDeviceGetName": staticmethod(lambda h: b"RTX 4090"),
            "nvmlSystemGetDriverVersion": staticmethod(lambda: b"550.0"),
        },
    )()
    with patch.dict("sys.modules", {"pynvml": fake_pynvml}):
        version, message = _probe_gpu()
    assert version == "550.0"
    assert "RTX 4090" in message
