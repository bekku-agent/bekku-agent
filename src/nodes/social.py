"""Social post generator node — sets the article as the LinkedIn post directly."""

from __future__ import annotations

import structlog

from src.state import AgentState

logger = structlog.get_logger()


async def generate_social(state: AgentState) -> AgentState:
    """Set social posts from the article draft.

    LinkedIn: the article IS the post (already under 3000 chars from writer).
    X: disabled for now.
    """
    if state.task_type == "interactive":
        return state

    if not state.draft or state.draft.startswith("["):
        return state

    logger.info("social_start", draft_len=len(state.draft))

    # The article itself is the LinkedIn post — no summarization needed
    state.social_posts = {
        "linkedin": state.draft,
    }

    # Warn if over LinkedIn limit
    if len(state.draft) > 3000:
        logger.warning("social_linkedin_over_limit", chars=len(state.draft))

    logger.info("social_done", linkedin_chars=len(state.draft))
    return state
