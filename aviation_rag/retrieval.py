from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from itertools import pairwise
from pathlib import Path
from typing import Any

from aviation_rag.models import Chunk, SearchResult

TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9'-]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def _matches(value: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        actual = str(value or "")
        if "$gte" in expected and actual < str(expected["$gte"]):
            return False
        if "$lte" in expected and actual > str(expected["$lte"]):
            return False
        return "$in" not in expected or any(_matches(value, item) for item in expected["$in"])
    if isinstance(expected, list):
        return any(_matches(value, item) for item in expected)
    if isinstance(value, list):
        return any(_matches(item, expected) for item in value)
    return str(value).lower() == str(expected).lower()


class HybridIndex:
    """Portable BM25 + hashed semantic index with metadata filtering."""

    def __init__(self, chunks: list[Chunk], vector_dimensions: int = 384):
        self.chunks = chunks
        self.vector_dimensions = vector_dimensions
        self.term_frequencies = [Counter(tokenize(chunk.text)) for chunk in chunks]
        self.lengths = [sum(frequencies.values()) for frequencies in self.term_frequencies]
        self.average_length = sum(self.lengths) / max(len(self.lengths), 1)
        document_frequency: Counter[str] = Counter()
        for frequencies in self.term_frequencies:
            document_frequency.update(frequencies.keys())
        self.idf = {
            term: math.log(1 + (len(chunks) - count + 0.5) / (count + 0.5))
            for term, count in document_frequency.items()
        }
        self.vectors = [self._vectorize(chunk.text) for chunk in chunks]

    def _vectorize(self, text: str) -> dict[int, float]:
        vector: defaultdict[int, float] = defaultdict(float)
        tokens = tokenize(text)
        features = tokens + [f"{a}_{b}" for a, b in pairwise(tokens)]
        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest, "big") % self.vector_dimensions
            vector[bucket] += 1.0
        norm = math.sqrt(sum(value * value for value in vector.values())) or 1.0
        return {key: value / norm for key, value in vector.items()}

    def _bm25(self, query_tokens: list[str], index: int) -> float:
        frequencies = self.term_frequencies[index]
        length = self.lengths[index]
        score = 0.0
        k1, b = 1.5, 0.75
        for term in query_tokens:
            frequency = frequencies.get(term, 0)
            denominator = frequency + k1 * (1 - b + b * length / max(self.average_length, 1))
            if denominator:
                score += self.idf.get(term, 0.0) * frequency * (k1 + 1) / denominator
        return score

    @staticmethod
    def _cosine(left: dict[int, float], right: dict[int, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(key, 0.0) for key, value in left.items())

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
        lexical_weight: float = 0.65,
    ) -> list[SearchResult]:
        filters = {key: value for key, value in (filters or {}).items() if value not in (None, "", [])}
        query_tokens = tokenize(query)
        query_vector = self._vectorize(query)
        candidates: list[tuple[int, float, float]] = []
        for index, chunk in enumerate(self.chunks):
            if not all(_matches(chunk.metadata.get(key), value) for key, value in filters.items()):
                continue
            candidates.append((index, self._bm25(query_tokens, index), self._cosine(query_vector, self.vectors[index])))
        max_bm25 = max((item[1] for item in candidates), default=1.0) or 1.0
        ranked = []
        for index, bm25, semantic in candidates:
            normalized_bm25 = bm25 / max_bm25
            score = lexical_weight * normalized_bm25 + (1 - lexical_weight) * semantic
            ranked.append(SearchResult(self.chunks[index], score, normalized_bm25, semantic))
        return sorted(ranked, key=lambda result: result.score, reverse=True)[:top_k]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"version": 1, "chunks": [chunk.to_dict() for chunk in self.chunks]}, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> HybridIndex:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls([Chunk(**record) for record in payload["chunks"]])

    def facet_values(self, field: str) -> list[str]:
        values: set[str] = set()
        for chunk in self.chunks:
            value = chunk.metadata.get(field)
            if isinstance(value, list):
                values.update(str(item) for item in value)
            elif value not in (None, ""):
                values.add(str(value))
        return sorted(values)

    @property
    def document_count(self) -> int:
        return len({chunk.document_id for chunk in self.chunks})
