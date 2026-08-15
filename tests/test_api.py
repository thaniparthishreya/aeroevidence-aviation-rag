from fastapi.testclient import TestClient

from aviation_rag.api import app, get_assistant
from aviation_rag.assistant import ResearchAssistant
from aviation_rag.models import Chunk
from aviation_rag.retrieval import HybridIndex


def test_health_endpoint():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_endpoint_returns_citations():
    chunk = Chunk(
        "engine_c1",
        "engine_report",
        "Engine report",
        "A fractured cylinder caused a total loss of engine power during cruise.",
        "https://example.test/report",
        {"record_status": "Final", "source_agency": "NTSB"},
        0,
    )
    app.dependency_overrides[get_assistant] = lambda: ResearchAssistant(HybridIndex([chunk]))
    try:
        response = TestClient(app).post(
            "/ask", json={"question": "What caused the loss of engine power?", "top_k": 3}
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is True
    assert payload["sources"][0]["label"] == "S1"

