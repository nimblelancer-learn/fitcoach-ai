from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE_ROOT = REPO_ROOT / "knowledge_base"
RAW_ROOT = KNOWLEDGE_BASE_ROOT / "raw"
PROCESSED_ROOT = KNOWLEDGE_BASE_ROOT / "processed"
DEFAULT_OUTPUT_PATH = PROCESSED_ROOT / "chunks-v1.json"
SCHEMA_VERSION = "chunk-set-v1"
TARGET_WORDS = 120
MAX_WORDS = 180


@dataclass(frozen=True)
class RawDocument:
    source_path: str
    metadata: dict[str, str]
    body: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    document_id: str
    source_path: str
    title: str
    topic: str
    source_type: str
    intended_use: str
    last_reviewed: str
    status: str
    chunk_index: int
    section_path: list[str]
    word_count: int
    text: str


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    parts = text.split("---", 2)
    if parts[0] != "" or len(parts) != 3:
        raise ValueError("expected markdown file with front matter")

    metadata: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"invalid front matter line: {line!r}")
        metadata[key.strip()] = value.strip()
    return metadata, parts[2].strip()


def load_raw_document(path: Path) -> RawDocument:
    metadata, body = _split_front_matter(path.read_text(encoding="utf-8"))
    return RawDocument(
        source_path=path.relative_to(KNOWLEDGE_BASE_ROOT).as_posix(),
        metadata=metadata,
        body=body,
    )


def load_raw_documents(raw_root: Path = RAW_ROOT) -> list[RawDocument]:
    return [load_raw_document(path) for path in sorted(raw_root.rglob("*.md"))]


def _iter_blocks(lines: Iterable[str]) -> Iterable[list[str]]:
    block: list[str] = []
    for raw_line in lines:
        line = raw_line.rstrip()
        if line.strip():
            block.append(line)
            continue
        if block:
            yield block
            block = []
    if block:
        yield block


def _word_count(text: str) -> int:
    return len(text.split())


def _section_units(body: str) -> list[tuple[list[str], str]]:
    section_stack: list[tuple[int, str]] = []
    current_section: list[str] = []
    current_lines: list[str] = []
    units: list[tuple[list[str], str]] = []

    def flush_current() -> None:
        if not current_lines:
            return
        for block in _iter_blocks(current_lines):
            text = "\n".join(block).strip()
            if text:
                units.append((current_section[:], text))
        current_lines.clear()

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            marker, _, heading = stripped.partition(" ")
            if heading and set(marker) == {"#"}:
                flush_current()
                level = len(marker)
                while section_stack and section_stack[-1][0] >= level:
                    section_stack.pop()
                section_stack.append((level, heading.strip()))
                current_section = [entry[1] for entry in section_stack]
                continue
        current_lines.append(line)

    flush_current()
    return units


def chunk_document(
    document: RawDocument,
    *,
    target_words: int = TARGET_WORDS,
    max_words: int = MAX_WORDS,
) -> list[Chunk]:
    units = _section_units(document.body)
    if not units:
        return []

    metadata = document.metadata
    chunks: list[Chunk] = []
    current_texts: list[str] = []
    current_section: list[str] = []
    current_word_count = 0

    def flush() -> None:
        nonlocal current_texts, current_section, current_word_count
        if not current_texts:
            return
        chunk_index = len(chunks)
        combined_text = "\n\n".join(current_texts)
        chunks.append(
            Chunk(
                chunk_id=f"{metadata['document_id']}::chunk-{chunk_index:03d}",
                document_id=metadata["document_id"],
                source_path=document.source_path,
                title=metadata["title"],
                topic=metadata["topic"],
                source_type=metadata["source_type"],
                intended_use=metadata["intended_use"],
                last_reviewed=metadata["last_reviewed"],
                status=metadata["status"],
                chunk_index=chunk_index,
                section_path=current_section[:],
                word_count=_word_count(combined_text),
                text=combined_text,
            )
        )
        current_texts = []
        current_section = []
        current_word_count = 0

    for section_path, text in units:
        unit_words = _word_count(text)
        starts_new_section = bool(current_section and current_section != section_path)
        exceeds_target = current_word_count >= target_words
        would_exceed_max = current_word_count and current_word_count + unit_words > max_words
        if starts_new_section and exceeds_target:
            flush()
        elif would_exceed_max:
            flush()

        if not current_section:
            current_section = section_path[:]
        current_texts.append(text)
        current_word_count += unit_words

    flush()
    return chunks


def build_chunk_artifact(raw_root: Path = RAW_ROOT) -> dict[str, object]:
    documents = load_raw_documents(raw_root)
    chunks = [chunk for document in documents for chunk in chunk_document(document)]
    return {
        "schema_version": SCHEMA_VERSION,
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "documents": [
            {
                "document_id": document.metadata["document_id"],
                "source_path": document.source_path,
                "title": document.metadata["title"],
                "topic": document.metadata["topic"],
                "status": document.metadata["status"],
            }
            for document in documents
        ],
        "chunks": [asdict(chunk) for chunk in chunks],
    }


def write_chunk_artifact(output_path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    artifact = build_chunk_artifact()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    output_path = write_chunk_artifact()
    print(f"Wrote {output_path.relative_to(REPO_ROOT)} from {RAW_ROOT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
