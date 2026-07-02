from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from swing_analyzer.config.settings import ApplicationConfiguration
from swing_analyzer.diagnostics.report import report_to_dict
from swing_analyzer.diagnostics.runner import run_diagnostics
from swing_analyzer.models.capability import CapabilityName

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "specs/001-foundation-and-dev-environment/contracts/diagnostic-report.schema.json"
)


@pytest.fixture
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_diagnostic_report_matches_schema(schema: dict, tmp_path: Path) -> None:
    config = ApplicationConfiguration(data_dir=tmp_path / "data")
    report = run_diagnostics(config)
    payload = report_to_dict(report)
    jsonschema.validate(instance=payload, schema=schema)


def test_report_has_five_checks(tmp_path: Path) -> None:
    config = ApplicationConfiguration(data_dir=tmp_path / "data")
    report = run_diagnostics(config)
    assert len(report.checks) == 5
    names = {check.name for check in report.checks}
    assert names == {
        CapabilityName.GPU,
        CapabilityName.FFMPEG,
        CapabilityName.OPENCV,
        CapabilityName.MEDIAPIPE,
        CapabilityName.STORAGE,
    }
