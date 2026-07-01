# Implementation Plan: Foundation & Local Development Environment

**Branch**: `001-foundation-and-dev-environment` | **Date**: 2026-06-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-foundation-and-dev-environment/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Establish the offline-first Python project foundation for the Golf Swing Analyzer: reproducible dependency management, modular `src/` layout for future pipeline modules, environment diagnostics (GPU warning / mandatory capability hard-fails), centralized configuration with XDG-default data paths, structured logging, quality gates (ruff, pytest, diagnostic CLI), and a minimal Streamlit health/status entrypoint. No swing processing, pose tracking, or persistence logic in this slice.

## Technical Context

**Language/Version**: Python 3.11+ (target 3.12 on Fedora)

**Primary Dependencies**: `uv` (dependency lock/install), Streamlit (minimal health UI), pydantic-settings + platformdirs (config/XDG paths), structlog (structured logging), OpenCV + MediaPipe + FFmpeg (system binary, validated not used for processing yet), pynvml (GPU probe), Typer (CLI diagnostic gate), ruff (lint/format), pytest + pytest-cov (test harness)

**Storage**: Local filesystem only — XDG user data directory (`~/.local/share/golf-swing-analyzer/` by default); no SQLite in this spec (deferred to spec 006)

**Testing**: pytest with unit tests (config, diagnostic logic, report serialization) and integration tests (diagnostic runner against mocked/subprocess checks, Streamlit app smoke, CLI exit codes)

**Target Platform**: Linux (Fedora), Nvidia GPU workstation (CUDA available; warning-only if absent)

**Project Type**: Single Python desktop/web-local app (Streamlit local server + CLI)

**Performance Goals**: Diagnostic completes <10s; app ready <15s (waived in GPU-warning mode); quality gates <60s on reference workstation

**Constraints**: Offline at runtime; pinned dependencies; no outbound network after setup; GPU optional (warning); video tooling + pose runtime + storage mandatory

**Scale/Scope**: Single developer/contributor machine; one diagnostic report per run; foundation only (~15–20 source modules)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify each item; document any exception in Complexity Tracking below.

| Principle | Gate | Status |
|-----------|------|--------|
| **I. Code Quality** | Module boundaries clear; lint/format rules identified; no unjustified complexity | ☑ |
| **II. Testing Standards** | Test strategy defined per user story (unit + integration); red-green-refactor plan stated | ☑ |
| **III. UX Consistency** | Shared UI patterns identified; accessibility (WCAG 2.1 AA) considered; terminology consistent | ☑ |
| **IV. Performance** | Performance goals and constraints filled in Technical Context; measurement approach defined | ☑ |

### Gate notes (post-design)

- **I**: Packages `config`, `diagnostics`, `logging`, `models`, `app` with typed public APIs; ruff enforces style.
- **II**: US1 → integration tests for diagnostic + app launch; US2 → unit tests for config/logging; US3 → CLI contract tests for exit codes; red-green-refactor in tasks.
- **III**: Health view uses consistent pass/fail/warning badges and remediation copy; full WCAG shell deferred to spec 002 — minimal health page uses semantic headings and status text (partial AA for this slice).
- **IV**: PERF targets from spec; quickstart includes timed validation steps.

## Project Structure

### Documentation (this feature)

```text
specs/001-foundation-and-dev-environment/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks — not yet created)
```

### Source Code (repository root)

```text
pyproject.toml
uv.lock
README.md
config/
└── default.toml.example

src/
└── swing_analyzer/
    ├── __init__.py
    ├── __main__.py              # `python -m swing_analyzer` → Streamlit health app
    ├── cli.py                   # Typer CLI: diagnose, config show
    ├── app/
    │   └── health.py            # Streamlit health/status view
    ├── config/
    │   └── settings.py          # pydantic-settings, XDG paths
    ├── diagnostics/
    │   ├── runner.py
    │   ├── report.py
    │   └── checks/
    │       ├── gpu.py
    │       ├── ffmpeg.py
    │       ├── opencv.py
    │       ├── mediapipe.py
    │       └── storage.py
    ├── logging/
    │   └── setup.py
    └── models/
        ├── capability.py
        └── diagnostic.py

tests/
├── unit/
│   ├── test_settings.py
│   ├── test_diagnostic_report.py
│   └── test_checks.py
├── integration/
│   ├── test_diagnostic_runner.py
│   └── test_cli_exit_codes.py
└── contract/
    └── test_diagnostic_schema.py

scripts/
└── quality-gates.sh             # lint + test + diagnose wrapper
```

**Structure Decision**: Single-project layout under `src/swing_analyzer/` per Spec Kit default. Future modules (ingestion, pose, telemetry, llm, persistence) add subpackages alongside `diagnostics/` without restructuring. CLI and Streamlit share diagnostic core logic.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | — | — |
