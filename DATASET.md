# Dataset and provenance

The bundled corpus is a curated portfolio dataset of eight **final NTSB aviation investigation
reports** covering weather encounters, loss of control, runway incursions, engine power loss,
controlled flight into terrain, and in-flight icing.

## Source

- Publisher: National Transportation Safety Board (NTSB)
- Catalog: `data/catalog/ntsb_reports.json`
- Normalized corpus: `data/official/ntsb_reports.json`
- Source format: official NTSB final-report PDFs
- Retrieved: 2026-08-14

Every normalized record stores its official report URL, NTSB number, report status, retrieval date,
and SHA-256 checksum of the downloaded PDF. The raw PDFs are intentionally excluded from Git to
keep the repository small; they can be reproduced with:

```bash
python scripts/fetch_ntsb_reports.py
```

The NTSB states that its aviation database covers civil aviation accidents and selected incidents
from 1962 onward. This project does **not** bundle that entire database and should not be used to
estimate population-level accident rates. It is a deliberately scoped RAG demonstration corpus.

## Included reports

| NTSB number | Topic | Event location |
|---|---|---|
| WPR09FA175 | Fog and loss of control | Sherwood, Oregon |
| OPS17IA008 | Runway incursion and airport geometry | San Francisco, California |
| OPS16IA008 | Runway incursion and communication | Dallas, Texas |
| WPR11LA380 | Total engine power loss | Lemoore, California |
| ERA16FA140 | Helicopter VFR encounter with IMC | Enterprise, Alabama |
| ANC12LA026 | Deteriorating weather and CFIT | Ketchikan, Alaska |
| WPR14FA286 | Continued VFR flight into IMC | Arizona |
| WPR26LA126 | In-flight icing | Arizona |

## Limitations

- The corpus is curated rather than statistically representative.
- PDF extraction can alter tables, spacing, and reading order.
- Metadata is maintained in the local catalog and should be checked against the linked report.
- Retrieval metrics describe eight versioned test questions, not all possible user questions.
- The structural citation check does not replace claim-level entailment evaluation.

