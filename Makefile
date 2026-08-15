.PHONY: install data index test lint evaluate api ui

install:
	python -m pip install -e ".[dev]"

data:
	python scripts/fetch_ntsb_reports.py

index:
	python scripts/build_index.py

test:
	python -m pytest

lint:
	ruff check aviation_rag scripts tests app.py

evaluate:
	python scripts/evaluate.py

api:
	uvicorn aviation_rag.api:app --reload

ui:
	streamlit run app.py
