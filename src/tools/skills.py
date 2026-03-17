"""Skill file loader and updater — the compounding knowledge system."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import structlog

logger = structlog.get_logger()

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"

# Which skill files each node should load
NODE_SKILLS: dict[str, list[str]] = {
    "planner": [
        "larry-playbook.md",
        "content-performance.md",
        "failure-log.md",
        "revenuecat-knowledge.md",
        "job-description.md",
        "competitive-landscape.md",
    ],
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
    "analyzer": [
        "content-performance.md",
        "failure-log.md",
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


def log_engagement(
    published_url: str,
    linkedin_url: str,
    impressions: int,
    likes: int,
    comments: int,
    shares: int,
) -> None:
    """Update an existing content-performance entry with LinkedIn engagement data.

    Finds the entry by published_url and appends engagement metrics.
    """
    path = SKILLS_DIR / "content-performance.md"
    if not path.exists():
        logger.warning("content_performance_not_found")
        return

    content = path.read_text()

    # Find the entry block that contains this published URL
    if published_url not in content:
        logger.warning("entry_not_found_for_url", url=published_url)
        # Append as a standalone engagement log
        entry = (
            f"\n### {date.today().isoformat()} — Engagement Update\n"
            f"- **Published URL:** {published_url}\n"
            f"- **LinkedIn URL:** {linkedin_url}\n"
            f"- **LinkedIn Engagement:** {impressions} impressions / {likes} likes / {comments} comments / {shares} shares\n"
        )
        append_to_skill("content-performance.md", entry)
        return

    # Replace "pending" engagement line or append after published URL line
    engagement_line = f"- **LinkedIn Engagement:** {impressions} impressions / {likes} likes / {comments} comments / {shares} shares"
    linkedin_url_line = f"- **LinkedIn URL:** {linkedin_url}"

    # Try to update existing engagement line
    if "- **LinkedIn Engagement:** pending" in content:
        content = content.replace(
            "- **LinkedIn Engagement:** pending",
            engagement_line,
            1,  # only replace first match near this URL — good enough for now
        )
    elif "- **LinkedIn URL:** N/A" in content:
        content = content.replace(
            "- **LinkedIn URL:** N/A",
            f"{linkedin_url_line}\n{engagement_line}",
            1,
        )
    else:
        # Append after the published URL line
        content = content.replace(
            f"- **Published URL:** {published_url}",
            f"- **Published URL:** {published_url}\n{linkedin_url_line}\n{engagement_line}",
            1,
        )

    path.write_text(content)
    logger.info("engagement_logged", url=published_url, impressions=impressions, likes=likes)


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
