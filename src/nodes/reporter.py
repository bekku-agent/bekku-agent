"""Reporter agent node — logs what happened and updates skill files."""

from __future__ import annotations

from datetime import datetime, timezone

import structlog

from src.state import AgentState
from src.tools.skills import append_to_skill, log_failure

logger = structlog.get_logger()


async def report(state: AgentState) -> AgentState:
    """Log the pipeline run and compound learnings into skill files."""
    logger.info("reporter_start")

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": state.task,
        "task_type": state.task_type,
        "published_url": state.published_url,
        "sources_count": len(state.sources),
        "draft_length": len(state.draft),
        "error": state.error or None,
    }

    state.activity_log.append(entry)

    # Compound learnings into skill files
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if state.error:
        # Log failures so they never repeat
        log_failure(
            what_failed=f"Pipeline error on task: {state.task[:60]}",
            root_cause=state.error,
            fix="[Pending investigation]",
            rule="[To be determined after fix]",
        )
    else:
        # Log successful patterns
        if state.task_type == "content" and state.sources:
            skill_entry = (
                f"- [{today}] Researched: \"{state.task[:80]}\" "
                f"— used {len(state.sources)} sources, "
                f"produced {len(state.draft)} char draft"
            )
            append_to_skill("revenuecat-knowledge.md", skill_entry)

        if state.task_type == "feedback":
            skill_entry = (
                f"- [{today}] Feedback produced: \"{state.task[:80]}\""
            )
            append_to_skill("product-feedback.md", skill_entry)

    logger.info("reporter_done", **entry)
    return state
