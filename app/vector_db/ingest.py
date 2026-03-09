"""Ingest documents into ChromaDB for similarity search.

Usage:
    python -m app.vector_db.ingest

This script reads all .txt files from data/sample_docs/ and stores them
as embeddings in the ChromaDB knowledge_base collection.
"""

import os
import glob
import logging

import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.tools.chroma_search import COLLECTION_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_docs")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def ingest():
    """Load documents, split into chunks, embed, and store in ChromaDB."""
    docs_path = os.path.abspath(DOCS_DIR)
    files = glob.glob(os.path.join(docs_path, "*.txt"))

    if not files:
        logger.warning("No .txt files found in %s", docs_path)
        return

    logger.info("Found %d files to ingest", len(files))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    all_chunks = []
    all_metadatas = []
    all_ids = []
    chunk_counter = 0

    for filepath in files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = splitter.split_text(content)
        logger.info("  %s → %d chunks", filename, len(chunks))

        for chunk in chunks:
            all_chunks.append(chunk)
            all_metadatas.append({"source": filename})
            all_ids.append(f"doc_{chunk_counter}")
            chunk_counter += 1

    logger.info("Total chunks to embed: %d", len(all_chunks))

    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    vectors = embeddings.embed_documents(all_chunks)

    client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)

    try:
        client.delete_collection(name=COLLECTION_NAME)
        logger.info("Deleted existing collection '%s'", COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)

    collection.add(
        ids=all_ids,
        documents=all_chunks,
        embeddings=vectors,
        metadatas=all_metadatas,
    )

    logger.info("Ingestion complete: %d chunks stored in '%s'", len(all_chunks), COLLECTION_NAME)


if __name__ == "__main__":
    ingest()
