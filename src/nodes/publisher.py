"""Publisher agent node — pushes draft to GitHub Gist via PyGithub."""

from __future__ import annotations

import structlog

from src.state import AgentState
from src.tools.github_tools import create_gist

logger = structlog.get_logger()


async def publish(state: AgentState) -> AgentState:
    """Publish the draft to a GitHub Gist. Returns the Gist URL."""
    logger.info("publisher_start", task=state.task[:80])

    # Build a filename from the task
    slug = state.task.lower().replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")[:50]
    filename = f"{slug}.md"

    try:
        gist_url = create_gist(
            title=filename,
            content=state.draft,
            description=f"Bekku: {state.task[:100]}",
        )
        state.published_url = gist_url
        logger.info("publisher_done", url=gist_url)
    except Exception as e:
        logger.error("publish_failed", error=str(e))
        state.error = f"Publish failed: {e}"

    return state
