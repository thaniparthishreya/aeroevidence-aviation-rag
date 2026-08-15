from aviation_rag.ingestion import chunk_documents, normalize_text
from aviation_rag.models import Document


def test_normalize_text_removes_noise():
    assert normalize_text("Hello   world\n\n\n\nNext") == "Hello world\n\nNext"


def test_chunk_ids_are_stable_and_metadata_is_preserved():
    document = Document("report_1", "Report", "First paragraph.\n\nSecond paragraph.", metadata={"state": "AK"})
    chunks = chunk_documents([document], target_chars=20, overlap_units=0)
    assert [chunk.chunk_id for chunk in chunks] == ["report_1_c0000", "report_1_c0001"]
    assert chunks[0].metadata["state"] == "AK"

