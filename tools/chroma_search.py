"""ChromaDB similarity search tool."""

from typing import Any

import chromadb
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

from app.config import settings

COLLECTION_NAME = "knowledge_base"


def _get_chroma_collection() -> chromadb.Collection:
    """Connect to ChromaDB and return the knowledge base collection."""
    client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    return client.get_or_create_collection(name=COLLECTION_NAME)


@tool
def chroma_search(query: str) -> list[dict[str, Any]]:
    """Search the internal knowledge base for relevant documents.

    Use this tool when the user asks about internal documentation,
    company FAQs, or any topic that might be in the knowledge base.

    Args:
        query: The search query in natural language.

    Returns:
        A list of relevant documents with content and metadata.
    """
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    query_embedding = embeddings.embed_query(query)

    collection = _get_chroma_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
    )

    documents = []
    for i, doc in enumerate(results["documents"][0]):
        entry = {
            "content": doc,
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else None,
        }
        documents.append(entry)

    return documents
