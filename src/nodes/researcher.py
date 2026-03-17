"""Researcher agent node — fetches RC docs, pulls relevant pages, compiles context."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

import httpx
from openai import AsyncOpenAI
import structlog

from src.config import get_docs_url
from src.state import AgentState
from src.tools.skills import load_skills

logger = structlog.get_logger()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "researcher.md"

# Module-level cache: (timestamp, content) with 10-min TTL
_llms_txt_cache: tuple[float, str] | None = None
_CACHE_TTL = 600  # 10 minutes


async def _fetch_llms_txt() -> str:
    """Fetch llms.txt with a 10-minute in-memory cache."""
    global _llms_txt_cache
    import time

    now = time.monotonic()
    if _llms_txt_cache and (now - _llms_txt_cache[0]) < _CACHE_TTL:
        logger.debug("llms_txt_cache_hit")
        return _llms_txt_cache[1]

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(get_docs_url())
        resp.raise_for_status()
        content = resp.text

    _llms_txt_cache = (now, content)
    logger.info("llms_txt_fetched", length=len(content))
    return content


def _extract_urls(llms_txt: str) -> list[str]:
    """Extract all doc page URLs from llms.txt.

    llms.txt uses relative paths like '/projects/overview' with a prefix.
    We convert them to full markdown URLs by appending .md.
    """
    base = "https://www.revenuecat.com/docs"
    # Match relative paths like /projects/overview, /api-v1/, /tools/mcp/setup
    paths = re.findall(r"- (/[a-zA-Z0-9_/\-]+)", llms_txt)
    urls = []
    for path in paths:
        # Strip trailing slash, append .md for markdown mirror
        clean = path.rstrip("/")
        urls.append(f"{base}{clean}.md")
    return urls


async def _pick_relevant_urls(task: str, urls: list[str]) -> list[str]:
    """Use Claude Haiku to pick the most relevant URLs for the task."""
    client = AsyncOpenAI()

    url_list = "\n".join(f"- {u}" for u in urls[:200])  # cap to avoid token overflow
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=512,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You select the most relevant RevenueCat doc pages for a task. "
                    "Return JSON: {\"urls\": [\"url1\", \"url2\", ...]}. "
                    "Pick 3-5 most relevant URLs. If none are relevant, return {\"urls\": []}."
                ),
            },
            {
                "role": "user",
                "content": f"Task: {task}\n\nAvailable pages:\n{url_list}",
            },
        ],
    )

    import json
    try:
        data = json.loads(response.choices[0].message.content)
        return data.get("urls", [])[:5]
    except (json.JSONDecodeError, KeyError):
        logger.warning("url_picker_parse_failed")
        return []


async def _fetch_page(url: str) -> tuple[str, str]:
    """Fetch a single doc page. Returns (url, content) or (url, '') on failure."""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            # Strip HTML tags for a rough text extraction
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s+", " ", text).strip()
            return url, text[:6000]  # cap per page
    except Exception as e:
        logger.warning("page_fetch_failed", url=url, error=str(e))
        return url, ""


async def research(state: AgentState) -> AgentState:
    """Fetch RC docs, identify relevant pages, pull them, synthesize context.

    For interactive tasks, uses a lightweight path (llms.txt only, no URL picking).
    """
    logger.info("researcher_start", task=state.task, task_type=state.task_type)

    # 1. Fetch llms.txt index
    try:
        llms_txt = await _fetch_llms_txt()
    except Exception as e:
        logger.error("llms_txt_fetch_failed", error=str(e))
        state.research_context = f"[Research failed: could not fetch llms.txt — {e}]"
        state.error = str(e)
        return state

    # Lightweight path for interactive tasks — just use llms.txt overview
    if state.task_type == "interactive":
        state.research_context = f"## llms.txt overview (first 4000 chars)\n\n{llms_txt[:4000]}"
        state.sources = [get_docs_url()]
        logger.info("researcher_done_lightweight", sources=1, context_len=len(state.research_context))
        return state

    # 2. Extract URLs and pick relevant ones
    all_urls = _extract_urls(llms_txt)
    logger.info("urls_extracted", count=len(all_urls))

    relevant_urls = await _pick_relevant_urls(state.task, all_urls)
    if not relevant_urls:
        # Fallback: pick core RC pages when the task is too broad for the picker
        base = "https://www.revenuecat.com/docs"
        fallback_paths = [
            "/welcome/overview.md",
            "/tools/mcp.md",
            "/tools/mcp/tools-reference.md",
            "/getting-started/quickstart.md",
            "/subscription-guidance/price-experimentation.md",
        ]
        relevant_urls = [f"{base}{p}" for p in fallback_paths]
        logger.info("urls_fallback_used", count=len(relevant_urls))
    logger.info("urls_selected", urls=relevant_urls)

    # 3. Fetch relevant pages concurrently
    pages: list[tuple[str, str]] = []
    if relevant_urls:
        results = await asyncio.gather(*[_fetch_page(u) for u in relevant_urls])
        pages = [(url, content) for url, content in results if content]

    state.sources = [url for url, _ in pages]
    state.sources.insert(0, get_docs_url())

    # 4. Build context: llms.txt overview + fetched pages
    context_parts = [f"## llms.txt overview (first 4000 chars)\n\n{llms_txt[:4000]}"]
    for url, content in pages:
        context_parts.append(f"## {url}\n\n{content}")

    docs_context = "\n\n---\n\n".join(context_parts)

    # 5. Synthesize with LLM (system prompt + accumulated skill knowledge)
    system_prompt = PROMPT_PATH.read_text()
    skill_context = load_skills("researcher")
    if skill_context:
        system_prompt += f"\n\n## Accumulated Knowledge\n\n{skill_context}"
    client = AsyncOpenAI()

    response = await client.chat.completions.create(
        model="o3",
        max_completion_tokens=8192,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Research the following task:\n\n"
                    f"**Task:** {state.task}\n"
                    f"**Type:** {state.task_type}\n\n"
                    f"RevenueCat documentation context:\n\n{docs_context}\n\n"
                    f"Compile comprehensive research context for the Writer agent."
                ),
            },
        ],
    )

    state.research_context = response.choices[0].message.content
    logger.info("researcher_done", sources=len(state.sources), context_len=len(state.research_context))
    return state
