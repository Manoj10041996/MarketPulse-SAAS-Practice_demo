import os
from functools import lru_cache

from langchain_tavily import TavilySearch

from app.config import get_settings


@lru_cache(maxsize=1)
def get_web_search_tool() -> TavilySearch:
    """Supplementary general web search (Tavily) — for market/brand context
    Amazon product data alone doesn't cover. Not a substitute for the Amazon
    tools; the agent's system prompt frames it as secondary.
    """
    settings = get_settings()
    # TavilySearch reads TAVILY_API_KEY from the environment; pydantic-settings
    # loads it into Settings but doesn't export it back to os.environ, so set
    # it explicitly (setdefault: never overwrites a value already present).
    os.environ.setdefault("TAVILY_API_KEY", settings.tavily_api_key)
    return TavilySearch(max_results=5)
