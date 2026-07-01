# Data Model: Foundation & Local Development Environment

**Feature**: 001-foundation-and-dev-environment  
**Date**: 2026-06-27

This feature has no persistent database. Models are in-memory / serialized JSON for diagnostics and configuration resolution.

## Entity: CapabilityCheckResult

Represents the outcome of a single environment capability probe.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string (enum) | yes | One of: `gpu`, `ffmpeg`, `opencv`, `mediapipe`, `storage` |
| `severity` | string (enum) | yes | `mandatory` or `recommended` |
| `status` | string (enum) | yes | `pass`, `fail`, or `warning` |
| `detected_version` | string \| null | no | Reported version string from probe (e.g. `6.1.1`, `4.10.0`) |
| `minimum_version` | string \| null | no | Required minimum when version check applies |
| `message` | string | yes | Human-readable summary |
| `remediation` | string \| null | no | Actionable fix when `fail` or `warning` |

### Validation rules

- `status=fail` ⇒ `severity=mandatory` and `remediation` MUST be non-empty.
- `status=warning` ⇒ `severity=recommended` (GPU only in this spec).
- `status=pass` ⇒ `remediation` SHOULD be null.

## Entity: EnvironmentDiagnosticReport

Aggregate result returned by the diagnostic runner and displayed in CLI/Streamlit.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `generated_at` | ISO 8601 datetime | yes | UTC timestamp |
| `overall_status` | string (enum) | yes | `pass`, `pass_with_warnings`, or `fail` |
| `performance_targets_waived` | boolean | yes | `true` when GPU check is `warning` |
| `checks` | array of CapabilityCheckResult | yes | Fixed length 5 (one per capability) |
| `effective_config_summary` | object | yes | Non-secret config snapshot (see below) |

### overall_status derivation

1. Any mandatory check with `status=fail` → `fail`
2. Else any recommended check with `status=warning` → `pass_with_warnings`
3. Else → `pass`

### effective_config_summary (embedded)

| Field | Type | Description |
|-------|------|-------------|
| `data_dir` | string (path) | Resolved absolute data directory |
| `log_dir` | string (path) | Resolved log directory |
| `config_file` | string \| null | Path to loaded config file if any |

## Entity: ApplicationConfiguration

Resolved settings used at startup (pydantic-settings model).

| Field | Type | Default | Validation |
|-------|------|---------|------------|
| `data_dir` | Path | XDG `user_data_dir("golf-swing-analyzer")` | Must be creatable/writable |
| `log_dir` | Path | `{data_dir}/logs` | Created on first run |
| `config_file` | Path \| null | null | If set, must exist and parse as TOML |
| `log_level` | string | `INFO` | Enum: DEBUG, INFO, WARNING, ERROR |
| `ffmpeg_minimum_version` | string | `6.0.0` | Semver string |
| `opencv_minimum_version` | string | `4.8.0` | Semver string |
| `mediapipe_minimum_version` | string | `0.10.0` | Semver string |

### State transitions

```text
[no config file] → load defaults → resolve paths → create dirs → ready
[config file present] → parse → validate → merge env overrides → ready
[invalid value] → fail fast (FR-007) → exit before diagnostic/app
```

## Relationships

```text
ApplicationConfiguration
        │
        ▼ (used by)
DiagnosticRunner ──produces──► EnvironmentDiagnosticReport
        │
        └──contains──► CapabilityCheckResult (×5)
```

## Out of scope (later specs)

- Swing session, video asset, pose frame, telemetry JSON, analysis result entities → specs 003–007
- SQLite tables → spec 006
