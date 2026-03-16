"""Skill file loader and updater — the compounding knowledge system."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import structlog

logger = structlog.get_logger()

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"

# Which skill files each node should load
NODE_SKILLS: dict[str, list[str]] = {
    "researcher": [
        "revenuecat-knowledge.md",
        "job-description.md",
        "competitive-landscape.md",
    ],
    "writer": [
        "revenuecat-knowledge.md",
        "technical-writing.md",
        "job-description.md",
        "competitive-landscape.md",
    ],
    "feedback_writer": [
        "revenuecat-knowledge.md",
        "product-feedback.md",
        "job-description.md",
    ],
}


def load_skills(node_name: str) -> str:
    """Load all skill files relevant to a node, concatenated as context.

    Returns empty string if no skills found (graceful degradation).
    """
    filenames = NODE_SKILLS.get(node_name, [])
    if not filenames:
        return ""

    parts: list[str] = []
    for filename in filenames:
        path = SKILLS_DIR / filename
        if path.exists():
            content = path.read_text().strip()
            if content:
                parts.append(content)
        else:
            logger.debug("skill_file_missing", filename=filename)

    if not parts:
        return ""

    combined = "\n\n---\n\n".join(parts)
    logger.info("skills_loaded", node=node_name, files=filenames, total_chars=len(combined))
    return combined


def append_to_skill(filename: str, entry: str) -> None:
    """Append a learning entry to a skill file.

    Used by the reporter to compound knowledge after each run.
    """
    path = SKILLS_DIR / filename
    if not path.exists():
        logger.warning("skill_file_not_found", filename=filename)
        return

    content = path.read_text()
    # Append after the last line
    updated = content.rstrip() + "\n\n" + entry.strip() + "\n"
    path.write_text(updated)
    logger.info("skill_updated", filename=filename, entry_length=len(entry))


def log_failure(what_failed: str, root_cause: str, fix: str, rule: str) -> None:
    """Append a structured failure entry to the failure log."""
    entry = (
        f"### {date.today().isoformat()} — {what_failed}\n"
        f"**What happened:** {what_failed}\n"
        f"**Root cause:** {root_cause}\n"
        f"**Fix:** {fix}\n"
        f"**Rule:** {rule}"
    )
    append_to_skill("failure-log.md", entry)
