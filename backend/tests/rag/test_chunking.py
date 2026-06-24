import json
from pathlib import Path

from app.rag.chunking import (
    DEFAULT_OUTPUT_PATH,
    RAW_ROOT,
    SCHEMA_VERSION,
    build_chunk_artifact,
    load_raw_documents,
    write_chunk_artifact,
)


def test_build_chunk_artifact_covers_all_raw_documents() -> None:
    artifact = build_chunk_artifact()
    documents = load_raw_documents()

    assert artifact["schema_version"] == SCHEMA_VERSION
    assert artifact["document_count"] == len(documents)
    assert artifact["chunk_count"] == len(artifact["chunks"])
    assert artifact["chunk_count"] > artifact["document_count"]

    raw_document_ids = {document.metadata["document_id"] for document in documents}
    artifact_document_ids = {entry["document_id"] for entry in artifact["documents"]}
    chunk_document_ids = {entry["document_id"] for entry in artifact["chunks"]}

    assert artifact_document_ids == raw_document_ids
    assert chunk_document_ids == raw_document_ids


def test_chunk_artifact_is_deterministic() -> None:
    first = build_chunk_artifact()
    second = build_chunk_artifact()

    assert first == second


def test_chunk_records_include_expected_metadata() -> None:
    artifact = build_chunk_artifact()
    chunks = artifact["chunks"]

    assert chunks

    for index, chunk in enumerate(chunks):
        assert chunk["chunk_id"].endswith(f"{chunk['chunk_index']:03d}")
        assert chunk["source_path"].startswith("raw/")
        assert chunk["section_path"]
        assert chunk["text"]
        assert chunk["word_count"] > 0
        if index:
            assert chunk["chunk_id"] != chunks[index - 1]["chunk_id"]


def test_write_chunk_artifact_matches_checked_in_sample(tmp_path: Path) -> None:
    output_path = tmp_path / "chunks.json"
    write_chunk_artifact(output_path)

    generated = json.loads(output_path.read_text(encoding="utf-8"))
    checked_in = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))

    assert generated == checked_in


def test_checked_in_sample_is_rooted_in_current_raw_corpus() -> None:
    checked_in = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))

    assert checked_in["document_count"] == len(list(RAW_ROOT.rglob("*.md")))
