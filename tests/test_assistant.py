from aviation_rag.assistant import ResearchAssistant
from aviation_rag.models import Chunk
from aviation_rag.retrieval import HybridIndex


def test_answer_has_citation_and_source():
    chunk = Chunk("c1", "d1", "Example", "Fuel restriction caused partial power loss.", "", {}, 0)
    answer = ResearchAssistant(HybridIndex([chunk])).ask("What caused the power loss?")
    assert "[S1]" in answer.answer
    assert answer.sources[0]["chunk_id"] == "c1"
    assert answer.grounded


def test_unsupported_question_abstains():
    chunk = Chunk("c1", "d1", "Example", "Fuel restriction caused partial power loss.", "", {}, 0)
    answer = ResearchAssistant(HybridIndex([chunk])).ask("What color was the pilot's jacket?")
    assert "insufficient evidence" in answer.answer

