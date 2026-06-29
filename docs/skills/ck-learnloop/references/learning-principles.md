# Learning Principles

Use these principles when designing or maintaining a learning system from a
real corpus.

## Core model

1. `reference`
   Read the source of truth.
2. `recall`
   Retrieve facts without looking.
3. `explain`
   Explain purpose, mechanism, or relationship.
4. `predict`
   Anticipate the result of a change, choice, or event.
5. `drill`
   Perform one bounded applied task.

## Why this sequence works

- `recall` fights familiarity illusions
- `explain` exposes shallow understanding
- `predict` trains causal reasoning
- `drill` connects knowledge to action

## Guardrails

- Do not present heuristic AI scoring as authoritative.
- Use self-review for nuanced explanation tasks.
- Keep expected points concise.
- Keep prediction scenarios concrete.
- Keep drills bounded to one objective and one validation path.
- Prefer local-first and low-friction systems over platform complexity.
- Avoid abstractions that appear before one real topic works end to end.

## Honest validation patterns

Good:

- reveal plus self-check
- expected-point coverage review
- answer-file substring checks
- exact option selection
- focused test or command targets

Bad:

- broad "AI says this is correct" grading
- vague open-ended drills with no validation path
- framework complexity that hides the corpus behind orchestration

## Growth pattern

Start with:

- one corpus
- one topic
- one pack

Then scale to:

- more topics
- cross-topic prediction prompts
- richer validator patterns
- optional metadata such as confidence, difficulty, or source revision
