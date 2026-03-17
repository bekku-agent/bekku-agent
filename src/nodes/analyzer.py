"""Analyzer agent node — closes the learning loop by logging outcomes and extracting rules."""

from __future__ import annotations

from datetime import datetime, timezone

import structlog

from src.state import AgentState
from src.tools.skills import append_to_skill, log_failure

logger = structlog.get_logger()


def _classify_topic(task: str) -> str:
    """Simple keyword-based topic classification."""
    task_lower = task.lower()
    categories = {
        "tutorial": ["tutorial", "guide", "how to", "integrate", "setup", "migration"],
        "case-study": ["case study", "pattern", "real-world", "example"],
        "feedback": ["feedback", "improve", "suggestion", "critique"],
        "opinion": ["opinion", "future", "predict", "change", "rise of"],
        "application": ["application", "letter", "advocate", "apply"],
    }
    for category, keywords in categories.items():
        if any(kw in task_lower for kw in keywords):
            return category
    return "guide"


def _determine_approval_status(state: AgentState) -> str:
    """Determine what happened during approval."""
    if state.error and "rejected" in state.error.lower():
        return "rejected"
    if state.published_url:
        return "approved"
    return "no-publish"


async def analyze(state: AgentState) -> AgentState:
    """Log structured outcome and extract learning rules from this run."""
    logger.info("analyzer_start")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    category = _classify_topic(state.task)
    approval = _determine_approval_status(state)

    # Build activity log entry
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": state.task,
        "task_type": state.task_type,
        "category": category,
        "published_url": state.published_url,
        "sources_count": len(state.sources),
        "draft_length": len(state.draft),
        "approval": approval,
        "error": state.error or None,
    }
    state.activity_log.append(entry)

    # --- Log to content-performance.md ---
    if state.task_type in ("content", "feedback"):
        perf_entry = (
            f"### {today} — {state.task[:80]}\n"
            f"- **Category:** {category}\n"
            f"- **Format:** gist\n"
            f"- **Sources:** {len(state.sources)} sources used\n"
            f"- **Draft length:** {len(state.draft)} chars\n"
            f"- **Approval:** {approval}\n"
            f"- **Published URL:** {state.published_url or 'N/A'}\n"
            f"- **LinkedIn URL:** N/A\n"
            f"- **LinkedIn Engagement:** pending\n"
            f"- **Rule learned:** [pending review]"
        )
        append_to_skill("content-performance.md", perf_entry)

    # --- Log failures with actionable rules ---
    if state.error:
        if "rejected" in state.error.lower():
            log_failure(
                what_failed=f"Draft rejected: {state.task[:60]}",
                root_cause="Operator rejected the draft",
                fix="Review operator feedback and adjust approach",
                rule=f"Topic '{category}' draft was rejected — check quality bar for this category",
            )
        else:
            log_failure(
                what_failed=f"Pipeline error on: {state.task[:60]}",
                root_cause=state.error,
                fix="[Pending investigation]",
                rule="[To be determined after fix]",
            )

    # --- Update knowledge skill on success ---
    if not state.error and state.task_type == "content" and state.sources:
        knowledge_entry = (
            f"- [{today}] Researched: \"{state.task[:80]}\" "
            f"— used {len(state.sources)} sources, "
            f"produced {len(state.draft)} char draft"
        )
        append_to_skill("revenuecat-knowledge.md", knowledge_entry)

    if not state.error and state.task_type == "feedback":
        feedback_entry = f"- [{today}] Feedback produced: \"{state.task[:80]}\""
        append_to_skill("product-feedback.md", feedback_entry)

    logger.info("analyzer_done", **entry)
    return state
