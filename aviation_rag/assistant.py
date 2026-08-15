from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any

from aviation_rag.models import Answer, SearchResult
from aviation_rag.retrieval import HybridIndex

SYSTEM_PROMPT = """You are an aviation safety research assistant. Answer only from the supplied sources.
Every factual claim must cite one or more source labels such as [S1]. If the evidence is insufficient,
say so plainly. Do not provide operational flight advice, speculate about causes, or treat preliminary
information as a final finding. Prefer a concise synthesis over copying source text."""

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "did", "do", "does", "for",
    "from", "had", "has", "have", "how", "i", "in", "is", "it", "of", "on", "or", "that",
    "the", "their", "there", "this", "to", "was", "were", "what", "when", "where", "which",
    "who", "why", "with",
}


def _keywords(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9][a-z0-9'-]+", text.lower())
        if token not in STOPWORDS and len(token) > 2
    }


def _sources(results: list[SearchResult]) -> list[dict[str, Any]]:
    return [
        {
            "label": f"S{number}",
            "title": result.chunk.title,
            "document_id": result.chunk.document_id,
            "chunk_id": result.chunk.chunk_id,
            "source_url": result.chunk.source_url,
            "metadata": result.chunk.metadata,
            "score": round(result.score, 4),
            "excerpt": result.chunk.text[:500],
        }
        for number, result in enumerate(results, start=1)
    ]


def _extractive_answer(question: str, results: list[SearchResult]) -> str:
    query_keywords = _keywords(question)
    evidence_overlap = max(
        (len(query_keywords & _keywords(result.chunk.text)) for result in results), default=0
    )
    minimum_overlap = 2 if len(query_keywords) >= 2 else 1
    if not results or results[0].score < 0.12 or evidence_overlap < minimum_overlap:
        return "There is insufficient evidence in the indexed documents to answer that question."
    statements = []
    for number, result in enumerate(results[:3], start=1):
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", result.chunk.text)]
        ranked_sentences = sorted(
            sentences,
            key=lambda sentence: len(query_keywords & _keywords(sentence)),
            reverse=True,
        )
        sentence = ranked_sentences[0] if ranked_sentences else ""
        if sentence and len(query_keywords & _keywords(sentence)) >= minimum_overlap:
            statements.append(f"{sentence.rstrip('.')} [S{number}].")
    return " ".join(statements) or "There is insufficient evidence in the indexed documents to answer that question."


def _openai_answer(question: str, results: list[SearchResult]) -> str:
    context = "\n\n".join(
        f"[S{number}] {result.chunk.title}\n{result.chunk.text}"
        for number, result in enumerate(results, start=1)
    )
    body = json.dumps(
        {
            "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            "input": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Question: {question}\n\nSources:\n{context}"},
            ],
            "temperature": 0.1,
        }
    ).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.loads(response.read())
    if payload.get("output_text"):
        return payload["output_text"]
    texts = []
    for output in payload.get("output", []):
        for content in output.get("content", []):
            if content.get("type") == "output_text":
                texts.append(content.get("text", ""))
    return "\n".join(texts).strip()


class ResearchAssistant:
    def __init__(self, index: HybridIndex):
        self.index = index

    def ask(self, question: str, filters: dict[str, Any] | None = None, top_k: int = 5) -> Answer:
        started = time.perf_counter()
        results = self.index.search(question, top_k=top_k, filters=filters)
        retrieval_ms = (time.perf_counter() - started) * 1000
        generation_started = time.perf_counter()
        if os.getenv("OPENAI_API_KEY") and results:
            try:
                answer = _openai_answer(question, results)
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError):
                answer = _extractive_answer(question, results)
        else:
            answer = _extractive_answer(question, results)
        generation_ms = (time.perf_counter() - generation_started) * 1000
        sources = _sources(results)
        grounded = bool(sources) and any(source["label"] in answer for source in sources)
        return Answer(answer, sources, retrieval_ms, generation_ms, grounded)
