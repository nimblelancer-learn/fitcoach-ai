from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE_ROOT = REPO_ROOT / "knowledge_base"
RAW_ROOT = KNOWLEDGE_BASE_ROOT / "raw"
REQUIRED_FRONT_MATTER_KEYS = {
    "document_id",
    "title",
    "topic",
    "source_type",
    "intended_use",
    "last_reviewed",
    "status",
}


def _parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)

    assert parts[0] == ""
    assert len(parts) == 3

    metadata: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        key, _, value = line.partition(":")
        metadata[key.strip()] = value.strip()
    return metadata


def test_knowledge_base_v1_structure_exists() -> None:
    assert KNOWLEDGE_BASE_ROOT.is_dir()
    assert (KNOWLEDGE_BASE_ROOT / "source-policy.md").is_file()
    assert (KNOWLEDGE_BASE_ROOT / "sources.md").is_file()
    assert RAW_ROOT.is_dir()
    assert (KNOWLEDGE_BASE_ROOT / "processed").is_dir()


def test_chunkable_documents_have_required_metadata() -> None:
    documents = sorted(RAW_ROOT.rglob("*.md"))

    assert len(documents) >= 5

    for path in documents:
        metadata = _parse_front_matter(path)
        assert REQUIRED_FRONT_MATTER_KEYS.issubset(metadata)
        assert metadata["status"] == "approved_for_chunking"


def test_sources_inventory_mentions_all_raw_documents() -> None:
    sources_text = (KNOWLEDGE_BASE_ROOT / "sources.md").read_text(encoding="utf-8")

    for path in sorted(RAW_ROOT.rglob("*.md")):
        metadata = _parse_front_matter(path)
        assert metadata["document_id"] in sources_text
        relative_path = path.relative_to(KNOWLEDGE_BASE_ROOT).as_posix()
        assert relative_path in sources_text
