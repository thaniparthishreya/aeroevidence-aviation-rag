FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY aviation_rag aviation_rag
COPY scripts scripts
COPY data/official data/official
COPY data/catalog data/catalog
RUN pip install --no-cache-dir .
RUN python scripts/build_index.py
COPY app.py ./
EXPOSE 8000
CMD ["uvicorn", "aviation_rag.api:app", "--host", "0.0.0.0", "--port", "8000"]
