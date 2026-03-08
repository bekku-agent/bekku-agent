"""Publisher agent node — pushes content to GitHub."""

from __future__ import annotations

from datetime import date

import structlog

from src.state import AgentState
from src.tools.github_tools import commit_to_repo, create_gist

logger = structlog.get_logger()

REPO_NAME = "bekku-rc-advocate"


async def publish(state: AgentState) -> AgentState:
    """Publish content to GitHub Gist and repo."""
    logger.info("publisher_start", title=state.title)
    state.current_step = "publish"

    # Format the full article
    article = f"# {state.title}\n\n"
    if state.summary:
        article += f"*{state.summary}*\n\n"
    article += state.body
    if state.tags:
        article += f"\n\n---\n\nTags: {', '.join(state.tags)}"
    if state.sources:
        article += f"\n\n**Sources:** {', '.join(state.sources)}"

    # Publish as Gist
    try:
        gist_url = create_gist(
            title=state.title,
            content=article,
            description=f"Bekku: {state.title}",
        )
        state.gist_url = gist_url
        logger.info("gist_published", url=gist_url)
    except Exception as e:
        logger.error("gist_publish_failed", error=str(e))
        state.error = f"Gist publish failed: {e}"

    # Commit to publications repo
    try:
        slug = state.title.lower().replace(" ", "-").replace(":", "")[:50]
        file_path = f"publications/{date.today().isoformat()}-{slug}.md"
        sha = commit_to_repo(
            repo_name=REPO_NAME,
            file_path=file_path,
            content=article,
            commit_message=f"Publish: {state.title}",
        )
        state.commit_sha = sha
        logger.info("repo_committed", sha=sha)
    except Exception as e:
        logger.error("repo_commit_failed", error=str(e))
        if not state.error:
            state.error = f"Repo commit failed: {e}"

    return state
