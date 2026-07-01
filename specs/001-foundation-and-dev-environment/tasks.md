---

description: "Task list for foundation & local development environment"
---

# Tasks: Foundation & Local Development Environment

**Input**: Design documents from `specs/001-foundation-and-dev-environment/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Per constitution Principle II and FR-011, every user story includes test tasks. Write tests first (red-green-refactor).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- All tasks include exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency lockfile, and tooling configuration

- [ ] T001 Create `src/swing_analyzer/` package skeleton per plan.md (`__init__.py`, `app/`, `config/`, `diagnostics/checks/`, `logging/`, `models/`)
- [ ] T002 Initialize `pyproject.toml` with hatchling build, Python 3.11+, runtime deps (streamlit, pydantic-settings, platformdirs, structlog, opencv-python, mediapipe, pynvml, typer), dev deps (ruff, pytest, pytest-cov, jsonschema), and `[project.scripts]` entry `swing-analyzer = swing_analyzer.cli:app`
- [ ] T003 [P] Configure ruff lint and format rules in `pyproject.toml`
- [ ] T004 [P] Configure pytest and coverage (`--cov=swing_analyzer`, ≥80% target) in `pyproject.toml`
- [ ] T005 Generate pinned `uv.lock` via `uv lock` and verify `uv sync` installs cleanly
- [ ] T006 [P] Create `config/default.toml.example` documenting `data_dir`, `log_level`, and capability minimum versions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared models, configuration, and logging that all user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 [P] Implement `CapabilityCheckResult` enums and model in `src/swing_analyzer/models/capability.py`
- [ ] T008 [P] Implement `EnvironmentDiagnosticReport` model and `overall_status` derivation in `src/swing_analyzer/models/diagnostic.py`
- [ ] T009 Implement `ApplicationConfiguration` with XDG defaults and version minimums in `src/swing_analyzer/config/settings.py`
- [ ] T010 Implement structlog JSON setup (stderr + file under `log_dir`) in `src/swing_analyzer/logging/setup.py`
- [ ] T011 [P] Write failing unit tests for `overall_status` derivation in `tests/unit/test_diagnostic_report.py`
- [ ] T012 [P] Write failing unit tests for settings defaults, XDG `data_dir`, and fail-fast validation in `tests/unit/test_settings.py`
- [ ] T013 Implement report serialization helpers in `src/swing_analyzer/diagnostics/report.py`
- [ ] T014 Make foundational unit tests in `tests/unit/test_diagnostic_report.py` and `tests/unit/test_settings.py` pass

**Checkpoint**: Models, config, and logging ready — user story implementation can begin

---

## Phase 3: User Story 1 - Verified Local Environment (Priority: P1) 🎯 MVP

**Goal**: Contributor can run diagnostics and launch minimal health UI confirming mandatory capabilities (GPU warns only)

**Independent Test**: On fresh checkout, `uv run swing-analyzer diagnose` reports pass/fail/warning per capability; `uv run python -m swing_analyzer` shows health view with no outbound network

### Tests for User Story 1 (REQUIRED — write FIRST, ensure FAIL before implementation)

- [ ] T015 [P] [US1] Write contract test validating diagnostic JSON against `specs/001-foundation-and-dev-environment/contracts/diagnostic-report.schema.json` in `tests/contract/test_diagnostic_schema.py`
- [ ] T016 [P] [US1] Write unit tests for each capability check (mocked subprocess/import) in `tests/unit/test_checks.py`
- [ ] T017 [P] [US1] Write integration test for full diagnostic runner in `tests/integration/test_diagnostic_runner.py`

### Implementation for User Story 1

- [ ] T018 [P] [US1] Implement GPU check (warning-only) in `src/swing_analyzer/diagnostics/checks/gpu.py`
- [ ] T019 [P] [US1] Implement FFmpeg version check (mandatory) in `src/swing_analyzer/diagnostics/checks/ffmpeg.py`
- [ ] T020 [P] [US1] Implement OpenCV version check (mandatory) in `src/swing_analyzer/diagnostics/checks/opencv.py`
- [ ] T021 [P] [US1] Implement MediaPipe import/version check (mandatory) in `src/swing_analyzer/diagnostics/checks/mediapipe.py`
- [ ] T022 [P] [US1] Implement storage writable probe and directory creation in `src/swing_analyzer/diagnostics/checks/storage.py`
- [ ] T023 [US1] Implement diagnostic runner orchestrating all five checks in `src/swing_analyzer/diagnostics/runner.py`
- [ ] T024 [US1] Implement `diagnose` Typer command with JSON stdout and exit codes per `contracts/cli-commands.md` in `src/swing_analyzer/cli.py`
- [ ] T025 [US1] Implement Streamlit health/status view with pass/fail/warning badges in `src/swing_analyzer/app/health.py`
- [ ] T026 [US1] Wire `python -m swing_analyzer` Streamlit entrypoint in `src/swing_analyzer/__main__.py`
- [ ] T027 [US1] Verify all US1 tests pass and manual quickstart steps 1, 3, 4 succeed per `quickstart.md`

**Checkpoint**: User Story 1 fully functional — diagnostic CLI + health UI independently testable

---

## Phase 4: User Story 2 - Diagnosable Configuration and Logging (Priority: P2)

**Goal**: Contributor can override config, see effective settings, and get structured logs on failures

**Independent Test**: Change `data_dir` in config, restart; invalid config fails fast; failed diagnostic writes structured log to `{data_dir}/logs/`

### Tests for User Story 2 (REQUIRED — write FIRST)

- [ ] T028 [P] [US2] Extend `tests/unit/test_settings.py` with config override and invalid-value fail-fast cases
- [ ] T029 [P] [US2] Write integration test for `config show` CLI output in `tests/integration/test_config_cli.py`

### Implementation for User Story 2

- [ ] T030 [US2] Implement `config show` subcommand emitting effective config JSON in `src/swing_analyzer/cli.py`
- [ ] T031 [US2] Integrate structlog context (operation, error, inputs summary) on check failures in `src/swing_analyzer/diagnostics/runner.py`
- [ ] T032 [US2] Display effective config summary in Streamlit health view in `src/swing_analyzer/app/health.py`
- [ ] T033 [US2] Implement first-run `data_dir`/`log_dir` creation and permission validation in `src/swing_analyzer/config/settings.py`
- [ ] T034 [US2] Verify US2 tests pass and quickstart steps 2, 5, 7 succeed per `quickstart.md`

**Checkpoint**: User Stories 1 and 2 both work independently

---

## Phase 5: User Story 3 - Quality Gates Runnable on Demand (Priority: P3)

**Goal**: Contributor runs lint, format, tests, and diagnostic via single documented command with correct exit codes

**Independent Test**: `./scripts/quality-gates.sh` passes on healthy env; exits non-zero on lint failure or mandatory capability fail; exits zero when only GPU warns

### Tests for User Story 3 (REQUIRED — write FIRST)

- [ ] T035 [P] [US3] Write integration tests for diagnose exit codes (pass, pass_with_warnings, fail) in `tests/integration/test_cli_exit_codes.py`
- [ ] T036 [P] [US3] Write smoke test invoking `scripts/quality-gates.sh` in `tests/integration/test_quality_gates.py`

### Implementation for User Story 3

- [ ] T037 [US3] Create `scripts/quality-gates.sh` chaining `ruff check`, `ruff format --check`, `pytest --cov`, and `swing-analyzer diagnose`
- [ ] T038 [US3] Ensure coverage reporting and fail-under threshold configured in `pyproject.toml`
- [ ] T039 [US3] Verify US3 tests pass and `scripts/quality-gates.sh` completes within 60s per PERF-003

**Checkpoint**: All three user stories independently functional with enforceable quality gates

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, repo hygiene, and end-to-end validation

- [ ] T040 [P] Write `README.md` with setup (`uv sync`), diagnostic, app launch, and link to `specs/001-foundation-and-dev-environment/quickstart.md`
- [ ] T041 [P] Add `.gitignore` entries for `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, and local data paths
- [ ] T042 Run full `quickstart.md` validation checklist and fix any gaps
- [ ] T043 Verify constitution gates: ruff clean, tests ≥80% coverage on `swing_analyzer`, no unresolved TODOs in production paths

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **blocks all user stories**
- **US1 (Phase 3)**: Depends on Foundational — **MVP target**
- **US2 (Phase 4)**: Depends on Foundational; integrates with US1 CLI/app but independently testable
- **US3 (Phase 5)**: Depends on US1 diagnostic CLI and Foundational test config
- **Polish (Phase 6)**: Depends on desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no dependency on US2/US3
- **US2 (P2)**: Can start after Foundational — extends US1 CLI/app but testable via `config show` and logging alone
- **US3 (P3)**: Requires US1 `diagnose` command and pytest config from Setup/Foundational

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/checks before runner
- Runner before CLI/UI
- Story tests green before next priority

### Parallel Opportunities

- **Phase 1**: T003, T004, T006 in parallel after T002
- **Phase 2**: T007, T008, T011, T012 in parallel
- **US1**: T015–T017 (tests) in parallel; T018–T022 (checks) in parallel after tests written
- **US2**: T028, T029 in parallel
- **US3**: T035, T036 in parallel
- **Polish**: T040, T041 in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (write first, expect failures):
tests/contract/test_diagnostic_schema.py
tests/unit/test_checks.py
tests/integration/test_diagnostic_runner.py

# Launch all capability checks together (after tests exist):
src/swing_analyzer/diagnostics/checks/gpu.py
src/swing_analyzer/diagnostics/checks/ffmpeg.py
src/swing_analyzer/diagnostics/checks/opencv.py
src/swing_analyzer/diagnostics/checks/mediapipe.py
src/swing_analyzer/diagnostics/checks/storage.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run `quickstart.md` steps 1, 3, 4
5. Demo diagnostic + health UI before proceeding

### Incremental Delivery

1. Setup + Foundational → shared infrastructure ready
2. Add US1 → diagnostic + health UI (MVP!)
3. Add US2 → config show + structured logging
4. Add US3 → quality-gates.sh for merge blocking
5. Polish → README, quickstart validation, .gitignore

### Suggested Feature Branch

Per constitution branch gate: implement on `001-foundation-and-dev-environment`, merge to `main` after quality gates pass.

---

## Notes

- GPU check MUST never return `fail` — only `pass` or `warning` (spec clarification)
- MediaPipe check is import/version only — no frame processing (pose logic is spec 004)
- Streamlit binds `localhost` only; no outbound network at runtime
- Terminology for capability labels must match `contracts/cli-commands.md` glossary (UX-003)
- Stop at any checkpoint to validate story independently before continuing
