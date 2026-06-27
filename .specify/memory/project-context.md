# Project Context: Local Golf Swing Analyzer MVP

> **Status: DRAFT — NOT FINAL**
>
> This document captures early project direction for agent and human context. All
> content here is subject to change as specs are written and refined via Spec Kit
> (`/speckit-specify`, `/speckit-plan`, etc.). When this file conflicts with a
> ratified feature spec under `specs/`, **the feature spec wins**.

## Objective

Build a local, offline-first application that:

1. Ingests golf swing videos
2. Extracts biomechanical telemetry using pose estimation
3. Uses a local LLM to provide swing analysis based on **deterministic mathematical heuristics** (not raw perception)

The LLM interprets structured numeric telemetry; it does not perform physics or vision inference.

## Environment & Tech Stack

| Area | Choice (draft) |
|------|----------------|
| **OS** | Linux (Fedora) |
| **Hardware** | Nvidia GPU — CUDA leveraged for hardware-accelerated processing where applicable |
| **Language** | Python 3.11+ |
| **Frontend** | Streamlit or Gradio (rapid MVP iteration; final choice TBD) |
| **Computer vision** | OpenCV (frame manipulation), FFmpeg (Constant Frame Rate normalization) |
| **Pose estimation** | MediaPipe Pose (33 3D keypoints) |
| **Persistence** | Local SQLite database |
| **Analysis layer** | Local LLM wrapper ingesting strict JSON telemetry payloads |

## Architectural Boundaries (Strict Limitations)

These constraints are intentional design guardrails. Deviations require explicit justification in a feature spec and plan.

### 1. No LLM Physics

The LLM MUST NOT analyze raw video frames or raw coordinate streams. A deterministic math/physics layer calculates all angles, speeds, and swing phases. The LLM receives only structured numeric data (JSON) and generates natural-language advice.

### 2. No Cloud Dependencies

Data persistence, video processing, and model execution MUST run entirely on the local machine. No external APIs for inference, storage, or analysis in the MVP scope unless a future spec explicitly expands scope.

### 3. Data Flow (Target Pipeline)

```text
Video Upload
  → FFmpeg CFR Normalization
  → OpenCV Frame Extraction
  → MediaPipe Tracking
  → Mathematical Heuristic Extraction (angles, speeds, phases)
  → JSON Payload
  → LLM Generation
  → SQLite Storage
  → UI Display
```

## Development Workflow (Spec-Driven)

Do not build the entire application at once or invent architecture outside approved specs. The original five pipeline modules are refined into **seven MVP specs** grouped under **four epics** — see [Draft Roadmap](#draft-roadmap) below. Epics are documentation groupings only; Spec Kit features live as flat folders under `specs/###-name/`.

Each spec is specified via Spec Kit (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`) before implementation. Planned first spec: **`001-foundation-and-dev-environment`**.

## Draft Roadmap

> **Status: DRAFT — NOT FINAL**
>
> Target: **7 MVP specs** across **4 epics**. Spec names, order, and boundaries may change
> when `/speckit-specify` is run. Epics are roadmap labels — not Spec Kit artifacts.
> A leaner **6-spec** MVP is possible by merging specs 001 and 002.

### Dependency Order

```text
001 → 002 → 003 → 004 → 005 → 006 → 007 → 008
         └──────────────────────────────┘
              (006 can start once 005 telemetry schema is sketched)
```

Spec **008** is optional: use it for a dedicated end-to-end integration milestone, or fold
E2E wiring into **007** for a 7-spec MVP.

### Epic A — Platform & Shell

| Spec | Working name | Objective |
|------|--------------|-----------|
| **001** | `foundation-and-dev-environment` | Python 3.11+ project layout, dependencies, CUDA/GPU + FFmpeg/OpenCV smoke checks, config, logging, test harness. **Delivers:** runnable local dev environment. |
| **002** | `app-shell-and-ui` | Choose Streamlit or Gradio; app layout, navigation, session state, shared loading/error/empty patterns; stub hooks for upload and results. **Delivers:** UI skeleton later specs plug into. |

### Epic B — Media & Vision

| Spec | Working name | Objective |
|------|--------------|-----------|
| **003** | `video-ingestion-pipeline` | Video upload/validation, local file handling, FFmpeg CFR normalization, OpenCV frame extraction. **Delivers:** normalized frame sequences from a swing video. |
| **004** | `pose-estimation-engine` | MediaPipe Pose on extracted frames; 33-keypoint tracking; confidence/visibility metadata; serialized pose output per frame. **Delivers:** pose time series (no biomechanics yet). |

### Epic C — Biomechanics Core

| Spec | Working name | Objective |
|------|--------------|-----------|
| **005** | `telemetry-and-heuristics` | Deterministic math layer: swing phases, joint angles, speeds; strict JSON telemetry schema (LLM contract). **Delivers:** structured numeric payload — boundary between CV and language. |

*If spec 005 grows too large during planning, split into phase detection vs metrics/heuristics as separate specs.*

### Epic D — Analysis & Delivery

| Spec | Working name | Objective |
|------|--------------|-----------|
| **006** | `persistence-layer` | SQLite schema for videos, pose runs, telemetry, and analysis results; CRUD/query API for the UI. **Delivers:** durable local storage (no LLM dependency). |
| **007** | `llm-analysis-wrapper` | Local LLM runtime; prompt design; JSON-only input guardrails; structured text output. **Delivers:** coaching text from telemetry, never from raw video/coords. |
| **008** *(optional)* | `e2e-analysis-flow` | Wire upload → pipeline → storage → LLM → UI; primary user journey; constitution performance and UX gates. **Delivers:** MVP “analyze a swing end-to-end” experience. |

### Post-MVP (Out of Initial Scope)

Track as separate specs after MVP ships — do not fold into specs 001–008:

- Pose overlay / swing playback scrubber
- Swing history and comparison
- Export (PDF/JSON)
- Heuristic tuning / calibration UI
- Batch or folder import

## Relationship to Other Project Artifacts

| Artifact | Role |
|----------|------|
| `.specify/memory/constitution.md` | Non-negotiable quality principles (code quality, testing, UX, performance) |
| `specs/*/spec.md` | Authoritative requirements per feature (supersedes this document) |
| `specs/*/plan.md` | Technical approach and constitution check per feature |
| This file | High-level MVP direction until specs exist |

## Open Questions (To Resolve in Specs)

- Streamlit vs Gradio for MVP UI
- Local LLM runtime and model selection
- Reference hardware profile for performance targets
- SQLite schema and retention policy for swing sessions
- Exact heuristic set for swing phase detection and fault metrics

---

*Last updated: 2026-06-27 — added draft spec/epic roadmap.*
