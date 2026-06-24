# Knowledge Source Policy

## Purpose

The knowledge base should ground workout generation with stable, beginner-safe,
non-sensational fitness guidance. It is not a substitute for medical advice,
diagnosis, or rehabilitation programming.

## Allowed source classes

- Internal curated notes written for this repository when they are clearly
  labeled as curated and limited in scope.
- Reputable public guidance from established health, sports medicine, or public
  health organizations.
- Technical references that explain beginner training principles, exercise
  selection, recovery, and general physical activity guidance.

## Disallowed source classes

- Social posts, short-form creator content, or anonymous forum advice.
- Content that makes medical, rehabilitation, or injury-treatment claims without
  strong authority.
- Extreme transformation, detox, or pain-through-it style advice.
- Sources that cannot be dated or traced.

## Content rules for v1

- Prefer low-risk beginner topics: frequency, intensity, exercise balance,
  warm-up, recovery, and general safety.
- Avoid prescriptive nutrition, supplementation, diagnosis, or treatment claims.
- Keep statements concrete enough for retrieval but generic enough to stay safe
  without individual assessment.
- Flag any red-flag symptoms or medical clearance needs instead of trying to
  solve them inside the corpus.

## Document format rules

Each chunkable source document should:

- live under `knowledge_base/raw/<topic>/`
- use markdown
- begin with metadata front matter
- use a stable `document_id`
- include topic-specific headings and short list items that chunk cleanly

Required front matter keys:

- `document_id`
- `title`
- `topic`
- `source_type`
- `intended_use`
- `last_reviewed`
- `status`

## Review policy

- Internal curated documents may be used for local MVP development.
- Before production or public health claims are expanded, the corpus should be
  reviewed against authoritative external references.
- Any future external document added to the corpus should also be recorded in
  `sources.md`.
