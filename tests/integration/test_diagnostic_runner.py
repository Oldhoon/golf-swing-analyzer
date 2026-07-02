from __future__ import annotations

from pathlib import Path

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.runner import exit_code_for_status, run_diagnostics
from swing_analyzer.models.capability import CapabilityName, CapabilityStatus
from swing_analyzer.models.diagnostic import OverallStatus


def test_full_diagnostic_runner(tmp_path: Path) -> None:
    config = ApplicationConfiguration(data_dir=tmp_path / "data")
    report = run_diagnostics(config)

    assert report.overall_status in OverallStatus
    assert len(report.checks) == 5
    assert report.effective_config_summary.data_dir.endswith("data")

    gpu = next(c for c in report.checks if c.name == CapabilityName.GPU)
    assert gpu.status in (CapabilityStatus.PASS, CapabilityStatus.WARNING)
    assert gpu.status != CapabilityStatus.FAIL

    code = exit_code_for_status(report.overall_status)
    if report.overall_status == OverallStatus.FAIL:
        assert code == 1
    else:
        assert code == 0
