from aviation_rag.models import Chunk
from aviation_rag.retrieval import HybridIndex


def make_chunk(identifier: str, text: str, **metadata):
    return Chunk(identifier, identifier, identifier, text, "", metadata, 0)


def test_retrieval_ranks_relevant_evidence_first():
    index = HybridIndex(
        [
            make_chunk("icing", "Airframe ice accumulation degraded aerodynamic performance."),
            make_chunk("runway", "The aircraft crossed the runway hold-short marking."),
        ]
    )
    assert index.search("How did ice affect aerodynamic performance?")[0].chunk.chunk_id == "icing"


def test_metadata_filter_is_case_insensitive():
    index = HybridIndex(
        [
            make_chunk("plane", "Weather deteriorated.", aircraft_category="Airplane"),
            make_chunk("heli", "Weather deteriorated.", aircraft_category="Helicopter"),
        ]
    )
    results = index.search("weather", filters={"aircraft_category": "helicopter"})
    assert [result.chunk.chunk_id for result in results] == ["heli"]


def test_unknown_filter_returns_no_results():
    index = HybridIndex([make_chunk("plane", "Engine power loss.", state="FL")])
    assert index.search("engine", filters={"state": "AK"}) == []


def test_date_range_filter():
    index = HybridIndex(
        [
            make_chunk("old", "Weather event.", event_date="2010-01-01"),
            make_chunk("new", "Weather event.", event_date="2020-01-01"),
        ]
    )
    results = index.search("weather", filters={"event_date": {"$gte": "2015-01-01"}})
    assert [result.chunk.chunk_id for result in results] == ["new"]


def test_index_vectors_are_stable_between_instances():
    chunks = [make_chunk("one", "runway surface movement alert")]
    assert HybridIndex(chunks).vectors == HybridIndex(chunks).vectors
