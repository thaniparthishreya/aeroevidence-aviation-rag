from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from aviation_rag.assistant import ResearchAssistant
from aviation_rag.retrieval import HybridIndex

app = FastAPI(title="Aviation Safety Research API", version="0.1.0")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    filters: dict[str, Any] = Field(default_factory=dict)
    top_k: int = Field(default=5, ge=1, le=12)


@lru_cache
def get_assistant() -> ResearchAssistant:
    path = Path(os.getenv("AVIATION_RAG_INDEX", "data/index/index.json"))
    if not path.exists():
        raise FileNotFoundError("Index missing. Run: python scripts/build_index.py")
    return ResearchAssistant(HybridIndex.load(path))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/stats")
def stats(assistant: Annotated[ResearchAssistant, Depends(get_assistant)]) -> dict[str, Any]:
    index = assistant.index
    return {
        "documents": index.document_count,
        "chunks": len(index.chunks),
        "source_agencies": index.facet_values("source_agency"),
        "record_statuses": index.facet_values("record_status"),
    }


@app.post("/ask")
def ask(
    request: AskRequest, assistant: Annotated[ResearchAssistant, Depends(get_assistant)]
) -> dict[str, Any]:
    result = assistant.ask(request.question, request.filters, request.top_k)
    return {
        "answer": result.answer,
        "sources": result.sources,
        "grounded": result.grounded,
        "latency": {
            "retrieval_ms": round(result.retrieval_ms, 2),
            "generation_ms": round(result.generation_ms, 2),
        },
    }
