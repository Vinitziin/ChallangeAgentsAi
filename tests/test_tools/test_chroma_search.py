"""Unit tests for the ChromaDB search tool."""

from unittest.mock import patch, MagicMock
from app.tools.chroma_search import chroma_search


MOCK_QUERY_RESULTS = {
    "documents": [["Document about TechStore FAQ", "About returns policy"]],
    "metadatas": [[{"source": "faq.txt"}, {"source": "faq.txt"}]],
    "distances": [[0.25, 0.45]],
}


@patch("app.tools.chroma_search.OpenAIEmbeddings")
@patch("app.tools.chroma_search._get_chroma_collection")
def test_chroma_search_returns_documents(mock_collection_fn, mock_embeddings_class):
    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.1] * 1536
    mock_embeddings_class.return_value = mock_embeddings

    mock_collection = MagicMock()
    mock_collection.query.return_value = MOCK_QUERY_RESULTS
    mock_collection_fn.return_value = mock_collection

    results = chroma_search.invoke({"query": "TechStore"})

    assert len(results) == 2
    assert results[0]["content"] == "Document about TechStore FAQ"
    assert results[0]["metadata"]["source"] == "faq.txt"
    assert results[0]["distance"] == 0.25


@patch("app.tools.chroma_search.OpenAIEmbeddings")
@patch("app.tools.chroma_search._get_chroma_collection")
def test_chroma_search_empty_results(mock_collection_fn, mock_embeddings_class):
    mock_embeddings = MagicMock()
    mock_embeddings.embed_query.return_value = [0.1] * 1536
    mock_embeddings_class.return_value = mock_embeddings

    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }
    mock_collection_fn.return_value = mock_collection

    results = chroma_search.invoke({"query": "nonexistent"})

    assert results == []
