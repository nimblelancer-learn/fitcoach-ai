# AI Fitness Coaching Assistant — Master Plan

> Portfolio project for preparing and applying to the Everfit AI Engineer role.
>
> Goal: Build a production-minded LLM application that demonstrates FastAPI, direct LLM SDK usage, RAG, structured output, evals, observability, guardrails, user feedback, and continuous improvement.

---

## 0. Why This Project Exists

This project is designed as a practical portfolio project to help transition from a Software Engineering / Automation Testing background into Product-oriented LLM Engineering.

The target job requires more than knowing AI theory or building simple demos. It expects evidence of:

- Shipping at least one LLM feature to real users.
- Building LLM workflows, RAG pipelines, embeddings, and structured outputs.
- Calling OpenAI and/or Anthropic SDKs directly, not only through framework wrappers.
- Understanding agentic systems and their safety boundaries.
- Having an eval-first mindset.
- Tracking LLM cost, latency, failure modes, hallucination risks, and user feedback.
- Working with product, QA, BA, and engineering teams to define what “done” means for non-deterministic AI features.

This project should become a living portfolio: MVP first, then user feedback, evals, observability, metrics, and iteration.

---

## 1. Project Summary

## Project Name

**FitCoach AI — RAG-powered Fitness Coaching Assistant**

Alternative title:

**AI Coaching Copilot for Personalized Fitness Planning**

## One-line Description

An AI-powered fitness coaching assistant that creates personalized workout plans using structured LLM output, RAG-based grounding, safety guardrails, evals, observability, and real user feedback.

## Problem Statement

Fitness beginners often struggle to create workout plans that match their goals, available time, equipment, current level, and physical limitations. Generic plans are often too vague, too intense, unsafe, or not personalized enough.

This project explores how an LLM-based assistant can generate structured, personalized, safer, and explainable workout plans while remaining grounded in a curated fitness knowledge base and continuously improved through evaluation and user feedback.

## Target Users

Initial target users:

- Fitness beginners.
- Busy people who want a simple 3–4 day/week plan.
- People training at home or in a gym.
- People with general fitness goals: fat loss, muscle gain, endurance, general health.

Not the initial target:

- Medical rehabilitation users.
- Users needing professional medical diagnosis.
- Advanced athletes requiring highly specialized programming.
- Nutrition/medical cases requiring licensed professional advice.

---

## 2. Core Positioning for Job Application

This project should communicate the following story:

> My background is Software Engineering with experience in .NET development and automation testing. While studying a master’s program focused on AI, I decided to move toward product-oriented LLM engineering. To prepare seriously, I built an AI Fitness Coaching Assistant that focuses not only on calling LLM APIs, but on production-minded concerns: structured output, RAG, schema validation, retries, safety guardrails, evals, observability, cost/latency tracking, user feedback, and continuous improvement.

The strongest personal angle:

- Software Engineering background → can build product, APIs, systems.
- Automation Testing background → natural fit for eval-first LLM development.
- Master’s AI background → understands ML/NLP foundations.
- Agentic coding tool experience → understands modern AI-assisted development workflows.
- This project → concrete proof of practical LLM engineering capability.

---

## 3. Product Scope

## MVP Scope

The first version should focus deeply on one complete flow:

```text
User Profile Intake
→ RAG Retrieval
→ Workout Plan Generation
→ Structured JSON Validation
→ Safety Validation
→ User-facing Plan Rendering
→ Feedback Collection
→ Eval / Improvement Loop
```

## MVP Features

### 1. User Profile Intake

Collect structured user information:

- Goal: fat loss, muscle gain, general fitness, endurance.
- Level: beginner, intermediate.
- Available days per week.
- Session duration.
- Equipment: gym, dumbbells, bodyweight, resistance bands.
- Injury or physical limitation.
- Exercise preference.
- Training location.

### 2. Workout Plan Generation

Generate a structured workout plan:

- Weekly schedule.
- Workout days.
- Exercises.
- Sets, reps, rest time.
- Warm-up.
- Cool-down.
- Intensity notes.
- Safety notes.
- Progression suggestion.

The generated plan must first be valid structured JSON, then rendered to the user.

### 3. RAG Knowledge Grounding

Use a curated fitness knowledge base for:

- Beginner training principles.
- Exercise form.
- Progressive overload.
- Recovery.
- Safety considerations.
- General wellness guidance.

### 4. Safety Guardrails

Implement guardrails for health-adjacent outputs:

- Do not diagnose medical conditions.
- Do not provide unsafe recommendations for injuries.
- Ask for clarification when required user data is missing.
- Use fallback/refusal when medical risk is detected.
- Avoid overly intense plans for beginners.

### 5. User Feedback Collection

Collect feedback after a plan is generated:

- Was the plan useful?
- Was it too easy / too hard?
- Was anything confusing?
- Did it feel safe?
- Would the user follow it?
- Free-text feedback.

### 6. Eval Baseline

Create an evaluation system to measure quality:

- Schema validity.
- Personalization.
- Safety.
- Clarity.
- Groundedness.
- Difficulty fit.
- Completeness.

---

## 4. Out of Scope for Early Versions

Do not build these in the first MVP:

- Full mobile app.
- Full nutrition planning.
- Wearable integration.
- Medical diagnosis.
- Rehabilitation planning.
- Complex multi-agent system.
- Social network features.
- Payment system.
- Complex user management.

Reason: the goal is not to build a full fitness startup product. The goal is to demonstrate LLM engineering capability in a focused, production-minded way.

---

## 5. Proposed Tech Stack

## Backend

- Python
- FastAPI
- Pydantic
- Docker

Purpose:

- Build AI backend API.
- Validate input/output schemas.
- Expose endpoints for generation, retrieval, feedback, evals, and health checks.

## LLM Providers

Primary:

- OpenAI SDK directly.

Secondary / optional:

- Anthropic SDK directly.

Important principle:

- Do not rely only on LangChain or other wrappers.
- Direct SDK experience should be visible in code.

## Vector Database

- Qdrant

Purpose:

- Store embeddings.
- Retrieve fitness knowledge chunks.
- Use metadata filtering by topic, equipment, difficulty, safety, body part.

## Observability

- Langfuse

Purpose:

- Trace LLM calls.
- Track prompt versions.
- Track latency.
- Track token usage.
- Track estimated cost.
- Track validation failures.
- Track user feedback.

## App Database

Initial:

- SQLite for local MVP.

Better for deployed version:

- PostgreSQL.
- Supabase is acceptable if it speeds up setup.

## Frontend

Recommended:

- Next.js.

Alternative for faster MVP:

- Streamlit.

Recommendation:

- Use Next.js if the goal is a more product-like portfolio.
- Use Streamlit only if speed is more important than product polish.

## Deployment

Possible options:

- Frontend: Vercel.
- Backend: Render, Railway, Fly.io, or Google Cloud Run.
- Vector DB: Qdrant Cloud or Docker-hosted Qdrant.
- Observability: Langfuse Cloud or self-hosted.

---

## 6. High-level Architecture

```text
Frontend
  ↓
FastAPI Backend
  ↓
Profile Validator
  ↓
RAG Retriever → Qdrant Vector DB → Fitness Knowledge Base
  ↓
Prompt Builder
  ↓
LLM Provider SDK
  ↓
Structured Output Validator
  ↓
Safety Validator
  ↓
Workout Plan Renderer
  ↓
User Feedback Collector
  ↓
Eval Dataset / Improvement Loop
  ↓
Langfuse Observability
```

Key design principle:

> The system should not be a simple prompt-to-text demo. It should be a controlled LLM workflow with validation, retrieval, observability, evals, and fallback behavior.

---

## 7. Suggested Repository Structure

```text
fitcoach-ai/
├── README.md
├── MASTER_PLAN.md
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes_health.py
│   │   │   ├── routes_profile.py
│   │   │   ├── routes_generate.py
│   │   │   ├── routes_feedback.py
│   │   │   └── routes_eval.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── errors.py
│   │   ├── schemas/
│   │   │   ├── profile.py
│   │   │   ├── workout_plan.py
│   │   │   ├── feedback.py
│   │   │   └── eval.py
│   │   ├── llm/
│   │   │   ├── openai_client.py
│   │   │   ├── anthropic_client.py
│   │   │   ├── prompts.py
│   │   │   └── structured_output.py
│   │   ├── rag/
│   │   │   ├── embeddings.py
│   │   │   ├── qdrant_client.py
│   │   │   ├── retriever.py
│   │   │   └── indexing.py
│   │   ├── safety/
│   │   │   ├── policy.py
│   │   │   ├── validators.py
│   │   │   └── fallback.py
│   │   ├── evals/
│   │   │   ├── runner.py
│   │   │   ├── rubrics.py
│   │   │   └── graders.py
│   │   └── observability/
│   │       ├── langfuse_client.py
│   │       └── metrics.py
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   └── ...
├── knowledge_base/
│   ├── raw/
│   ├── processed/
│   └── sources.md
├── evals/
│   ├── datasets/
│   │   └── workout_plan_eval_v1.jsonl
│   ├── reports/
│   └── README.md
├── docs/
│   ├── architecture.md
│   ├── safety-policy.md
│   ├── rag-design.md
│   ├── eval-design.md
│   ├── user-feedback.md
│   └── interview-notes.md
└── project-management/
    ├── github-projects-setup.md
    ├── milestones.md
    └── backlog.md
```

---

## 8. Milestones

Milestones are not date-based. They are readiness-based.

## Milestone 1 — Local AI Feature Works

Goal:

- A local FastAPI app can generate a structured workout plan from a user profile.

Must have:

- FastAPI backend.
- User profile schema.
- Workout plan schema.
- Direct OpenAI SDK call.
- Structured JSON output.
- Schema validation.
- Basic retry on invalid output.
- Basic logs for latency and token usage.

Definition of Done:

- Run backend locally.
- Send sample profile.
- Receive valid structured workout plan.
- Invalid output is handled with retry or fallback.

---

## Milestone 2 — RAG MVP

Goal:

- Workout plan generation uses retrieved knowledge from a curated fitness knowledge base.

Must have:

- Knowledge base v1.
- Chunking script.
- Embedding script.
- Qdrant collection.
- Retrieval function.
- Retrieved context injected into prompt.
- Debug logs showing retrieved chunks.

Definition of Done:

- A generation request retrieves relevant context.
- Retrieved chunks are visible in debug/logs.
- There is a re-indexing script.
- At least 30–50 initial chunks exist.

---

## Milestone 3 — Safety and Eval Baseline

Goal:

- The system has basic health-adjacent safety boundaries and measurable evals.

Must have:

- Safety policy v1.
- Injury/medical keyword handling.
- Fallback/refusal behavior.
- Eval dataset v1.
- Eval runner.
- Metrics for schema validity, safety, personalization, clarity, and completeness.

Definition of Done:

- Unsafe inputs trigger fallback.
- Eval runner can be executed from command line.
- Baseline report is generated.
- At least 30 eval cases exist.

---

## Milestone 4 — Deployed MVP and First Real Users

Goal:

- The app is deployed and used by real users.

Must have:

- Public app or demo link.
- Feedback collection form.
- Feedback stored in database or file.
- At least 5 real users.
- At least 10 feedback entries.
- Changelog based on feedback.

Definition of Done:

- Users can access the app without local setup.
- Feedback is collected.
- At least 3 changes are made based on feedback.

---

## Milestone 5 — Observability and Metrics

Goal:

- The project has traceability, cost/latency visibility, and failure analysis.

Must have:

- Langfuse integration.
- Request tracing.
- Prompt version tracking.
- Token usage tracking.
- Cost estimate per request.
- Latency tracking.
- Validation error tracking.
- Retry count tracking.
- Safety trigger tracking.

Definition of Done:

- Each generation request has a trace.
- There is a report showing latency, cost, and failure modes.
- At least one optimization has a quantified result.

Example metric goals:

- Schema-valid output rate improved from X% to Y%.
- Average latency reduced from X seconds to Y seconds.
- Average token usage reduced by X%.
- Safety failure cases reduced by X%.

---

## Milestone 6 — Interview-ready Portfolio Package

Goal:

- The project can be presented confidently in a job application and interview.

Must have:

- Polished README.
- Architecture diagram.
- Demo video.
- Eval report.
- User feedback summary.
- Metrics summary.
- Known limitations.
- Future roadmap.
- CV bullet points.
- Interview talking points.

Definition of Done:

- A recruiter/interviewer can understand the project from README alone.
- You can explain all key design decisions.
- You can discuss failures and improvements clearly.

---

## 9. GitHub Projects Setup

Recommended GitHub Project view fields:

## Fields

- Status
  - Backlog
  - Ready
  - In Progress
  - In Review
  - Blocked
  - Done

- Priority
  - P0 — Critical
  - P1 — Important
  - P2 — Nice to have

- Epic
  - Foundation
  - LLM SDK
  - RAG
  - Safety
  - Evals
  - Observability
  - Feedback
  - Deployment
  - Documentation
  - Interview Prep

- Milestone
  - M1 Local AI Feature
  - M2 RAG MVP
  - M3 Safety + Eval
  - M4 Deployed MVP
  - M5 Observability
  - M6 Interview-ready

- Type
  - Feature
  - Bug
  - Research
  - Documentation
  - Experiment
  - Refactor
  - Test

- Confidence
  - High
  - Medium
  - Low

- Evidence
  - Link to PR, screenshot, trace, eval report, demo, or user feedback.

## Recommended Views

1. **Roadmap by Milestone**
   - Group by Milestone.

2. **Kanban by Status**
   - Group by Status.

3. **Backlog by Epic**
   - Group by Epic.

4. **Interview Evidence View**
   - Filter Done items with Evidence not empty.

5. **Current Focus**
   - Filter Status = In Progress or Ready.

---

## 10. Initial Backlog — Issue-based Backlog

This backlog is organized by **GitHub Issues**, not by tiny tasks.

Each issue should represent a meaningful outcome. Smaller tasks should be written as checklists inside the issue description.

Recommended GitHub Project fields:

* **Status**: Backlog / Ready / In Progress / In Review / Blocked / Done
* **Priority**: P0 / P1 / P2
* **Epic**: Foundation / LLM SDK / RAG / Safety / Evals / Observability / Feedback / Deployment / Documentation / Interview Prep
* **Milestone**: M1 / M2 / M3 / M4 / M5 / M6
* **Type**: Feature / Bug / Research / Documentation / Experiment / Refactor / Test
* **Evidence**: PR link, screenshot, trace, eval report, demo, user feedback, or documentation link

---

# Milestone 1 — Local AI Feature Works

Goal:

A local FastAPI backend can generate a valid structured workout plan from a user profile using direct LLM SDK calls.

---

## Issue 1 — [Foundation] Initialize repository and project structure

**Priority:** P0
**Epic:** Foundation
**Milestone:** M1 — Local AI Feature Works
**Type:** Feature / Documentation

### Scope

* [ ] Create GitHub repository.
* [ ] Add `MASTER_PLAN.md`.
* [ ] Add `README.md` v0.
* [ ] Add `.gitignore`.
* [ ] Add `.env.example`.
* [ ] Create initial backend folder structure.
* [ ] Create initial docs folder structure.

### Done when

* [ ] Repository is created.
* [ ] Master plan exists in the repo.
* [ ] Basic project structure is visible.
* [ ] README contains project name, goal, and local setup placeholder.

### Evidence

* Repository link.
* Initial commit or PR link.

---

## Issue 2 — [Foundation] Setup FastAPI backend skeleton

**Priority:** P0
**Epic:** Foundation
**Milestone:** M1 — Local AI Feature Works
**Type:** Feature

### Scope

* [ ] Setup Python project with `uv` or `poetry`.
* [ ] Setup FastAPI app.
* [ ] Add `/health` endpoint.
* [ ] Add basic app configuration.
* [ ] Add basic logging.
* [ ] Add global error handling.
* [ ] Add API request examples.

### Done when

* [ ] Backend runs locally.
* [ ] `/health` returns a successful response.
* [ ] FastAPI docs are available.
* [ ] Local run command is documented.

### Evidence

* PR link.
* Screenshot or terminal log showing `/health` works.

---

## Issue 3 — [Foundation] Add local development environment

**Priority:** P1
**Epic:** Foundation
**Milestone:** M1 — Local AI Feature Works
**Type:** Feature / DevEx

### Scope

* [ ] Add Dockerfile.
* [ ] Add `docker-compose.yml`.
* [ ] Add Makefile or task runner.
* [ ] Add local run instructions.
* [ ] Add pre-commit hooks, optional.
* [ ] Add basic unit test command.

### Done when

* [ ] Project can be started locally with documented commands.
* [ ] Docker setup works, or limitation is documented.
* [ ] Developer setup is clear from README.

### Evidence

* PR link.
* Screenshot or terminal log showing local app startup.

---

## Issue 4 — [Foundation] Define core domain schemas

**Priority:** P0
**Epic:** Foundation
**Milestone:** M1 — Local AI Feature Works
**Type:** Feature

### Scope

* [ ] Define `UserProfile` schema.
* [ ] Define `WorkoutPlan` schema.
* [ ] Define `ExerciseItem` schema.
* [ ] Define `SafetyWarning` schema.
* [ ] Define basic request and response models.
* [ ] Add basic schema validation tests.

### Done when

* [ ] User profile input can be validated.
* [ ] Workout plan output has a stable schema.
* [ ] Invalid input returns a meaningful validation error.
* [ ] Schema tests pass.

### Evidence

* PR link.
* Test result screenshot or log.

---

## Issue 5 — [LLM SDK] Implement direct OpenAI structured generation

**Priority:** P0
**Epic:** LLM SDK
**Milestone:** M1 — Local AI Feature Works
**Type:** Feature

### Scope

* [ ] Create OpenAI client wrapper.
* [ ] Load API key from environment variables.
* [ ] Create first prompt for workout plan generation.
* [ ] Implement structured JSON output.
* [ ] Validate LLM output with Pydantic.
* [ ] Return structured workout plan from API endpoint.

### Done when

* [ ] A sample user profile can generate a workout plan.
* [ ] Output is valid structured JSON.
* [ ] Output matches `WorkoutPlan` schema.
* [ ] OpenAI SDK is called directly, not only through a framework wrapper.

### Evidence

* PR link.
* Example API response.
* Screenshot or terminal log showing successful generation.

---

## Issue 6 — [LLM SDK] Add LLM reliability handling

**Priority:** P0
**Epic:** LLM SDK
**Milestone:** M1 — Local AI Feature Works
**Type:** Feature

### Scope

* [ ] Add retry on malformed output.
* [ ] Add fallback response if retries fail.
* [ ] Add timeout handling.
* [ ] Add basic LLM error handling.
* [ ] Add logs for failed generations.
* [ ] Add test or mock case for malformed output.

### Done when

* [ ] Malformed output does not crash the app.
* [ ] System retries within a defined limit.
* [ ] System returns fallback after retry failure.
* [ ] Failure behavior is documented.

### Evidence

* PR link.
* Test result or log showing retry/fallback behavior.

---

## Issue 7 — [LLM SDK] Add basic LLM usage metrics

**Priority:** P0
**Epic:** LLM SDK
**Milestone:** M1 — Local AI Feature Works
**Type:** Feature

### Scope

* [ ] Track latency per request.
* [ ] Track token usage per request.
* [ ] Estimate cost per request.
* [ ] Log model name.
* [ ] Log retry count.
* [ ] Add simple metrics output to logs.

### Done when

* [ ] Each generation request logs latency.
* [ ] Each generation request logs token usage if available.
* [ ] Estimated cost is calculated or clearly marked as unavailable.
* [ ] Metrics are visible in local logs.

### Evidence

* PR link.
* Log screenshot showing latency/token/cost.

---

## Issue 8 — [Foundation] Add basic tests for local AI feature

**Priority:** P1
**Epic:** Foundation
**Milestone:** M1 — Local AI Feature Works
**Type:** Test

### Scope

* [ ] Add unit tests for schemas.
* [ ] Add test for valid profile input.
* [ ] Add test for invalid profile input.
* [ ] Add test for malformed LLM output handling.
* [ ] Add test run command to README.

### Done when

* [ ] Tests can be run locally.
* [ ] Core schema tests pass.
* [ ] Basic reliability behavior is covered.

### Evidence

* PR link.
* Test result screenshot or CI log.

---

# Milestone 2 — RAG MVP

Goal:

Workout plan generation uses retrieved context from a curated fitness knowledge base.

---

## Issue 9 — [RAG] Setup fitness knowledge base v1

**Priority:** P0
**Epic:** RAG
**Milestone:** M2 — RAG MVP
**Type:** Research / Documentation

### Scope

* [ ] Create `knowledge_base/` folder.
* [ ] Define knowledge source policy.
* [ ] Collect initial fitness knowledge documents.
* [ ] Convert sources into markdown or JSON.
* [ ] Add `sources.md`.
* [ ] Organize documents by topic.

### Done when

* [ ] Knowledge base v1 exists.
* [ ] Sources are documented.
* [ ] Documents are usable for chunking.
* [ ] At least initial beginner fitness topics are covered.

### Evidence

* PR link.
* Knowledge base folder.
* `sources.md`.

---

## Issue 10 — [RAG] Implement document processing and chunking

**Priority:** P0
**Epic:** RAG
**Milestone:** M2 — RAG MVP
**Type:** Feature

### Scope

* [ ] Define document format.
* [ ] Implement chunking script.
* [ ] Add chunk metadata.
* [ ] Save processed chunks.
* [ ] Add sample processed output.
* [ ] Document chunking strategy.

### Done when

* [ ] Raw documents can be converted into chunks.
* [ ] Chunks include useful metadata.
* [ ] Processed chunks are stored in a predictable location.
* [ ] Chunking strategy is documented.

### Evidence

* PR link.
* Sample processed chunks.
* Chunking script.

---

## Issue 11 — [RAG] Setup Qdrant and embedding pipeline

**Priority:** P0
**Epic:** RAG
**Milestone:** M2 — RAG MVP
**Type:** Feature

### Scope

* [ ] Setup Qdrant locally.
* [ ] Create Qdrant collection.
* [ ] Implement embedding script.
* [ ] Store embeddings and metadata.
* [ ] Add re-index command.
* [ ] Document local Qdrant setup.

### Done when

* [ ] Qdrant runs locally.
* [ ] Chunks can be embedded.
* [ ] Embeddings and metadata are stored in Qdrant.
* [ ] Re-indexing can be triggered with a documented command.

### Evidence

* PR link.
* Screenshot/log of Qdrant collection.
* Re-index command output.

---

## Issue 12 — [RAG] Implement retrieval and prompt grounding

**Priority:** P0
**Epic:** RAG
**Milestone:** M2 — RAG MVP
**Type:** Feature

### Scope

* [ ] Implement retriever.
* [ ] Retrieve top-k relevant chunks.
* [ ] Inject retrieved context into workout generation prompt.
* [ ] Log retrieved chunks.
* [ ] Add debug output for retrieved context.
* [ ] Update generation endpoint to use retrieved context.

### Done when

* [ ] Workout plan generation uses retrieved context.
* [ ] Retrieved chunks are visible in logs/debug output.
* [ ] Prompt includes grounded context.
* [ ] System still returns valid structured output.

### Evidence

* PR link.
* Example request showing retrieved chunks.
* Example generated plan using retrieved context.

---

## Issue 13 — [RAG] Add basic retrieval quality checks

**Priority:** P1
**Epic:** RAG
**Milestone:** M2 — RAG MVP
**Type:** Test / Experiment

### Scope

* [ ] Add retrieval test queries.
* [ ] Check whether retrieved chunks are relevant.
* [ ] Add metadata filtering, optional.
* [ ] Document early retrieval failure cases.
* [ ] Identify possible improvements.

### Done when

* [ ] Basic retrieval test cases exist.
* [ ] Retrieval behavior can be inspected manually.
* [ ] At least a few failure cases are documented.
* [ ] Next-step improvements are identified.

### Evidence

* PR link.
* Retrieval test results.
* Notes on failure cases.

---

## Issue 14 — [Docs] Write RAG design doc v0

**Priority:** P1
**Epic:** Documentation
**Milestone:** M2 — RAG MVP
**Type:** Documentation

### Scope

* [ ] Explain knowledge base structure.
* [ ] Explain chunking strategy.
* [ ] Explain embedding pipeline.
* [ ] Explain retrieval flow.
* [ ] Document known limitations.
* [ ] Add future RAG improvement ideas.

### Done when

* [ ] `docs/rag-design.md` exists.
* [ ] Design choices are explained.
* [ ] Limitations are clearly documented.

### Evidence

* PR link.
* `docs/rag-design.md`.

---

# Milestone 3 — Safety and Eval Baseline

Goal:

The system has basic health-adjacent safety boundaries and measurable evaluation.

---

## Issue 15 — [Safety] Define safety policy and medical boundaries

**Priority:** P0
**Epic:** Safety
**Milestone:** M3 — Safety + Eval Baseline
**Type:** Documentation / Research

### Scope

* [ ] Write safety policy v1.
* [ ] Define out-of-scope medical cases.
* [ ] Define refusal/fallback scenarios.
* [ ] Define general fitness vs medical advice boundary.
* [ ] Add examples of safe and unsafe responses.

### Done when

* [ ] Safety policy exists.
* [ ] Medical boundaries are clear.
* [ ] Refusal/fallback cases are documented.
* [ ] The assistant’s scope is explicit.

### Evidence

* PR link.
* `docs/safety-policy.md`.

---

## Issue 16 — [Safety] Implement basic safety guardrails

**Priority:** P0
**Epic:** Safety
**Milestone:** M3 — Safety + Eval Baseline
**Type:** Feature

### Scope

* [ ] Add injury/medical keyword detection.
* [ ] Add refusal/fallback templates.
* [ ] Add beginner intensity validator.
* [ ] Add unsafe exercise validator.
* [ ] Log safety trigger events.
* [ ] Integrate safety checks into generation flow.

### Done when

* [ ] Medical-risk inputs trigger fallback.
* [ ] Beginner overload cases are detected.
* [ ] Unsafe exercise cases are handled.
* [ ] Safety trigger events are logged.

### Evidence

* PR link.
* Example unsafe input and fallback output.
* Log screenshot.

---

## Issue 17 — [Safety] Add safety test cases

**Priority:** P0
**Epic:** Safety
**Milestone:** M3 — Safety + Eval Baseline
**Type:** Test

### Scope

* [ ] Add injury-related test cases.
* [ ] Add medical-risk test cases.
* [ ] Add beginner-overload test cases.
* [ ] Add unsafe exercise test cases.
* [ ] Define expected fallback behavior.
* [ ] Add tests to local test suite.

### Done when

* [ ] Safety tests exist.
* [ ] Expected fallback behavior is covered.
* [ ] Tests can be run locally.
* [ ] Safety failures are easy to detect.

### Evidence

* PR link.
* Test result screenshot/log.

---

## Issue 18 — [Evals] Create eval dataset and rubric v1

**Priority:** P0
**Epic:** Evals
**Milestone:** M3 — Safety + Eval Baseline
**Type:** Test / Documentation

### Scope

* [ ] Create eval dataset v1 with 30 cases.
* [ ] Define eval rubric.
* [ ] Add expected behavior per case.
* [ ] Add risk tags.
* [ ] Include normal, edge, and unsafe scenarios.
* [ ] Document scoring criteria.

### Done when

* [ ] Eval dataset exists.
* [ ] At least 30 cases are included.
* [ ] Rubric is documented.
* [ ] Each case has expected behavior.

### Evidence

* PR link.
* `evals/datasets/workout_plan_eval_v1.jsonl`.
* `docs/eval-design.md`.

---

## Issue 19 — [Evals] Implement eval runner v1

**Priority:** P0
**Epic:** Evals
**Milestone:** M3 — Safety + Eval Baseline
**Type:** Feature / Test

### Scope

* [ ] Load eval dataset.
* [ ] Run generation flow for each case.
* [ ] Check schema validity.
* [ ] Check safety behavior.
* [ ] Check personalization.
* [ ] Check clarity.
* [ ] Generate markdown or CSV eval report.

### Done when

* [ ] Eval runner can be executed from command line.
* [ ] Eval report is generated.
* [ ] Schema and safety checks are included.
* [ ] Failed cases are visible.

### Evidence

* PR link.
* Eval report.
* Command output screenshot/log.

---

## Issue 20 — [Evals] Add failed case analysis v1

**Priority:** P1
**Epic:** Evals
**Milestone:** M3 — Safety + Eval Baseline
**Type:** Test / Documentation

### Scope

* [ ] Review failed eval cases.
* [ ] Categorize failure types.
* [ ] Identify prompt, retrieval, schema, or safety issues.
* [ ] Document top failure patterns.
* [ ] Create follow-up improvement tasks.

### Done when

* [ ] Failed cases are categorized.
* [ ] Failure taxonomy v1 exists.
* [ ] Follow-up issues are created if needed.

### Evidence

* PR link.
* Failed case analysis document.
* Linked follow-up issues.

---

## Issue 21 — [Docs] Write eval and safety design docs

**Priority:** P1
**Epic:** Documentation
**Milestone:** M3 — Safety + Eval Baseline
**Type:** Documentation

### Scope

* [ ] Write eval design doc.
* [ ] Write safety policy doc.
* [ ] Add known limitations.
* [ ] Add examples of pass/fail cases.
* [ ] Explain why eval-first matters for this project.

### Done when

* [ ] Eval design is documented.
* [ ] Safety design is documented.
* [ ] Limitations are clear.
* [ ] Docs can be used later for interview preparation.

### Evidence

* PR link.
* `docs/eval-design.md`.
* `docs/safety-policy.md`.

---

# Deferred Backlog — Create Later

The following milestones should not be fully created as GitHub Issues too early. Keep them in the master plan and create detailed issues when M2 or M3 is nearly complete.

---

# Milestone 4 — Deployed MVP and First Real Users

Create these issues later.

## Proposed Issues

### [Deployment] Deploy MVP backend and frontend

Suggested checklist:

* [ ] Deploy backend.
* [ ] Deploy frontend.
* [ ] Setup environment variables.
* [ ] Setup deployed database.
* [ ] Setup deployed Qdrant or managed vector DB.
* [ ] Test full user flow on deployed app.
* [ ] Add public demo link to README.

---

### [Feedback] Add user feedback collection flow

Suggested checklist:

* [ ] Add feedback form after plan generation.
* [ ] Add feedback schema.
* [ ] Store feedback.
* [ ] Link feedback to generated plan.
* [ ] Create feedback review page or report.

---

### [Feedback] Collect first real user feedback

Suggested checklist:

* [ ] Invite first 5 real users.
* [ ] Collect at least 10 feedback entries.
* [ ] Review common complaints.
* [ ] Identify product changes from feedback.
* [ ] Add changelog based on feedback.

---

### [Docs] Add public demo link and changelog

Suggested checklist:

* [ ] Add public demo link to README.
* [ ] Add basic usage instructions.
* [ ] Add changelog.
* [ ] Add feedback summary placeholder.
* [ ] Add known limitations.

---

# Milestone 5 — Observability and Metrics

Create these issues later.

## Proposed Issues

### [Observability] Integrate Langfuse tracing

Suggested checklist:

* [ ] Integrate Langfuse.
* [ ] Trace generation request.
* [ ] Track prompt version.
* [ ] Track retrieved chunks.
* [ ] Track model name.
* [ ] Track workflow steps.

---

### [Observability] Track LLM cost, latency, and failures

Suggested checklist:

* [ ] Track input/output tokens.
* [ ] Track latency.
* [ ] Track estimated cost.
* [ ] Track validation errors.
* [ ] Track retry count.
* [ ] Track safety trigger.
* [ ] Create cost/latency report.

---

### [Observability] Link feedback to request traces

Suggested checklist:

* [ ] Add request ID to generation flow.
* [ ] Store request ID with feedback.
* [ ] Link feedback to trace.
* [ ] Review traces for negative feedback.
* [ ] Document observed failure modes.

---

### [Evals] Add advanced evals and regression comparison

Suggested checklist:

* [ ] Add LLM-as-judge evaluator.
* [ ] Add groundedness score.
* [ ] Add difficulty-fit score.
* [ ] Add prompt/model regression comparison.
* [ ] Expand dataset to 50–100 cases.
* [ ] Convert repeated user complaints into eval cases.

---

### [Optimization] Run first cost/latency optimization experiment

Suggested checklist:

* [ ] Identify slowest requests.
* [ ] Identify most expensive prompts.
* [ ] Run prompt compression experiment.
* [ ] Run top-k retrieval experiment.
* [ ] Measure before/after optimization.
* [ ] Document result with numbers.

---

### [Agentic Workflow] Add controlled workflow tools experiment

Suggested checklist:

* [ ] Define where agentic behavior is useful.
* [ ] Define max steps.
* [ ] Define timeout.
* [ ] Define budget cap.
* [ ] Define fallback path.
* [ ] Add simple workflow tools.
* [ ] Add LangGraph experiment, optional.
* [ ] Trace each workflow step.

---

# Milestone 6 — Interview-ready Portfolio Package

Create these issues later.

## Proposed Issues

### [Docs] Polish README and architecture documentation

Suggested checklist:

* [ ] Write polished README.
* [ ] Add architecture diagram.
* [ ] Explain tech stack.
* [ ] Explain RAG design.
* [ ] Explain eval design.
* [ ] Explain safety guardrails.
* [ ] Explain observability.
* [ ] Add local setup and deployment notes.

---

### [Docs] Prepare project evidence package

Suggested checklist:

* [ ] Add screenshots.
* [ ] Add Langfuse trace screenshots.
* [ ] Add eval report screenshots.
* [ ] Add demo screenshots.
* [ ] Add changelog.
* [ ] Add “lessons learned” page.

---

### [Docs] Write user feedback and metrics summary

Suggested checklist:

* [ ] Summarize number of users.
* [ ] Summarize feedback entries.
* [ ] Summarize repeated issues.
* [ ] Summarize changes made from feedback.
* [ ] Summarize cost, latency, and eval metrics.

---

### [Interview] Prepare CV bullet points and talking points

Suggested checklist:

* [ ] Prepare CV bullet points.
* [ ] Prepare project summary.
* [ ] Prepare RAG explanation.
* [ ] Prepare eval explanation.
* [ ] Prepare safety explanation.
* [ ] Prepare observability explanation.
* [ ] Prepare lessons learned.
* [ ] Prepare future roadmap explanation.

---

### [Demo] Record demo video

Suggested checklist:

* [ ] Record 3–5 minute demo video.
* [ ] Show profile intake.
* [ ] Show workout plan generation.
* [ ] Show retrieved context if possible.
* [ ] Show feedback flow.
* [ ] Show eval/metrics evidence.
* [ ] Add demo video link to README.

---

## Backlog Management Rule

Do not create every small task as a GitHub Issue.

Use this rule:

```text
GitHub Issue = meaningful outcome
Checklist item = small implementation step
Pull Request = concrete code/doc change
Evidence = proof that the issue is truly done
```

Create detailed issues only for the current or next milestone.

Recommended workflow:

```text
During M1:
- Create M1 issues.
- Create only essential M2 issues.

During M2:
- Refine M2 issues.
- Create M3 issues.

During M3:
- Refine safety/eval work.
- Create M4 issues.

During M4:
- Create M5 issues based on real user feedback and observed failures.

During M5:
- Create M6 issues for interview-ready packaging.
```

The goal is to avoid over-planning while still keeping the project direction clear.

## 11. Project Tracking Rules

## Weekly Review Questions

Use these questions regularly:

1. What did I ship this week?
2. What evidence did I produce?
3. What did I learn technically?
4. What failed?
5. What user feedback did I collect?
6. What metric changed?
7. What should be converted into an eval case?
8. What is the next smallest valuable task?

## Evidence Rule

A task is not truly done unless it has evidence:

- PR link.
- Screenshot.
- Demo link.
- Eval report.
- Langfuse trace.
- User feedback.
- Test result.
- Documentation page.

## Avoid This

- Do not mark large vague tasks as done.
- Do not build too many features before evals.
- Do not over-focus on UI before the AI workflow is measurable.
- Do not use only AI-generated code without understanding it.
- Do not add agentic complexity before the deterministic workflow is working.

---

## 12. Learning Roadmap

## Track 1 — Python and FastAPI

Must know:

- FastAPI routes.
- Pydantic schemas.
- Request/response validation.
- Error handling.
- Async basics.
- Logging.
- Docker.

Evidence:

- Backend runs locally.
- API docs available.
- Tests pass.

---

## Track 2 — Direct LLM SDK Usage

Must know:

- OpenAI SDK direct calls.
- Anthropic SDK direct calls, optional but useful.
- Structured output.
- Function/tool calling.
- Streaming.
- Retry handling.
- Timeout handling.
- Token/cost tracking.

Evidence:

- LLM calls are implemented directly.
- Output is validated.
- Malformed output is handled.
- Cost/latency is logged.

---

## Track 3 — RAG

Must know:

- Embeddings.
- Chunking.
- Vector DB.
- Top-k retrieval.
- Metadata filtering.
- Retrieval quality evaluation.
- Grounding and hallucination analysis.

Evidence:

- Qdrant collection exists.
- Retrieval works.
- Retrieved chunks are logged.
- Retrieval eval cases exist.

---

## Track 4 — Evals

Must know:

- Eval dataset design.
- Rubric design.
- Regression testing.
- LLM-as-judge.
- Safety evals.
- Failure taxonomy.

Evidence:

- Eval runner exists.
- Eval report exists.
- Failed cases are tracked.
- User feedback becomes eval cases.

---

## Track 5 — Observability

Must know:

- LLM tracing.
- Prompt versioning.
- Cost tracking.
- Latency tracking.
- Failure analysis.

Evidence:

- Langfuse traces exist.
- Metrics are summarized.
- Optimization result has numbers.

---

## Track 6 — Fitness Domain Basics

Must know:

- Beginner training principles.
- Progressive overload.
- Recovery.
- Exercise categories.
- Safety boundaries.
- Difference between general fitness guidance and medical advice.

Evidence:

- Knowledge base has curated sources.
- Safety policy exists.
- Unsafe cases are handled.

---

## 13. Interview Preparation Notes

## Key Message

> I built this project to practice production-minded LLM engineering, not just prompt engineering. The system includes structured output, RAG, validation, retries, guardrails, evals, observability, user feedback, and continuous improvement.

## Questions to Be Ready For

### LLM / Structured Output

- Why did you use structured output instead of plain text?
- What happens when the model returns malformed JSON?
- How do you validate the plan before showing it to users?
- How do you handle retries and fallback?

### RAG

- What documents are in your knowledge base?
- How did you choose chunk size?
- How do you evaluate retrieval quality?
- What happens when retrieval returns irrelevant chunks?
- How do you reduce hallucination?

### Evals

- What does “good output” mean in this project?
- How did you design the eval dataset?
- What metrics do you track?
- How do you detect regression after prompt changes?
- How did user feedback become eval cases?

### Safety

- How do you handle injury or medical cases?
- What are the boundaries of your assistant?
- What does fail-closed mean in your system?
- Which safety checks are prompt-based and which are code-based?

### Observability

- How do you track cost?
- How do you track latency?
- How do you debug a bad response?
- How do you know which prompt version performs better?

### Product Thinking

- What did real users say?
- What did you change after feedback?
- What would you improve next?
- What trade-offs did you make?

---

## 14. CV Bullet Point Drafts

Use after evidence exists. Do not use these before implementation.

### Version 1 — General

- Built a RAG-powered AI fitness coaching assistant using Python, FastAPI, OpenAI SDK, Qdrant, and Langfuse, generating structured workout plans with schema validation, safety guardrails, evals, and user feedback loops.

### Version 2 — Eval-focused

- Designed an eval-first LLM workflow for personalized workout plan generation, including structured output validation, safety test cases, LLM-as-judge rubrics, regression reports, and failure analysis.

### Version 3 — Observability-focused

- Integrated LLM observability to track prompt versions, retrieved context, token usage, latency, cost, retries, safety triggers, and user feedback for continuous improvement.

### Version 4 — User feedback-focused

- Deployed an AI fitness planning MVP to real users, collected feedback, converted recurring issues into eval cases, and iterated on prompts, retrieval, and safety rules based on observed failures.

---

## 15. README Checklist

The final README should include:

- [ ] Project overview.
- [ ] Problem statement.
- [ ] Target users.
- [ ] Demo link.
- [ ] Demo video.
- [ ] Architecture diagram.
- [ ] Tech stack.
- [ ] Main features.
- [ ] RAG design.
- [ ] Structured output design.
- [ ] Safety guardrails.
- [ ] Eval design.
- [ ] Observability.
- [ ] User feedback.
- [ ] Metrics.
- [ ] Known limitations.
- [ ] Roadmap.
- [ ] Local setup.
- [ ] Deployment notes.

---

## 16. Apply Readiness Levels

## Level 1 — Too Early

You only have:

- Local demo.
- No RAG.
- No evals.
- No users.

Use for learning only.

## Level 2 — Can Apply Early if Job May Close

You have:

- FastAPI backend.
- Direct LLM SDK.
- Structured output.
- Basic RAG.
- Basic README.

Risk:

- Still weak on real user evidence.

## Level 3 — Reasonable to Apply

You have:

- Deployed MVP.
- RAG.
- Safety guardrails.
- Eval baseline.
- Some real user feedback.
- Clear roadmap.

This is the first serious apply point.

## Level 4 — Strong Portfolio

You have:

- Observability.
- Metrics.
- User feedback loop.
- Cost/latency analysis.
- Eval reports.
- Demo video.
- Interview notes.

This is the target state for confident interviewing.

---

## 17. Guiding Principles

1. Build narrow, but deep.
2. Prioritize evidence over claims.
3. Treat evals as a core feature, not an afterthought.
4. Treat safety as system design, not only prompt wording.
5. Use AI coding tools to accelerate, but understand every critical decision.
6. Keep a changelog of failures and improvements.
7. Convert user feedback into eval cases.
8. Avoid over-engineering before the MVP works.
9. Make the project explainable to interviewers.
10. Always ask: “How will I measure this?” before building.

---

## 18. Immediate Next Actions

Start with these tasks:

- [ ] Create GitHub repository: `fitcoach-ai`.
- [ ] Add this file as `MASTER_PLAN.md`.
- [ ] Create GitHub Project.
- [ ] Add fields: Status, Priority, Epic, Milestone, Type, Confidence, Evidence.
- [ ] Create milestones M1–M6.
- [ ] Add initial P0 tasks from Epic A and Epic B.
- [ ] Create backend FastAPI skeleton.
- [ ] Define initial schemas.
- [ ] Implement first direct OpenAI structured output call.
- [ ] Write first README draft.

---

## 19. First GitHub Project Items to Create

Create these issues first:

1. Setup repository structure.
2. Setup FastAPI backend skeleton.
3. Define user profile schema.
4. Define workout plan schema.
5. Implement OpenAI SDK client.
6. Implement structured workout plan generation.
7. Add Pydantic validation for LLM output.
8. Add retry and fallback for malformed output.
9. Add token, cost, and latency logging.
10. Write README v0.

Recommended first focus:

> Do not start with UI. First make the backend generate a valid, structured, testable workout plan.

---

## 20. Long-term Roadmap

## V1 — MVP

- Single user flow.
- Structured workout plan generation.
- Basic RAG.
- Basic safety.
- Basic feedback.

## V2 — Evaluation and Observability

- Eval dataset.
- Eval runner.
- Langfuse tracing.
- Cost/latency dashboard.
- Failure taxonomy.

## V3 — User-driven Iteration

- More user feedback.
- Feedback-to-eval conversion.
- Prompt/retrieval improvements.
- Metrics improvements.

## V4 — Controlled Agentic Workflow

- Workflow tools.
- Max steps.
- Budget cap.
- Timeout.
- Fallback.
- Optional LangGraph experiment.

## V5 — Interview-ready Package

- Demo video.
- Architecture diagram.
- Metrics report.
- Eval report.
- User feedback summary.
- CV bullets.
- Interview Q&A.

---

## 21. Final Reminder

This project is not only about building an app. It is about building a credible story:

> I can take an LLM feature from idea to MVP, make it structured and testable, ground it with retrieval, evaluate its quality, monitor its cost and latency, handle safety risks, collect user feedback, and iterate like a real AI product engineer.

That is the capability this portfolio should prove.
