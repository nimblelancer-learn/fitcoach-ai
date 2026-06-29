# Learning System Maintenance Guide

This guide is the source of truth for keeping curated learning content aligned
with the current corpus.

## Learning Surfaces

- `reference`:
- `recall`:
- `explain`:
- `predict`:
- `drill`:

## When To Update

Update `reference` when stable explanation changed.

Update practice content when:

- facts changed
- expected reasoning changed
- likely outcomes changed
- the bounded task or validation path changed

Update both when the learner should both understand and rehearse the change.

## Source-Change Workflow

1. Read the changed source material first.
2. List what changed:
   - facts
   - explanations
   - likely outcomes
   - bounded tasks
3. Review all five surfaces.
4. Update the smallest files that restore truth.
5. Run validation.
6. Update focused tests if the content contract changed.

## Anti-Drift Checklist

- [ ] Source references still exist.
- [ ] Answers and expected points are still true.
- [ ] Prediction outcomes still match real behavior.
- [ ] Drill validators still prove the intended thing.
- [ ] The maintenance guide still matches the current system.

## Validation Commands

```bash
# Add project-specific lint, tests, loader checks, and smoke commands here.
```
