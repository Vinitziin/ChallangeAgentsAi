"""Unit tests for the Tavily search tool."""

from unittest.mock import patch, MagicMock
from app.tools.tavily_search import tavily_search


MOCK_SEARCH_RESULTS = [
    {"url": "https://example.com/1", "content": "Result about AI"},
    {"url": "https://example.com/2", "content": "More about AI"},
]


@patch("app.tools.tavily_search.TavilySearchResults")
def test_tavily_search_returns_results(mock_class):
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = MOCK_SEARCH_RESULTS
    mock_class.return_value = mock_instance

    results = tavily_search.invoke({"query": "artificial intelligence"})

    assert len(results) == 2
    assert results[0]["url"] == "https://example.com/1"


@patch("app.tools.tavily_search.TavilySearchResults")
def test_tavily_search_passes_query(mock_class):
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = []
    mock_class.return_value = mock_instance

    tavily_search.invoke({"query": "test query"})

    mock_instance.invoke.assert_called_once_with("test query")
