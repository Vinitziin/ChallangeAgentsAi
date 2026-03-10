FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential gcc && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY . .

ENV PYTHONPATH=/workspace

EXPOSE 8501

CMD ["sh", "-c", "python -m vector_db.ingest || true && streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501"]
