<!--
Sync Impact Report
==================
Version change: (unratified template) → 1.0.0
Modified principles: N/A (initial ratification)
Added sections:
  - Core Principles (4): Code Quality, Testing Standards, UX Consistency, Performance
  - Additional Constraints
  - Development Workflow & Quality Gates
  - Governance
Removed sections: None (template placeholders replaced)
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated
  - .specify/templates/tasks-template.md ✅ updated
  - .specify/templates/checklist-template.md ✅ (no changes required)
  - .specify/templates/commands/*.md ⚠ N/A (directory does not exist)
  - README.md ⚠ N/A (file does not exist)
Follow-up TODOs: None
-->

# Golf Swing Analyzer Constitution

## Core Principles

### I. Code Quality

All production code MUST be readable, maintainable, and consistent with project conventions.

- Every module MUST have a single, clear responsibility; shared logic MUST be extracted rather than duplicated.
- Public APIs, data models, and service boundaries MUST be explicitly typed and documented at the point of use.
- Linting and formatting rules MUST pass with zero warnings before merge; suppressions require documented justification.
- Complexity beyond straightforward solutions MUST be recorded in the plan's Complexity Tracking table with rejected alternatives.
- Dead code, commented-out blocks, and unexplained magic numbers MUST NOT be committed.

**Rationale**: Golf swing analysis depends on precise, evolvable algorithms and UI flows. High code quality reduces regression risk as pose detection, metrics, and feedback logic grow.

### II. Testing Standards (NON-NEGOTIABLE)

Automated tests are a delivery requirement, not an optional follow-up.

- Every user story MUST ship with tests that prove its independent acceptance scenarios before the story is marked complete.
- Unit tests MUST cover business logic, metric calculations, and edge cases; integration tests MUST cover end-to-end user journeys and API contracts.
- Tests MUST follow red-green-refactor: written (or updated) first, observed failing for the right reason, then implementation makes them pass.
- Test names MUST describe behavior (given/when/then intent), not implementation details.
- Flaky tests MUST be fixed or quarantined immediately; they MUST NOT be ignored or retried without root-cause analysis.
- Coverage targets: ≥80% line coverage on new/changed production code; critical paths (swing analysis pipeline, scoring, persistence) MUST have explicit regression tests.

**Rationale**: Incorrect swing metrics or broken flows erode user trust. A enforced testing bar catches regressions in video processing, analysis, and presentation layers early.

### III. User Experience Consistency

The product MUST feel cohesive, predictable, and accessible across every screen and interaction.

- A shared design language (typography, spacing, color, motion, iconography) MUST be applied consistently; one-off styling requires design justification.
- Common patterns (loading, empty, error, success, confirmation) MUST use shared components and copy tone; users MUST NOT encounter conflicting messages for the same state.
- All interactive elements MUST meet WCAG 2.1 AA: keyboard navigable, visible focus, sufficient contrast, and meaningful labels for assistive technology.
- Feedback MUST be timely: perceived response to user actions within 100ms for UI acknowledgment; long operations MUST show progress or skeleton states.
- Terminology for golf concepts (swing phases, faults, drills) MUST remain consistent across UI, reports, and API responses.
- Breaking UX changes to primary flows MUST include a migration or in-app guidance note in the feature spec.

**Rationale**: Golfers use this tool to improve technique. Inconsistent UX creates confusion; consistent patterns build confidence and reduce support burden.

### IV. Performance Requirements

The system MUST remain responsive under real-world video and analysis workloads.

- Video upload and swing analysis MUST complete within targets defined in each feature spec (default: analysis results within 30s for a 10s clip on reference hardware).
- Interactive UI MUST maintain 60fps on target devices during playback, scrubbing, and overlay rendering; jank MUST be investigated when frame drops exceed 5% of a session.
- API p95 latency MUST stay under 500ms for read operations and under 2s for write/analysis triggers unless spec documents a justified exception.
- Memory growth during video sessions MUST be bounded; repeated analyze/export cycles MUST NOT leak resources across sessions.
- Performance regressions beyond agreed thresholds MUST block merge until measured, fixed, or explicitly waived in Complexity Tracking with owner sign-off.
- Performance-sensitive changes MUST include before/after measurements (or profiling notes) in the PR or plan.

**Rationale**: Swing analysis is inherently compute-heavy. Explicit performance standards keep the product usable on consumer hardware and prevent gradual degradation as features accumulate.

## Additional Constraints

- **Stack discipline**: Prefer established libraries for video, pose estimation, and UI; new dependencies MUST be justified in plan.md research.
- **Data handling**: User swing videos and derived metrics are sensitive; data retention, export, and deletion behavior MUST be specified per feature.
- **Offline / degraded mode**: When analysis cannot run (network, GPU, or model unavailable), the UI MUST surface a clear, actionable error—not a silent failure.
- **Observability**: Production paths MUST emit structured logs and error context sufficient to diagnose failed analyses without reproducing on a developer machine.

## Development Workflow & Quality Gates

1. **Spec gate**: User stories, acceptance scenarios, success criteria, and non-functional requirements (UX, performance) defined before planning.
2. **Plan gate**: Constitution Check in plan.md MUST pass before Phase 0 research; re-check after Phase 1 design.
3. **Implementation gate**: Lint clean, tests passing, no unresolved TODO in changed production paths.
4. **Review gate**: PR description MUST map changes to user stories and cite test evidence; reviewers verify principles I–IV explicitly.
5. **Release gate**: Quickstart validation and primary user journey smoke test MUST pass for the affected feature slice.

## Governance

This constitution supersedes ad-hoc practices for the Golf Swing Analyzer project. All feature work (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`) MUST align with these principles.

- **Amendments**: Proposed via PR updating this file; include version bump rationale and Sync Impact Report. Material principle changes require explicit acknowledgment in the amending PR.
- **Versioning**: Semantic versioning—MAJOR for incompatible principle removals or redefinitions; MINOR for new principles or materially expanded guidance; PATCH for clarifications and non-semantic edits.
- **Compliance review**: Every plan.md Constitution Check and every PR review MUST confirm adherence to principles I–IV; violations MUST be documented in Complexity Tracking or fixed before merge.
- **Runtime guidance**: Feature-specific technical context lives in `specs/*/plan.md` and agent context files; this constitution defines non-negotiable quality bars.

**Version**: 1.0.0 | **Ratified**: 2026-06-27 | **Last Amended**: 2026-06-27
