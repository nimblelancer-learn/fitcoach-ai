# Maintenance Workflow

Use this whenever the source corpus changes.

## Update sequence

1. Read the changed source material first.
2. List what changed:
   - facts
   - explanations
   - workflows
   - likely outcomes
   - bounded tasks or validation paths
3. Review every surface:
   - `reference`
   - `recall`
   - `explain`
   - `predict`
   - `drill`
4. Update the smallest files that restore truth.
5. Run local validation.
6. Update one focused test if a content contract changed.

## Surface decisions

- Update `reference` when the stable explanation changed.
- Update `recall` when factual answers or distinctions changed.
- Update `explain` when expected reasoning or architecture story changed.
- Update `predict` when expected outcomes or follow-up checks changed.
- Update `drill` when the applied task or its validator changed.

## Anti-drift checks

- Is any answer now wrong?
- Is any expected point stale?
- Does any prediction scenario still match a real source event?
- Does any drill validator still match a trustworthy local check?
- Does the maintenance guide still describe the current system?

## Anti-drift policy

- Never update only reference prose if practice content drifted too.
- Never keep a validator that no longer proves the intended thing.
- Never keep a prediction prompt detached from real source behavior.
- Never broaden the framework before the current loop is truthful and usable.
