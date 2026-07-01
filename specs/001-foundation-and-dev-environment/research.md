# Research: Foundation & Local Development Environment

**Feature**: 001-foundation-and-dev-environment  
**Date**: 2026-06-27

## 1. Dependency management & packaging

**Decision**: `uv` + `pyproject.toml` + `uv.lock` (PEP 621 project metadata, hatchling build backend)

**Rationale**: Reproducible pinned installs (FR-001), fast resolver, single lockfile for CI and contributors. Standard `src/` layout via hatchling.

**Alternatives considered**:
- *Poetry*: Mature but slower; viable fallback documented in quickstart.
- *pip + requirements.txt*: No first-class lock semantics; weaker reproducibility.

## 2. Minimal launchable entrypoint (health UI)

**Decision**: **Streamlit** for `python -m swing_analyzer` health/status view

**Rationale**: Aligns with `project-context.md` (Streamlit listed first); rapid status dashboard with pass/fail/warning components; local-only server binds localhost. Full navigation/session shell deferred to spec 002.

**Alternatives considered**:
- *Gradio*: Better for ML demos; less natural for static health dashboard.
- *CLI-only*: Fails spec clarification (minimal launchable entrypoint with health view).

## 3. Diagnostic CLI (quality gate)

**Decision**: **Typer** subcommand `swing-analyzer diagnose` (also exposed as `python -m swing_analyzer.cli diagnose`)

**Rationale**: Machine-readable JSON output + exit codes for merge gates (FR-010); separable from Streamlit for headless CI.

**Alternatives considered**:
- *Click*: Equivalent; Typer gives typed params and auto-help with less boilerplate.

## 4. Configuration

**Decision**: **pydantic-settings** loading `config.toml` (optional) + env overrides; defaults via **platformdirs** (`user_data_dir("golf-swing-analyzer")`)

**Rationale**: Typed validation (FR-007 fail-fast), XDG-compliant default path per clarification, overridable `data_dir` key.

**Alternatives considered**:
- *Raw TOML + os.environ*: No validation story.
- *Project-relative `.data/`*: Rejected in clarification — keeps large swing data out of repo.

## 5. Structured logging

**Decision**: **structlog** with JSON renderer to stderr + rotating file under XDG data `logs/`

**Rationale**: Constitution observability; machine-parseable context (operation, error, inputs summary) without cloud sinks.

**Alternatives considered**:
- *stdlib logging only*: Possible but more boilerplate for structured fields.

## 6. Capability checks (mandatory vs recommended)

| Capability | Check method | Severity |
|------------|--------------|----------|
| GPU / CUDA | `pynvml` + `nvidia-smi` fallback; driver + device presence | **Warning** (optional) |
| FFmpeg | `subprocess` `ffmpeg -version`; parse semver vs pinned minimum | **Fail** |
| OpenCV | `import cv2`; `cv2.__version__` vs minimum | **Fail** |
| MediaPipe Pose | `import mediapipe`; version vs minimum; import smoke only (no frame processing) | **Fail** |
| Local storage | Resolve configured data dir; create-if-missing; write+delete probe file | **Fail** |

**Rationale**: Matches spec clarifications Q2–Q3; pose runtime validated at foundation without tracking logic.

**Alternatives considered**:
- *Defer MediaPipe to spec 004*: Rejected per clarification — early fail saves pipeline rework.

## 7. Lint, format, test

**Decision**: **ruff** (lint + format), **pytest** + **pytest-cov** (≥80% target on new code per constitution)

**Rationale**: Single fast tool for code quality gate; pytest is standard for Python module/integration tests.

**Alternatives considered**:
- *black + flake8*: Two tools vs ruff unified.

## 8. GPU warning vs fail (exit codes)

**Decision**: Diagnostic JSON includes `overall_status`: `pass` | `pass_with_warnings` | `fail`. CLI exits **0** for `pass` and `pass_with_warnings`; **1** for `fail` or internal error.

**Rationale**: Spec clarification Q5 — GPU absence must not block merge gates.

## 9. Reference workstation profile

**Decision**: Fedora 40+, Python 3.12, Nvidia GPU with driver ≥535, 16 GB RAM, FFmpeg 6.x system package, CUDA toolkit optional for warning-mode dev without GPU

**Rationale**: Matches `project-context.md` OS/hardware; gives measurable PERF targets a concrete baseline.

**Alternatives considered**:
- *Exact GPU model lock-in*: Too brittle; driver + device presence sufficient.

## 10. Version pinning policy

**Decision**: Minimum versions in `pyproject.toml`; exact pins in `uv.lock`. Diagnostic compares detected versions against `pyproject.toml` `[tool.swing_analyzer.capabilities]` table.

**Rationale**: FR-004 version compatibility at runtime, not just import success.
