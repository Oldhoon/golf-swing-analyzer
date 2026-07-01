# CLI Contract: Foundation Commands

**Feature**: 001-foundation-and-dev-environment  
**Date**: 2026-06-27

Console entry point: `swing-analyzer` (installed via `[project.scripts]` in `pyproject.toml`).

## Commands

### `swing-analyzer diagnose`

Runs all capability checks and prints JSON to stdout.

| Aspect | Contract |
|--------|----------|
| **Stdout** | Single JSON document conforming to [diagnostic-report.schema.json](./diagnostic-report.schema.json) |
| **Stderr** | Structured log lines only (no JSON) |
| **Exit 0** | `overall_status` is `pass` or `pass_with_warnings` |
| **Exit 1** | `overall_status` is `fail` or unhandled internal error |
| **Network** | MUST NOT perform outbound network I/O |
| **Duration** | SHOULD complete within 10s on reference workstation (PERF-001) |

**Options** (Typer):

| Flag | Description |
|------|-------------|
| `--config PATH` | Optional TOML config file override |
| `--pretty` | Pretty-print JSON (human dev use; default compact) |

### `swing-analyzer config show`

Prints resolved effective configuration (non-secret fields) as JSON.

| Aspect | Contract |
|--------|----------|
| **Stdout** | JSON: `{ "data_dir", "log_dir", "log_level", "config_file", capability minimum versions }` |
| **Exit 0** | Valid configuration resolved |
| **Exit 1** | Invalid configuration (fail-fast message on stderr) |

### `python -m swing_analyzer`

Launches Streamlit health/status UI on `localhost` (default port 8501).

| Aspect | Contract |
|--------|----------|
| **Behavior** | On load: run diagnostic, render per-capability pass/fail/warning + overall verdict |
| **Network** | Binds localhost only; no external API calls |
| **Startup** | Ready within 15s on reference workstation (PERF-002; waived in GPU-warning mode) |

## Quality gate wrapper

`scripts/quality-gates.sh` invokes sequentially:

1. `ruff check .`
2. `ruff format --check .`
3. `pytest --cov=swing_analyzer --cov-report=term-missing`
4. `swing-analyzer diagnose`

Any step non-zero → script exits non-zero.

## Capability name glossary (UX-003)

| Canonical name | User-facing label |
|----------------|---------------------|
| `gpu` | Hardware acceleration (GPU) |
| `ffmpeg` | Video tooling (FFmpeg) |
| `opencv` | Frame processing (OpenCV) |
| `mediapipe` | Pose runtime (MediaPipe) |
| `storage` | Local storage |
