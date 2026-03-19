"""
Web Search Tool — supports mock mode and SerpAPI.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import httpx
from loguru import logger

from core.config import get_settings
from models import SearchResult


# ─────────────── Mock search for development ───────────────

_MOCK_RESULTS: dict[str, list[dict]] = {
    "default": [
        {
            "title": "Wikipedia — General Knowledge",
            "url": "https://en.wikipedia.org/wiki/Knowledge",
            "snippet": "Knowledge is a form of awareness or familiarity gained by experience or education.",
        },
        {
            "title": "Recent Advances in AI Research",
            "url": "https://arxiv.org/ai-research",
            "snippet": "Transformer architectures continue to dominate NLP and computer vision tasks with state-of-the-art results.",
        },
        {
            "title": "Best Practices for Software Engineering",
            "url": "https://martinfowler.com/articles/practices.html",
            "snippet": "Clean architecture, testing, and continuous integration remain foundational practices for production systems.",
        },
    ],
}


async def _mock_search(query: str, num_results: int = 5) -> list[SearchResult]:
    await asyncio.sleep(0.2)  # simulate latency
    results = _MOCK_RESULTS.get("default", [])[:num_results]
    return [SearchResult(**r) for r in results]


# ─────────────── SerpAPI search ───────────────

async def _serpapi_search(query: str, num_results: int = 5) -> list[SearchResult]:
    settings = get_settings()
    params = {
        "q": query,
        "api_key": settings.serpapi_key,
        "engine": "google",
        "num": num_results,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get("https://serpapi.com/search", params=params)
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("organic_results", [])[:num_results]:
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
            )
        )
    return results


# ─────────────── Public interface ───────────────

async def web_search(query: str, num_results: int = 5) -> list[SearchResult]:
    """Route to mock or real search based on config."""
    settings = get_settings()
    mode = settings.search_mode.lower()
    logger.info("Web search [mode={}]: '{}'", mode, query)

    try:
        if mode == "serpapi" and settings.serpapi_key:
            return await _serpapi_search(query, num_results)
        return await _mock_search(query, num_results)
    except Exception as e:
        logger.error("Web search failed: {}", e)
        return []
