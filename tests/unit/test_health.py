from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch


def _fake_streamlit() -> MagicMock:
    fake_st = MagicMock()
    fake_st.cache_data = lambda **kwargs: lambda fn: fn
    return fake_st


def _report_payload(overall_status: str, **kwargs: object) -> dict:
    return {
        "overall_status": overall_status,
        "performance_targets_waived": kwargs.get("performance_targets_waived", False),
        "checks": kwargs.get(
            "checks",
            [
                {
                    "name": "ffmpeg",
                    "status": "pass",
                    "message": "ok",
                    "detected_version": "6.1.0",
                    "remediation": None,
                }
            ],
        ),
        "effective_config_summary": {
            "data_dir": "/tmp/data",
            "log_dir": "/tmp/data/logs",
            "config_file": None,
        },
    }


def test_render_health_view_pass_status() -> None:
    fake_st = _fake_streamlit()
    with (
        patch.dict(sys.modules, {"streamlit": fake_st}),
        patch(
            "swing_analyzer.app.health._cached_diagnostics",
            return_value=_report_payload("pass"),
        ),
    ):
        from swing_analyzer.app.health import render_health_view

        render_health_view()

    fake_st.success.assert_called_once()


def test_render_health_view_fail_status() -> None:
    fake_st = _fake_streamlit()
    with (
        patch.dict(sys.modules, {"streamlit": fake_st}),
        patch(
            "swing_analyzer.app.health._cached_diagnostics",
            return_value=_report_payload(
                "fail",
                checks=[
                    {
                        "name": "ffmpeg",
                        "status": "fail",
                        "message": "missing",
                        "remediation": "install ffmpeg",
                    }
                ],
            ),
        ),
    ):
        from swing_analyzer.app.health import render_health_view

        render_health_view()

    fake_st.error.assert_called_once()
    fake_st.caption.assert_called()


def test_render_health_view_with_warnings() -> None:
    fake_st = _fake_streamlit()
    report_payload = _report_payload(
        "pass_with_warnings",
        performance_targets_waived=True,
        checks=[
            {
                "name": "gpu",
                "status": "warning",
                "message": "no gpu",
                "remediation": "install driver",
            }
        ],
    )

    with (
        patch.dict(sys.modules, {"streamlit": fake_st}),
        patch(
            "swing_analyzer.app.health._cached_diagnostics",
            return_value=report_payload,
        ),
    ):
        from swing_analyzer.app.health import render_health_view

        render_health_view()

    fake_st.warning.assert_called_once()
    fake_st.info.assert_called_once()
    fake_st.expander.assert_called_once()


def test_cached_diagnostics_runs_runner(tmp_path) -> None:
    fake_st = _fake_streamlit()
    config = {"data_dir": str(tmp_path / "data")}

    with (
        patch.dict(sys.modules, {"streamlit": fake_st}),
        patch("swing_analyzer.app.health.load_settings") as load_settings,
        patch("swing_analyzer.app.health.configure_logging") as configure_logging,
        patch("swing_analyzer.app.health.run_diagnostics") as run_diagnostics,
    ):
        from swing_analyzer.app.health import _cached_diagnostics
        from swing_analyzer.models.diagnostic import (
            EffectiveConfigSummary,
            EnvironmentDiagnosticReport,
            OverallStatus,
        )

        load_settings.return_value = MagicMock()
        run_diagnostics.return_value = EnvironmentDiagnosticReport(
            overall_status=OverallStatus.PASS,
            performance_targets_waived=False,
            checks=[],
            effective_config_summary=EffectiveConfigSummary(
                data_dir=config["data_dir"],
                log_dir=f"{config['data_dir']}/logs",
                config_file=None,
            ),
        )

        result = _cached_diagnostics()

    load_settings.assert_called_once()
    configure_logging.assert_called_once()
    run_diagnostics.assert_called_once()
    assert result["overall_status"] == "pass"
