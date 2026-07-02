from __future__ import annotations

import json
from typing import Any

from swing_analyzer.models.diagnostic import EnvironmentDiagnosticReport


def report_to_dict(report: EnvironmentDiagnosticReport) -> dict[str, Any]:
    payload = report.model_dump(mode="json")
    payload["generated_at"] = report.generated_at.isoformat().replace("+00:00", "Z")
    return payload


def report_to_json(report: EnvironmentDiagnosticReport, *, pretty: bool = False) -> str:
    payload = report_to_dict(report)
    if pretty:
        return json.dumps(payload, indent=2)
    return json.dumps(payload, separators=(",", ":"))
