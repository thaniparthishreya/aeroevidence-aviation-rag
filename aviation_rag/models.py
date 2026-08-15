from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Document:
    document_id: str
    title: str
    text: str
    source_url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Chunk:
    chunk_id: str
    document_id: str
    title: str
    text: str
    source_url: str
    metadata: dict[str, Any]
    position: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SearchResult:
    chunk: Chunk
    score: float
    lexical_score: float
    semantic_score: float


@dataclass(slots=True)
class Answer:
    answer: str
    sources: list[dict[str, Any]]
    retrieval_ms: float
    generation_ms: float
    grounded: bool

