from __future__ import annotations

import streamlit as st

from swing_analyzer.config.settings import load_settings
from swing_analyzer.diagnostics.runner import run_diagnostics
from swing_analyzer.logging.setup import configure_logging
from swing_analyzer.models.capability import CAPABILITY_LABELS, CapabilityName, CapabilityStatus
from swing_analyzer.models.diagnostic import OverallStatus

STATUS_ICONS = {
    CapabilityStatus.PASS: "✅",
    CapabilityStatus.WARNING: "⚠️",
    CapabilityStatus.FAIL: "❌",
}

OVERALL_LABELS = {
    OverallStatus.PASS: "All mandatory capabilities passed",
    OverallStatus.PASS_WITH_WARNINGS: "Passed with warnings (GPU optional)",
    OverallStatus.FAIL: "One or more mandatory capabilities failed",
}


@st.cache_data(show_spinner=False)
def _cached_diagnostics() -> dict:
    settings = load_settings()
    configure_logging(settings)
    report = run_diagnostics(settings)
    return report.model_dump(mode="json")


def render_health_view() -> None:
    st.set_page_config(page_title="Golf Swing Analyzer — Health", layout="wide")
    st.title("Golf Swing Analyzer")
    st.subheader("Environment Health")

    report = _cached_diagnostics()
    overall = OverallStatus(report["overall_status"])

    if overall == OverallStatus.PASS:
        st.success(OVERALL_LABELS[overall])
    elif overall == OverallStatus.PASS_WITH_WARNINGS:
        st.warning(OVERALL_LABELS[overall])
    else:
        st.error(OVERALL_LABELS[overall])

    if report.get("performance_targets_waived"):
        st.info("Performance targets waived — GPU acceleration not detected.")

    st.markdown("### Capability checks")
    for check in report["checks"]:
        name = check["name"]
        label = CAPABILITY_LABELS.get(CapabilityName(name), name)
        status = CapabilityStatus(check["status"])
        icon = STATUS_ICONS[status]
        st.markdown(f"**{icon} {label}** — {check['message']}")
        if check.get("detected_version"):
            st.caption(f"Detected: {check['detected_version']}")
        if check.get("remediation"):
            st.caption(f"Remediation: {check['remediation']}")

    summary = report["effective_config_summary"]
    with st.expander("Effective configuration"):
        st.json(summary)


if __name__ == "__main__":
    render_health_view()
