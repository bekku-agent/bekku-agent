"""Web fetching and document ingestion tools."""

from __future__ import annotations

import httpx
import structlog

logger = structlog.get_logger()


async def fetch_url(url: str, timeout: float = 30.0) -> str:
    """Fetch content from a URL."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


async def fetch_rc_docs() -> str:
    """Fetch RevenueCat's LLM-optimized documentation index."""
    url = "https://www.revenuecat.com/docs/llms.txt"
    logger.info("fetching_rc_docs", url=url)
    return await fetch_url(url)


async def fetch_rc_api_docs(version: str = "v2") -> str:
    """Fetch RevenueCat API documentation."""
    url = f"https://www.revenuecat.com/docs/api-{version}"
    logger.info("fetching_rc_api_docs", url=url, version=version)
    return await fetch_url(url)
