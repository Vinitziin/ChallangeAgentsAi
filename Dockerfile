FROM python:3.11-slim

WORKDIR /workspace

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/workspace

EXPOSE 8501

CMD ["sh", "-c", "python -m vector_db.ingest || true && streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501"]
