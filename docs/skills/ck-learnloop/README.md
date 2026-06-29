# `ck:learnloop`

Portable skill package for building and maintaining a local-first learning
system from a real corpus.

## What this captures

`ck:learnloop` packages the reusable framework behind the FitCoach learning
system without coupling it to FitCoach runtime details.

Core loop:

- `reference`
- `recall`
- `explain`
- `predict`
- `drill`

Maintenance stance:

- review both explanation and practice when source knowledge changes
- prefer deterministic local validation
- avoid fake authoritative grading
- avoid overengineering before one real topic works

## Good fits

Use it for:

- software repos
- docs or notes collections
- personal learning systems
- personal development frameworks
- other curated knowledge domains

## Package contents

- [SKILL.md](./SKILL.md)
  Core operating instructions
- [references/learning-principles.md](./references/learning-principles.md)
  Learning model and guardrails
- [references/domain-adaptation.md](./references/domain-adaptation.md)
  Domain mapping beyond software
- [references/maintenance-workflow.md](./references/maintenance-workflow.md)
  Update workflow when source knowledge changes
- [assets/quiz-pack-template.toml](./assets/quiz-pack-template.toml)
  Starter recall/explain pack
- [assets/prediction-pack-template.toml](./assets/prediction-pack-template.toml)
  Starter prediction pack
- [assets/drill-pack-template.toml](./assets/drill-pack-template.toml)
  Starter drill pack
- [assets/maintenance-guide-template.md](./assets/maintenance-guide-template.md)
  Starter maintenance guide

## Minimal adoption flow

1. Pick one bounded corpus.
2. Choose one topic.
3. Create one quiz/explain pack.
4. Add one prediction pack only if causal reasoning matters.
5. Add one drill only if a trustworthy local validation path exists.
6. Write the maintenance guide before scaling topic count.

## Reference implementation

FitCoach provides one concrete reference shape:

- portal reference content under `backend/app/learning/content/`
- practice packs under `backend/app/learning/exercises/`
- quiz runtime under `backend/app/learning/quiz/`
- drill runtime under `backend/app/learning/drills/`

That implementation is a reference, not a requirement. Another project can keep
only the content model and templates.

## Reuse in another project

1. Copy `docs/skills/ck-learnloop/` into the target repo.
2. Adapt the templates to the target corpus and validation style.
3. Fill in project-specific validation commands in the maintenance guide.
4. Install as a local/global skill later only if you want auto-activation.

## Likely next extensions

- spaced-review metadata
- confidence capture
- misconception tracking
- more validator patterns by domain
- lightweight eval cases for the skill package
