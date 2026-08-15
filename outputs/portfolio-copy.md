# AeroEvidence portfolio copy

GitHub: https://github.com/thaniparthishreya/aeroevidence-aviation-rag

## Résumé — concise version

**AeroEvidence — Aviation Safety RAG Assistant** | Python, FastAPI, Streamlit, RAG, NLP, Docker

- Built a citation-first RAG application over official NTSB aviation reports, combining BM25 and
  semantic retrieval with metadata filtering, evidence-linked responses, and hallucination abstention.
- Developed reproducible PDF ingestion, paragraph-aware chunking, provenance tracking, FastAPI and
  Streamlit interfaces, and automated CI tests; achieved 1.00 Recall@5 and 1.00 MRR on a versioned
  eight-question retrieval benchmark across 235 indexed passages.

## Résumé — one bullet

- Engineered AeroEvidence, a production-oriented aviation-safety RAG assistant using Python,
  FastAPI, Streamlit, hybrid retrieval, structured filters, and source-grounded generation; implemented
  provenance, hallucination tests, latency measurement, Docker, and CI, achieving 1.00 Recall@5/MRR
  on a curated NTSB benchmark.

## LinkedIn project description

I built **AeroEvidence**, an independent AI-powered research assistant for exploring official National
Transportation Safety Board aviation investigation reports.

The project goes beyond a generic PDF chatbot. It implements an end-to-end RAG pipeline: document
ingestion, cleaning, paragraph-aware chunking, hybrid lexical and semantic retrieval, metadata
filtering, grounded answer generation, citations, latency measurement, and retrieval evaluation.

Users can ask questions about weather encounters, runway incursions, engine failures, loss of control,
and contributing factors, then inspect the exact evidence passages and open the corresponding official
NTSB report. When the corpus does not support a question, the assistant abstains instead of fabricating
an answer.

**Technical highlights:**

- Python, FastAPI, Streamlit, Docker
- Hybrid BM25 + semantic retrieval
- Filters for aircraft category, weather, event date, and report status
- Citation-backed responses with source provenance
- Optional OpenAI synthesis with an offline extractive fallback
- Automated evaluation, hallucination tests, and GitHub Actions CI
- 8 official reports, 235 indexed evidence passages
- 1.00 Recall@5 and 1.00 MRR on the versioned demonstration benchmark

This is an independent portfolio project built from public NTSB documents. It is not affiliated with
the NTSB, FAA, or any employer and does not provide operational aviation advice.

## LinkedIn launch post

I’m excited to share **AeroEvidence**, a citation-first aviation safety research assistant I built using
Retrieval-Augmented Generation.

Rather than creating another generic “chat with a PDF” demo, I focused on the engineering required for
trustworthy research: hybrid retrieval, structured metadata filters, report-level provenance, evidence
citations, explicit abstention, latency tracking, and automated evaluation.

The application researches a curated collection of official NTSB final reports covering weather,
runway incursions, engine power loss, controlled flight into terrain, and in-flight icing. Every answer
includes an inspectable evidence trail and a link to the original report.

Stack: Python · FastAPI · Streamlit · RAG · BM25 · semantic search · Docker · GitHub Actions

Current benchmark: 1.00 Recall@5 and 1.00 MRR across eight versioned research questions and 235
indexed passages. These are scoped demo-corpus results, not a claim of universal accuracy.

The project is independent and uses public NTSB documents; it is not affiliated with the NTSB, FAA,
or any employer.

#ArtificialIntelligence #RAG #Python #NLP #FastAPI #Streamlit #MachineLearning #AviationSafety
