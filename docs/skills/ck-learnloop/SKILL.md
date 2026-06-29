---
name: ck:learnloop
description: Build or maintain a local-first learning system from a real corpus. Use for repos, docs, notes, personal learning, or other domains that need recall, explain, predict, and drill loops.
version: "0.2.0"
---

# Learnloop

Build or maintain a local-first learning system from a real source corpus.
Use this skill when the user wants active learning loops from code, docs,
notes, journals, study material, or another bounded knowledge base.

This skill handles:

- corpus-to-learning-system design
- `reference`, `recall`, `explain`, `predict`, `drill` surface design
- local-first content authoring
- maintenance when source knowledge changes
- honest validation design

This skill does NOT handle:

- production LMS platforms
- fake authoritative AI grading
- broad autonomous research without a bounded corpus
- unnecessary runtime/framework complexity

## Scope And Guardrails

- Use the real corpus as source of truth.
- Keep content data-first: prompts, rubrics, scenarios, and validators belong in
  files, not hidden runtime logic.
- Prefer self-review for nuanced explanation tasks.
- Prefer deterministic validation for drills.
- Refuse to claim precise grading when the check is only heuristic.
- Start with one small topic before generalizing.

## When To Use

Use this skill when the user wants to:

- turn a repo, doc set, or notes collection into a learning system
- add quiz, explain-back, prediction, or drill content
- maintain learning content after the source corpus changes
- package a reusable learning framework for another project or domain

## Workflow

1. Define the corpus.
   Decide what the source of truth is: repo, docs, notes, transcripts, or a
   curated mixed corpus.
2. Map the learning surfaces.
   Split content into:
   - `reference`
   - `recall`
   - `explain`
   - `predict`
   - `drill`
3. Build the smallest useful loop.
   Start with one topic and one real pack.
4. Choose honest validation.
   Use reveal/self-review for explanation. Use deterministic checks for drills.
5. Add maintenance rules.
   When the corpus changes, review both explanation and practice surfaces.
6. Keep the framework portable.
   Avoid runtime coupling unless the user explicitly wants project-specific app
   integration.

## Content Design Rules

- `reference`: explain stable structure, terminology, and flow.
- `recall`: test facts, distinctions, and compact answers.
- `explain`: ask the learner to explain purpose, relationships, or tradeoffs.
- `predict`: ask what happens after a change, choice, or event.
- `drill`: ask for one bounded artifact or action with a local validation path.

## Maintenance Rules

- When source knowledge changes, review `reference`, `recall`, `explain`,
  `predict`, and `drill`.
- Do not update only prose if practice content became stale.
- Do not keep drills whose validator no longer matches a trustworthy local
  check.
- Do not add abstractions before one real topic works end to end.

## Bundled Resources

Read these references as needed:

- `references/learning-principles.md`
  Use for the core model and anti-fake-grading guardrails.
- `references/domain-adaptation.md`
  Use for adapting the framework beyond software repos.
- `references/maintenance-workflow.md`
  Use when the source corpus changed or the system is drifting.

Reuse these assets:

- `assets/quiz-pack-template.toml`
- `assets/prediction-pack-template.toml`
- `assets/drill-pack-template.toml`
- `assets/maintenance-guide-template.md`

## Expected Outputs

When using this skill, produce:

1. the chosen corpus and learning surfaces
2. the pack or drill structure to create or update
3. the validation approach
4. the maintenance workflow
5. only the smallest usable set of files
