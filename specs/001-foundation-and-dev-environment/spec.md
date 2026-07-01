# Feature Specification: Foundation & Local Development Environment

**Feature Branch**: `001-foundation-and-dev-environment`

**Created**: 2026-06-27

**Status**: Draft

**Input**: User description: "Draft the foundational spec for this project based on project-context.md — establish the runnable, offline-first local foundation that all later modules (video ingestion, pose estimation, telemetry/heuristics, LLM analysis, persistence) build upon."

## Clarifications

### Session 2026-06-27

- Q: How much runnable app surface should spec 001 deliver versus deferring to spec 002 (app-shell-and-ui)? → A: Foundation delivers a minimal launchable entrypoint that runs the diagnostic and shows a health/status view; the full interactive UI shell (navigation, session state, upload/results stubs) is deferred to 002.
- Q: Is GPU/hardware acceleration required or optional for the foundation? → A: GPU acceleration is recommended but optional — its absence produces a prominent warning (not a hard fail), the app still starts, and performance targets are explicitly waived in that mode. Video tooling, pose runtime, and local storage remain mandatory (hard fail).
- Q: Should the foundation validate the pose-estimation runtime? → A: Foundation validates pose runtime presence and version in the diagnostic (mandatory hard fail if missing/incompatible). Actual pose tracking logic remains in spec 004.
- Q: What is the default local data storage location? → A: User-scoped directory following XDG conventions (e.g., under the user's local share path) as the default, overridable via configuration; large data stays out of the repository.
- Q: Should quality gates treat a GPU warning as pass or fail? → A: Pass with warning — only mandatory capability failures cause a non-zero exit status from the diagnostic quality gate.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verified local environment from a clean machine (Priority: P1)

A contributor clones the project onto a local Linux workstation and, following the documented setup, reaches a state where the application launches and a single diagnostic step confirms every mandatory capability is present and working: video processing tooling, pose-estimation runtime, and local storage. GPU/hardware acceleration is checked and reported; if absent, the system warns but still starts. They never need cloud access or external services.

**Why this priority**: Nothing else in the roadmap can be built or trusted until the foundation runs locally and its core capabilities are verifiably available. This is the MVP of the foundation itself.

**Independent Test**: On a fresh checkout, run the documented setup and the environment diagnostic; verify it reports a clear pass/fail/warning per capability and the app starts without errors or network calls.

**Acceptance Scenarios**:

1. **Given** a clean checkout on a supported workstation, **When** the contributor follows the setup instructions, **Then** all declared dependencies install successfully with reproducible, pinned versions.
2. **Given** a completed setup, **When** the contributor runs the environment diagnostic, **Then** the system reports the status of each capability (hardware acceleration, video tooling, pose runtime, local storage) as pass, fail, or warning with an actionable message for any failure or warning.
3. **Given** missing GPU/hardware acceleration, **When** the diagnostic runs, **Then** the system reports a prominent warning (not a hard fail), the overall environment is still considered usable, and performance targets are explicitly waived for that mode.
4. **Given** a missing or misconfigured mandatory capability (video tooling, pose runtime, or local storage), **When** the diagnostic runs, **Then** the system reports a hard fail, clearly identifies the capability, and provides remediation guidance without crashing.
5. **Given** a verified environment, **When** the contributor launches the minimal application entrypoint, **Then** it starts locally, runs the diagnostic, presents a health/status view, and makes no outbound network requests.

---

### User Story 2 - Diagnosable configuration and logging (Priority: P2)

A contributor needs to change local settings (such as file locations or runtime options) and understand what the system is doing when something goes wrong, using local configuration and structured logs only.

**Why this priority**: Later modules are compute-heavy and failure-prone (video decode, GPU inference). Centralized configuration and structured logging make every subsequent module diagnosable from the start, satisfying the constitution's observability constraint.

**Independent Test**: Change a documented configuration value, restart the app, and confirm the new value takes effect; trigger an error path and confirm a structured log entry with enough context to diagnose it appears locally.

**Acceptance Scenarios**:

1. **Given** documented configuration options, **When** a contributor sets a local override, **Then** the application applies it on next start and reports the effective configuration.
2. **Given** an invalid configuration value, **When** the application starts, **Then** it fails fast with a clear message naming the offending setting.
3. **Given** an operation that fails, **When** the failure occurs, **Then** a structured log entry is written locally with sufficient context (operation, inputs summary, error) to diagnose it without reproducing on another machine.

---

### User Story 3 - Quality gates runnable on demand (Priority: P3)

A contributor runs the project's automated quality gates — linting/formatting, the test harness, and the environment diagnostic — with simple, documented commands before submitting changes.

**Why this priority**: The constitution makes code quality and testing non-negotiable. A working harness from day one ensures every later module inherits enforceable gates rather than retrofitting them.

**Independent Test**: Run the documented quality-gate commands on a clean checkout and confirm lint/format, the (initially minimal) test suite, and the diagnostic all execute and report clear pass/fail results.

**Acceptance Scenarios**:

1. **Given** a clean checkout, **When** the contributor runs the lint/format gate, **Then** it executes and reports violations (or a clean result) with zero ambiguous output.
2. **Given** the test harness, **When** the contributor runs it, **Then** at least one foundational test executes and the runner reports pass/fail and coverage scope.
3. **Given** the quality gates, **When** a mandatory capability fails, **Then** the command exits with a non-zero status suitable for blocking a merge; **When** only a GPU warning is present, **Then** the diagnostic gate exits zero (pass with warning).

---

### Edge Cases

- When hardware acceleration is absent or the driver is incompatible, the foundation MUST degrade gracefully: report a prominent warning, allow startup, and waive performance targets for that mode (no crash, no hard fail).
- How does the system behave when video tooling or the pose runtime is installed but the wrong version? The diagnostic must detect version mismatches, not just presence, and treat mismatches as hard fails for mandatory capabilities.
- What happens on first run when local storage or required directories do not yet exist — the system MUST create them safely under the configured default (user-scoped XDG-style path) or report a clear error if it cannot.
- What happens when configuration files are missing entirely — are sensible local defaults used?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST provide a documented, reproducible local setup process that installs all required dependencies with pinned versions and no cloud or external-service dependency.
- **FR-002**: The system MUST establish a clear, documented project structure that accommodates the planned modules (UI, video ingestion, pose estimation, telemetry/heuristics, LLM analysis, persistence) without prescribing their internal implementation.
- **FR-003**: The system MUST provide an environment diagnostic that checks each capability — hardware/GPU acceleration (recommended), video processing tooling (mandatory), pose-estimation runtime (mandatory), and local storage (mandatory) — and reports per-capability status as pass, fail, or warning with actionable remediation guidance.
- **FR-004**: The environment diagnostic MUST detect not only presence but version compatibility of checked capabilities, MUST NOT crash when a capability is missing or misconfigured, MUST validate pose-estimation runtime presence and version as a mandatory check (pose tracking logic itself is deferred to spec 004), and MUST treat missing or incompatible mandatory capabilities as hard fails while treating absent GPU acceleration as a warning only.
- **FR-005**: The foundation MUST provide a minimal launchable application entrypoint that starts locally, runs the environment diagnostic, presents a health/status view, and operates without making outbound network requests during startup and diagnostics. The full interactive UI shell (navigation, session state, upload/results stubs) is out of scope here and is deferred to spec 002.
- **FR-006**: The system MUST provide centralized, local configuration with sensible defaults, support local overrides, and report the effective configuration at startup. The default local data storage path MUST follow user-scoped XDG conventions and MUST be overridable via configuration.
- **FR-007**: The system MUST fail fast with a clear, specific message when configuration is invalid.
- **FR-008**: The system MUST emit structured logs locally with enough context to diagnose failures without reproducing them on another machine.
- **FR-009**: The system MUST provide runnable quality gates — code formatting/linting, an automated test harness, and the environment diagnostic — invokable via documented commands.
- **FR-010**: Quality-gate commands MUST return non-zero exit status when a mandatory capability fails or when lint/format/tests fail; the environment diagnostic MUST exit zero when only recommended-capability warnings are present (pass with warning).
- **FR-011**: The foundation MUST include at least one passing automated test and a coverage-reporting capability so later modules inherit the testing harness.
- **FR-012**: First-run setup MUST safely create required local directories and storage locations under the configured default path (user-scoped XDG-style location unless overridden), or report a clear error if it cannot.
- **FR-013**: Setup and diagnostic documentation MUST be discoverable in the repository so a new contributor can reach a verified environment unaided.

### Key Entities *(include if feature involves data)*

- **Environment Diagnostic Report**: The outcome of the capability checks — a per-capability status (pass/fail/warning), detected version, remediation hint for failures, and an explicit note when performance targets are waived due to missing GPU acceleration.
- **Application Configuration**: The effective set of local settings (storage locations defaulting to a user-scoped XDG-style path, runtime options) resolved from defaults plus local overrides.
- **Mandatory Capability**: A prerequisite that blocks a usable environment when missing or incompatible (video tooling, pose runtime, local storage).
- **Recommended Capability**: A prerequisite that improves performance but does not block startup when absent (hardware/GPU acceleration); reported as a warning.

## Non-Functional Requirements *(mandatory)*

### User Experience

- **UX-001**: The environment diagnostic MUST present results in a consistent, scannable format with an unambiguous pass/fail/warning per capability and a single overall verdict that distinguishes mandatory failures from recommended warnings.
- **UX-002**: Every failure (setup, configuration, diagnostic) MUST produce an actionable message that names the problem and the next step; silent failures are not acceptable.
- **UX-003**: Terminology used in diagnostics, configuration keys, and logs MUST be consistent with the project glossary established in `project-context.md`.

### Performance

- **PERF-001**: The environment diagnostic MUST complete within 10 seconds on the reference workstation so it is cheap to run repeatedly.
- **PERF-002**: Application startup (excluding one-time dependency installation) MUST reach a ready state within 15 seconds on the reference workstation; this target is waived when GPU acceleration is absent (warning mode).
- **PERF-003**: Running the quality gates on the foundation MUST complete within 60 seconds on the reference workstation to keep the inner development loop fast.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new contributor can go from a clean checkout to a verified, running environment in under 15 minutes of active effort (excluding unattended download/install time).
- **SC-002**: The environment diagnostic reports a correct pass/fail/warning for 100% of checked capabilities, including at least one intentionally broken mandatory capability and one absent GPU scenario in testing.
- **SC-003**: The application starts and runs the diagnostic with zero outbound network requests.
- **SC-004**: All quality gates are runnable with documented single commands and return correct exit statuses: zero for pass (including pass-with-warning when only GPU is absent), non-zero for mandatory capability failures and lint/test failures.
- **SC-005**: At least one automated test runs and passes, and coverage is reported, establishing the testing baseline for later modules.

## Assumptions

- The target environment is a local Linux (Fedora) workstation with an Nvidia GPU, consistent with `project-context.md`; "reference workstation" in performance criteria refers to this class of machine. GPU absence is a supported warning mode, not the primary target.
- Default local data lives in a user-scoped XDG-style directory (not inside the repository) unless overridden; this keeps swing videos and derived data out of version control.
- The concrete technology choices (Python version, UI framework, pose runtime, video tooling) are governed by `project-context.md` and will be finalized during `/speckit-plan`; this spec intentionally states capabilities rather than fixing tools.
- This foundation does not yet process golf swing videos or produce analysis; it establishes the verified, runnable base and quality harness only. Video, pose, telemetry, LLM, and persistence behavior are deferred to specs 002–008.
- "No cloud dependencies" applies to runtime; one-time dependency downloads during setup are permitted.
- Offline-first means all processing and storage happen locally; the foundation must not require connectivity to operate once set up.

## Dependencies

- Governed by the project constitution (`.specify/memory/constitution.md`) for code quality, testing, UX consistency, and performance principles.
- Aligns with the draft roadmap in `.specify/memory/project-context.md`; this is spec **001**, a prerequisite for all subsequent specs.
