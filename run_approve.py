"""Bekku — Issue approval handler for GitHub Actions.

Called when MK comments on a Bekku draft issue.
Reads the comment, publishes to gist if approved, runs the analyzer,
and comments back with the final social posts.

Usage:
    python run_approve.py --issue 42 --action approve
    python run_approve.py --issue 42 --action reject
    python run_approve.py --issue 42 --action edit --draft "edited content..."
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re

from dotenv import load_dotenv
from github import Github

load_dotenv()


def get_repo():
    token = os.environ.get("GH_TOKEN") or os.environ["GITHUB_TOKEN"]
    repo_name = os.environ.get("GITHUB_REPO", "bekku-agent/bekku-agent")
    gh = Github(token)
    return gh.get_repo(repo_name)


def extract_draft_from_issue(body: str) -> str:
    """Extract the draft markdown from the issue body (between HTML comment markers)."""
    match = re.search(r"<!-- DRAFT_START -->\s*(.*?)\s*<!-- DRAFT_END -->", body, re.DOTALL)
    if match:
        return match.group(1).strip()
    return body


def extract_social_from_issue(body: str) -> dict[str, str]:
    """Extract social posts from the issue body."""
    social = {}
    # Extract X post
    x_match = re.search(r"### X \(Twitter\)\n```\n(.*?)\n```", body, re.DOTALL)
    if x_match:
        social["x"] = x_match.group(1)
    # Extract LinkedIn post
    li_match = re.search(r"### LinkedIn\n```\n(.*?)\n```", body, re.DOTALL)
    if li_match:
        social["linkedin"] = li_match.group(1)
    return social


def extract_task_from_issue(title: str) -> str:
    """Extract the original task from the issue title."""
    return title.replace("[Bekku Draft] ", "")


async def handle_approve(issue_number: int, action: str, edited_draft: str | None = None):
    """Handle an approval action on a draft issue."""
    from src.nodes.analyzer import analyze
    from src.nodes.publisher import publish
    from src.state import AgentState

    repo = get_repo()
    issue = repo.get_issue(issue_number)

    task = extract_task_from_issue(issue.title)
    draft = edited_draft or extract_draft_from_issue(issue.body)
    social = extract_social_from_issue(issue.body)
    print(f"  Draft length: {len(draft)}")
    print(f"  Social posts found: {list(social.keys()) if social else 'none'}")

    if action == "reject":
        # Log rejection and close
        state = AgentState(
            task=task,
            task_type="content",
            draft="[Rejected by operator]",
            error="Draft rejected by operator",
        )
        await analyze(state)

        issue.create_comment("Draft rejected. Logged to failure-log.md for learning.")
        try:
            issue.remove_from_labels("awaiting-review")
        except Exception:
            pass
        try:
            issue.add_to_labels("rejected")
        except Exception:
            pass
        issue.edit(state="closed")
        print(f"Issue #{issue_number} rejected and closed.")
        return

    # Approve or edit → publish
    state = AgentState(
        task=task,
        task_type="content",
        draft=draft,
        social_posts=social,
    )

    # Publish to gist
    state = await publish(state)

    if not state.published_url:
        issue.create_comment(f"Publish failed: {state.error}")
        return

    # Run analyzer to log outcome
    await analyze(state)

    # Build comment with published article + social posts (URL filled in)
    from src.nodes.publisher import _extract_title_and_body
    _, clean_body = _extract_title_and_body(draft)

    comment_parts = [
        f"Published! {state.published_url}\n",
        "---\n",
        clean_body,
        "\n---\n",
    ]

    if social:
        comment_parts.append("**Social posts ready to copy:**\n")
        if social.get("x"):
            x_text = social["x"].replace("[GIST_URL]", state.published_url)
            comment_parts.append(f"**X (Twitter)**\n```\n{x_text}\n```\n")
        if social.get("linkedin"):
            li_text = social["linkedin"].replace("[GIST_URL]", state.published_url)
            comment_parts.append(f"**LinkedIn**\n```\n{li_text}\n```\n")

    comment_parts.append(
        "\n---\n"
        "After posting to LinkedIn, come back and comment with engagement numbers:\n"
        "`engagement: <linkedin_url> <impressions> <likes> <comments> <shares>`"
    )

    issue.create_comment("\n".join(comment_parts))
    try:
        issue.remove_from_labels("awaiting-review")
    except Exception:
        pass
    try:
        issue.add_to_labels("published")
    except Exception:
        pass
    issue.edit(state="closed")
    print(f"Issue #{issue_number} published: {state.published_url}")


async def handle_engagement(issue_number: int, comment_body: str):
    """Parse an engagement comment and log it."""
    from src.tools.skills import log_engagement

    # Expected format: engagement: <linkedin_url> <impressions> <likes> <comments> <shares>
    match = re.match(
        r"engagement:\s*(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
        comment_body.strip(),
    )
    if not match:
        print(f"Could not parse engagement from: {comment_body}")
        return

    linkedin_url = match.group(1)
    impressions = int(match.group(2))
    likes = int(match.group(3))
    comments = int(match.group(4))
    shares = int(match.group(5))

    repo = get_repo()
    issue = repo.get_issue(issue_number)
    task = extract_task_from_issue(issue.title)

    # Find the published URL from the issue comments
    published_url = ""
    for comment in issue.get_comments():
        if "Published!" in comment.body:
            url_match = re.search(r"(https://gist\.github\.com/\S+)", comment.body)
            if url_match:
                published_url = url_match.group(1)
                break

    if not published_url:
        print("Could not find published URL in issue comments")
        return

    log_engagement(
        published_url=published_url,
        linkedin_url=linkedin_url,
        impressions=impressions,
        likes=likes,
        comments=comments,
        shares=shares,
    )

    issue.create_comment(
        f"Engagement logged! {impressions} impressions, {likes} likes, "
        f"{comments} comments, {shares} shares. "
        f"Planner will use this data in the next content run."
    )
    print(f"Engagement logged for issue #{issue_number}")


def main():
    parser = argparse.ArgumentParser(description="Bekku issue approval handler")
    parser.add_argument("--issue", type=int, required=True, help="Issue number")
    parser.add_argument("--action", type=str, required=True, help="approve|reject|edit|engagement")
    parser.add_argument("--draft", type=str, help="Edited draft content (for edit action)")
    parser.add_argument("--comment", type=str, help="Raw comment body (for engagement)")
    args = parser.parse_args()

    if args.action == "engagement":
        asyncio.run(handle_engagement(args.issue, args.comment or ""))
    else:
        asyncio.run(handle_approve(args.issue, args.action, args.draft))


if __name__ == "__main__":
    main()
