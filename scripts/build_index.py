import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aviation_rag.ingestion import chunk_documents, load_directory
from aviation_rag.retrieval import HybridIndex


def main() -> None:
    official = Path("data/official")
    user_documents = Path("data/user")
    documents = load_directory(official) + load_directory(user_documents)
    if not documents:
        raise SystemExit("No documents found. Run scripts/fetch_ntsb_reports.py first.")
    chunks = chunk_documents(documents)
    index = HybridIndex(chunks)
    output = Path("data/index/index.json")
    index.save(output)
    agencies = sorted({str(document.metadata.get("source_agency", "User")) for document in documents})
    print(
        f"Indexed {len(documents)} documents into {len(chunks)} chunks at {output} "
        f"(sources: {', '.join(agencies)})"
    )


if __name__ == "__main__":
    main()
