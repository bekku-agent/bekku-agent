"""Reporter agent node — logs activity and generates reports."""

from __future__ import annotations

from datetime import datetime

import structlog

from src.state import AgentState

logger = structlog.get_logger()


async def report(state: AgentState) -> AgentState:
    """Log activity and append to activity log."""
    logger.info("reporter_start")
    state.current_step = "report"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "topic": state.topic,
        "title": state.title,
        "gist_url": state.gist_url,
        "commit_sha": state.commit_sha,
        "error": state.error,
        "sources_count": len(state.sources),
    }

    state.activity_log.append(entry)
    logger.info("activity_logged", entry=entry)
    return state
