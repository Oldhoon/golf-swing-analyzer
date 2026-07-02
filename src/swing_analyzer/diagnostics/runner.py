from __future__ import annotations

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.checks.ffmpeg import check_ffmpeg
from swing_analyzer.diagnostics.checks.gpu import check_gpu
from swing_analyzer.diagnostics.checks.mediapipe import check_mediapipe
from swing_analyzer.diagnostics.checks.opencv import check_opencv
from swing_analyzer.diagnostics.checks.storage import check_storage
from swing_analyzer.models.diagnostic import (
    EffectiveConfigSummary,
    EnvironmentDiagnosticReport,
    OverallStatus,
)


def run_diagnostics(config: ApplicationConfiguration) -> EnvironmentDiagnosticReport:
    config.ensure_directories()

    checks = [
        check_gpu(config),
        check_ffmpeg(config),
        check_opencv(config),
        check_mediapipe(config),
        check_storage(config),
    ]

    overall_status = EnvironmentDiagnosticReport.derive_overall_status(checks)
    performance_targets_waived = EnvironmentDiagnosticReport.performance_targets_waived_from_checks(
        checks
    )

    assert config.log_dir is not None
    summary = EffectiveConfigSummary(
        data_dir=str(config.data_dir.resolve()),
        log_dir=str(config.log_dir.resolve()),
        config_file=str(config.config_file.resolve()) if config.config_file else None,
    )

    return EnvironmentDiagnosticReport(
        overall_status=overall_status,
        performance_targets_waived=performance_targets_waived,
        checks=checks,
        effective_config_summary=summary,
    )


def exit_code_for_status(status: OverallStatus) -> int:
    if status in (OverallStatus.PASS, OverallStatus.PASS_WITH_WARNINGS):
        return 0
    return 1
