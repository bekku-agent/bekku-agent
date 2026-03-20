"""Publisher agent node — pushes draft to GitHub Gist via PyGithub."""

from __future__ import annotations

import re

import structlog

from src.state import AgentState
from src.tools.buffer_tools import distribute_social
from src.tools.github_tools import create_gist

logger = structlog.get_logger()


def _extract_title_and_body(draft: str) -> tuple[str, str]:
    """Extract the article title from structured writer output and return clean body.

    The writer outputs structured fields like:
        title: Some Title
        summary: ...
        tags: [...]
        body:
        # Actual content...

    Returns (title, clean_body) — strips metadata, keeps just the article.
    """
    title = ""
    body = draft

    # Try to extract title from "title: ..." line
    title_match = re.match(r"^title:\s*(.+)", draft, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip().strip('"').strip("'")

    # Try to find where the body starts (after "body:" line or first heading)
    body_match = re.search(r"^body:\s*\n", draft, re.MULTILINE)
    if body_match:
        body = draft[body_match.end():].strip()
    elif title_match:
        # Strip metadata lines (title/summary/tags) from the top
        lines = draft.split("\n")
        content_start = 0
        for i, line in enumerate(lines):
            if line.startswith(("title:", "summary:", "tags:", "body:")):
                content_start = i + 1
            elif line.strip() and not line.startswith(("title:", "summary:", "tags:")):
                break
        body = "\n".join(lines[content_start:]).strip()

    # Prepend the title as an H1 if we extracted one and the body doesn't start with it
    if title and not body.startswith(f"# {title}"):
        body = f"# {title}\n\n{body}"

    return title, body


def _slugify(text: str) -> str:
    """Create a clean URL slug from text."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug[:60]


async def publish(state: AgentState) -> AgentState:
    """Publish the draft to a GitHub Gist. Returns the Gist URL."""
    logger.info("publisher_start", task=state.task[:80])

    title, clean_body = _extract_title_and_body(state.draft)

    # Use the extracted title for the filename, fall back to task
    slug = _slugify(title) if title else _slugify(state.task)

    try:
        gist_url = create_gist(
            title=slug,
            content=clean_body,
            description=f"Bekku: {title or state.task[:100]}",
        )
        state.published_url = gist_url
        logger.info("publisher_gist_done", url=gist_url)

        # Distribute social posts via Buffer (non-fatal if it fails)
        if state.social_posts and gist_url:
            try:
                post_ids = await distribute_social(state.social_posts, gist_url, full_article=clean_body)
                if post_ids:
                    logger.info("publisher_buffer_done", posts=len(post_ids))
            except Exception as e:
                logger.warning("publisher_buffer_failed", error=str(e))

    except Exception as e:
        logger.error("publish_failed", error=str(e))
        state.error = f"Publish failed: {e}"

    return state
