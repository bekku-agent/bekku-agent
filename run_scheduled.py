"""Bekku — Headless content runner for GitHub Actions deployment.

Runs the pipeline up to the draft stage (planner → researcher → writer),
then creates a GitHub Issue with the draft + social posts for MK to review.

Usage:
    python run_scheduled.py                    # Run one auto-picked task
    python run_scheduled.py --task "..."       # Run a specific task
    python run_scheduled.py --batch 3          # Run 3 auto-picked tasks
"""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from github import Github

load_dotenv()

SCHEDULE_PATH = Path(__file__).parent / "schedule.yaml"


def load_schedule() -> dict:
    if SCHEDULE_PATH.exists():
        return yaml.safe_load(SCHEDULE_PATH.read_text()) or {}
    return {}


def get_topic_queue(schedule: dict) -> list[str]:
    return schedule.get("topic_queue", [])


async def generate_draft(task: str) -> dict:
    """Run planner → router → researcher → writer (no approval/publish)."""
    from openai import AsyncOpenAI

    from src.nodes.planner import plan
    from src.nodes.researcher import research
    from src.nodes.router import route
    from src.nodes.social import generate_social
    from src.nodes.writer import write
    from src.state import AgentState

    state = AgentState(task=task)

    # Run the pipeline nodes directly — no graph interrupt needed
    state = await route(state)
    if state.task_type != "interactive":
        state = await plan(state)
    state = await research(state)
    state = await write(state)
    state = await generate_social(state)

    return {
        "task": state.task,
        "task_type": state.task_type,
        "draft": state.draft,
        "social_posts": state.social_posts,
        "sources": state.sources,
        "plan": state.plan,
        "error": state.error,
    }


def create_review_issue(result: dict) -> str:
    """Create a GitHub Issue with the draft for MK to review."""
    token = os.environ.get("GH_TOKEN") or os.environ["GITHUB_TOKEN"]
    repo_name = os.environ.get("GITHUB_REPO", "bekku-agent/bekku-agent")

    gh = Github(token)
    repo = gh.get_repo(repo_name)

    task = result["task"]
    draft = result["draft"]
    social = result["social_posts"]
    sources = result["sources"]

    # Clean the draft — strip metadata (title/summary/tags/body:) for display
    from src.nodes.publisher import _extract_title_and_body
    title, clean_body = _extract_title_and_body(draft)

    # Build issue body — use unique markers so we can extract the draft later
    body_parts = [
        "## Draft for Review\n",
        f"**Task:** {task}\n",
        f"**Type:** {result['task_type']}\n",
        f"**Sources:** {len(sources)}\n",
        "<!-- DRAFT_START -->\n",
        clean_body,
        "\n<!-- DRAFT_END -->\n",
    ]

    if social:
        body_parts.append("## Social Posts\n")
        if social.get("x"):
            body_parts.append(f"### X (Twitter)\n```\n{social['x']}\n```\n")
        if social.get("linkedin"):
            body_parts.append(f"### LinkedIn\n```\n{social['linkedin']}\n```\n")

    body_parts.append(
        "\n---\n"
        "**Actions:** Comment on this issue to proceed:\n"
        "- `approve` — publish as-is to GitHub Gist\n"
        "- `reject` — skip publishing, log rejection\n"
        "- Paste edited markdown — publish the edited version\n"
    )

    body = "\n".join(body_parts)

    # Create issue — use article title if available, fall back to task
    issue_title = f"[Bekku Draft] {title or task[:80]}"
    issue = repo.create_issue(
        title=issue_title,
        body=body,
        labels=["bekku-draft", "awaiting-review"],
    )

    print(f"  → Issue created: {issue.html_url}")
    return issue.html_url


async def run_one(task: str) -> None:
    """Generate a draft and create a review issue."""
    print(f"Generating draft for: {task[:80]}")
    result = await generate_draft(task)

    if result["error"]:
        print(f"  → Error: {result['error']}")
        return

    create_review_issue(result)


async def run_batch(count: int) -> None:
    """Run multiple tasks from the queue or auto-pick."""
    schedule = load_schedule()
    topic_queue = get_topic_queue(schedule)

    for i in range(count):
        if topic_queue:
            task = topic_queue.pop(0)
            print(f"\n[{i+1}/{count}] Queued topic: {task[:80]}")
        else:
            task = (
                "Auto-pick a topic: analyze content gaps in skills/content-performance.md "
                "and write about an uncovered RevenueCat topic. Diversify from past content."
            )
            print(f"\n[{i+1}/{count}] Autonomous topic selection")

        await run_one(task)

    # Update schedule with remaining queue
    if schedule:
        schedule["topic_queue"] = topic_queue
        SCHEDULE_PATH.write_text(yaml.dump(schedule, default_flow_style=False))


def main():
    parser = argparse.ArgumentParser(description="Bekku headless content runner")
    parser.add_argument("--task", type=str, help="Specific task to run")
    parser.add_argument("--batch", type=int, default=1, help="Number of tasks to run")
    args = parser.parse_args()

    if args.task:
        asyncio.run(run_one(args.task))
    else:
        asyncio.run(run_batch(args.batch))


if __name__ == "__main__":
    main()
