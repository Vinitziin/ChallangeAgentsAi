"""Web search tool using Tavily API."""

from dataclasses import dataclass
from typing import Any

from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

from app.config import settings

import os

os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY


@dataclass
class SearchResult:
    """A single web search result."""

    title: str
    url: str
    content: str


@tool
def tavily_search(query: str) -> list[dict[str, Any]]:
    """Search the web for current information about any topic.

    Args:
        query: The search query string.

    Returns:
        A list of search results with title, url and content.
    """
    search = TavilySearchResults(max_results=5)
    raw_results = search.invoke(query)

    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            content=r.get("content", ""),
        ).__dict__
        for r in raw_results
    ]
