---
phase: 1
title: Review corpus and chunk contract
status: completed
priority: P1
effort: ''
dependencies: []
---

# Phase 1: Review corpus and chunk contract

## Overview

Define the minimal chunk schema and output layout based on the current raw
document format and the RAG roadmap. The contract should be deterministic so
later embedding and retrieval work can depend on stable fields instead of
having to reverse-engineer one-off sample files.

## Requirements

- Functional: Parse all markdown files in `knowledge_base/raw/`, preserve front
  matter metadata, and expose enough chunk metadata for downstream retrieval.
- Non-functional: Keep the format simple, human-inspectable, and reproducible
  from source files without external services.

## Architecture

The chunking pipeline should treat the current raw markdown files as the single
source of truth. A backend utility module should:

1. read each raw markdown file
2. parse front matter and markdown body
3. split body content into bounded chunks using headings and paragraph/list
   boundaries where possible
4. write a normalized JSON artifact under `knowledge_base/processed/`

The chunk schema should include document-level metadata (`document_id`,
`title`, `topic`, `source_type`, `intended_use`, `last_reviewed`, `status`)
plus chunk-level metadata (`chunk_id`, `chunk_index`, `section_path`, `text`,
and a small size proxy such as `word_count`).

## Related Code Files

- Create: `backend/app/rag/__init__.py`
- Create: `backend/app/rag/chunking.py`
- Create: `backend/tests/rag/test_chunking.py`
- Modify: `knowledge_base/processed/README.md`
- Modify: `knowledge_base/README.md`
- Modify: `README.md`

## Implementation Steps

1. Inspect the raw document format and choose the smallest chunk contract that
   satisfies the issue checklist and later retrieval needs.
2. Decide on the processed output shape, likely one JSON file containing all
   chunk records.
3. Define deterministic chunk IDs so reprocessing the same content does not
   change identifiers unexpectedly.
4. Record the output path and CLI entrypoint that Phase 2 will implement.

## Success Criteria

- [ ] Chunk metadata fields are explicitly defined before implementation starts.
- [ ] The processed output location and file naming strategy are fixed.
- [ ] The contract is narrow enough to support issue `#14` without prematurely
      adding embeddings or vector-store concerns.

## Risk Assessment

The main risk is overengineering the chunk schema before embeddings and
retrieval exist. Mitigation: keep the output JSON-centric, deterministic, and
limited to fields that are directly useful for indexing and debugging.
