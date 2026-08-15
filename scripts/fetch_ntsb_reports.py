"""Download and normalize the curated, authoritative NTSB report corpus."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aviation_rag.ingestion import normalize_text

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/ntsb_reports.json"
DOWNLOAD_DIR = ROOT / "data/raw/ntsb"
OUTPUT = ROOT / "data/official/ntsb_reports.json"


def download(url: str, destination: Path) -> bytes:
    request = Request(url, headers={"User-Agent": "aviation-safety-rag/0.1 (research project)"})
    with urlopen(request, timeout=60) as response:
        content = response.read()
    if not content.startswith(b"%PDF"):
        raise ValueError(f"Expected PDF from {url}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return content


def extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise SystemExit("Install project dependencies first: pip install -e '.[dev]'") from exc
    reader = PdfReader(str(path))
    return normalize_text("\n\n".join(page.extract_text() or "" for page in reader.pages))


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    documents = []
    for record in catalog:
        pdf_path = DOWNLOAD_DIR / f"{record['metadata']['ntsb_number']}.pdf"
        content = download(record["source_url"], pdf_path)
        text = extract_pdf(pdf_path)
        if len(text) < 500:
            raise ValueError(f"Insufficient extracted text for {pdf_path.name}")
        metadata = dict(record["metadata"])
        metadata.update(
            {
                "retrieved_at": datetime.now(UTC).date().isoformat(),
                "source_sha256": hashlib.sha256(content).hexdigest(),
                "source_file": pdf_path.name,
                "corpus_scope": "Curated NTSB final reports for portfolio demonstration",
            }
        )
        documents.append(
            {
                "document_id": record["document_id"],
                "title": record["title"],
                "source_url": record["source_url"],
                "metadata": metadata,
                "text": text,
            }
        )
        print(f"Fetched {metadata['ntsb_number']}: {len(text):,} characters")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(documents, indent=2), encoding="utf-8")
    print(f"Wrote {len(documents)} authoritative records to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
