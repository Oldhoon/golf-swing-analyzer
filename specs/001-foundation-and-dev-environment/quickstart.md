# Quickstart: Foundation & Local Development Environment

**Feature**: 001-foundation-and-dev-environment  
**Date**: 2026-06-27

Validates that a contributor can reach a verified, offline-capable foundation per [spec.md](./spec.md). Implementation commands assume the plan in [plan.md](./plan.md) has been built.

## Prerequisites

- Fedora 40+ (or compatible Linux)
- Python 3.11+ (3.12 recommended)
- [uv](https://docs.astral.sh/uv/) installed
- System packages: `ffmpeg` (≥6.0), Nvidia driver (optional — warning if absent)
- Git clone of this repository

## 1. Install dependencies

```bash
cd /path/to/golf-swing-analyzer
uv sync
```

**Expected**: Virtual environment created; `uv.lock` honored; OpenCV and MediaPipe importable inside the venv.

## 2. Optional local config

```bash
cp config/default.toml.example ~/.config/golf-swing-analyzer/config.toml
# Edit data_dir only if overriding XDG default
```

**Expected**: File parses; invalid values cause fail-fast on next command.

## 3. Run environment diagnostic (CLI)

```bash
uv run swing-analyzer diagnose --pretty
```

**Expected**:

- JSON matching [contracts/diagnostic-report.schema.json](./contracts/diagnostic-report.schema.json)
- `checks` length = 5
- Mandatory capabilities (`ffmpeg`, `opencv`, `mediapipe`, `storage`) → `pass` on healthy machine
- `gpu` → `pass` or `warning` (not `fail`)
- Exit code `0` when only GPU warns; `1` if any mandatory check fails
- Completes in **<10 seconds**

## 4. Launch minimal health UI

```bash
uv run python -m swing_analyzer
```

Open browser to `http://localhost:8501`.

**Expected**:

- Health/status view shows same five capabilities with pass/fail/warning
- Overall verdict visible; remediation text for failures/warnings
- No outbound network (verify with firewall or offline mode if desired)
- Ready in **<15 seconds** (reference workstation with GPU)

## 5. Show effective configuration

```bash
uv run swing-analyzer config show
```

**Expected**: JSON with `data_dir` under XDG path (e.g. `~/.local/share/golf-swing-analyzer`).

## 6. Quality gates

```bash
./scripts/quality-gates.sh
```

**Expected**:

- Ruff lint + format check pass
- Pytest passes with coverage report
- Diagnostic exits 0 (or 0 with GPU warning only)
- Total wall time **<60 seconds**

## 7. Verify logging

Trigger a diagnostic failure (e.g., temporarily set invalid `data_dir` in config) and re-run diagnose.

**Expected**: Structured log entry in `{data_dir}/logs/` with error context; actionable stderr message.

## Validation matrix (maps to user stories)

| Story | Quickstart steps | Pass criteria |
|-------|------------------|---------------|
| US1 Verified environment | 1, 3, 4 | Diagnostic + app launch; correct pass/fail/warning |
| US2 Config & logging | 2, 5, 7 | Override applies; logs written on error |
| US3 Quality gates | 6 | All gates runnable; correct exit codes |

## Troubleshooting

| Symptom | Remediation |
|---------|-------------|
| FFmpeg fail | `sudo dnf install ffmpeg` |
| MediaPipe fail | `uv sync` — ensure venv active |
| GPU warning | Install Nvidia driver or continue in CPU warning mode |
| Storage fail | Check permissions on `data_dir`; ensure disk space |

## References

- Data model: [data-model.md](./data-model.md)
- CLI contract: [contracts/cli-commands.md](./contracts/cli-commands.md)
- Research decisions: [research.md](./research.md)
