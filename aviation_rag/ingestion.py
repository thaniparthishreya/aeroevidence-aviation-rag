from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path

from aviation_rag.models import Chunk, Document


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def stable_id(value: str, prefix: str = "doc") -> str:
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:12]}"


def load_json_documents(path: Path) -> list[Document]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload if isinstance(payload, list) else payload.get("documents", [])
    documents: list[Document] = []
    for record in records:
        text = normalize_text(record["text"])
        document_id = record.get("document_id") or stable_id(
            record.get("source_url", "") + record.get("title", "") + text[:200]
        )
        documents.append(
            Document(
                document_id=document_id,
                title=record.get("title", path.stem),
                text=text,
                source_url=record.get("source_url", ""),
                metadata=record.get("metadata", {}),
            )
        )
    return documents


def load_document(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_json_documents(path)
    if suffix in {".txt", ".md"}:
        text = normalize_text(path.read_text(encoding="utf-8"))
        return [Document(stable_id(str(path.resolve())), path.stem, text)]
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Install pypdf to ingest PDF files") from exc
        text = "\n\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        text = normalize_text(text)
        return [Document(stable_id(str(path.resolve())), path.stem, text)]
    return []


def load_directory(directory: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".json", ".txt", ".md", ".pdf"}:
            documents.extend(load_document(path))
    deduplicated = {document.document_id: document for document in documents}
    return list(deduplicated.values())


def _paragraph_units(text: str) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    units: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= 1200:
            units.append(paragraph)
        else:
            units.extend(
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", paragraph)
                if sentence.strip()
            )
    return units


def chunk_documents(
    documents: Iterable[Document], target_chars: int = 1100, overlap_units: int = 1
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        units = _paragraph_units(document.text)
        current: list[str] = []
        position = 0
        for unit in units:
            if current and sum(map(len, current)) + len(unit) > target_chars:
                text = "\n\n".join(current)
                chunks.append(
                    Chunk(
                        chunk_id=f"{document.document_id}_c{position:04d}",
                        document_id=document.document_id,
                        title=document.title,
                        text=text,
                        source_url=document.source_url,
                        metadata=document.metadata,
                        position=position,
                    )
                )
                position += 1
                current = current[-overlap_units:] if overlap_units else []
            current.append(unit)
        if current:
            chunks.append(
                Chunk(
                    chunk_id=f"{document.document_id}_c{position:04d}",
                    document_id=document.document_id,
                    title=document.title,
                    text="\n\n".join(current),
                    source_url=document.source_url,
                    metadata=document.metadata,
                    position=position,
                )
            )
    return chunks

