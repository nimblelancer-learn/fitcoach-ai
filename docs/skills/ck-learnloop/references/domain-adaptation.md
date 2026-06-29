# Domain Adaptation

Adapt the framework to the corpus. Do not force every domain into a
software-repo shape.

## Surface mapping by domain

### Software repo

- `reference`: architecture pages, module maps, request or startup flows
- `recall`: file roles, contracts, flags, workflows
- `explain`: why modules exist and how pieces fit together
- `predict`: effects of edits, config changes, or command choices
- `drill`: answer file, test selection, focused command

### Docs, notes, or books

- `reference`: chapter map, glossary, framework summary
- `recall`: definitions, distinctions, key claims
- `explain`: arguments, mechanisms, tradeoffs
- `predict`: what follows from a principle, case, or decision
- `drill`: short artifact checked against expected concepts

### Personal learning or personal development

- `reference`: routines, policies, frameworks, decision rules
- `recall`: triggers, constraints, steps, definitions
- `explain`: why a routine exists and when to use it
- `predict`: what happens if a rule is skipped, changed, or misapplied
- `drill`: one bounded reflection, planning, or review artifact

### Other non-software domains

Map the same five surfaces:

- `reference`: stable source explanation
- `recall`: factual retrieval
- `explain`: mechanism or purpose
- `predict`: consequences or likely outcomes
- `drill`: one bounded applied task

## Adaptation rules

- Keep prompts in the language of the corpus.
- Keep source references explicit.
- Use drills only when a bounded validation path exists.
- Do not force command-based drills for conceptual domains.
- Prefer answer-file, checklist, or exact-selection validation when operations
  are not code-centric.
- Keep one maintenance guide per corpus.
