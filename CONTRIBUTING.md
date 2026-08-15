# Contributing

1. Create a virtual environment and install `.[dev]`.
2. Rebuild the index with `python scripts/build_index.py`.
3. Run `ruff check aviation_rag scripts tests app.py`, `pytest -q`, and
   `python scripts/evaluate.py` before opening a pull request.
4. Add retrieval changes to the evaluation set and preserve every document's provenance.

Do not add records without an authoritative source URL and visible publication status. Never mix
preliminary and final reports without making that distinction available as metadata and in the UI.

