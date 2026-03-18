"""Social post generator node — creates X and LinkedIn posts from the article draft."""

from __future__ import annotations

import json

from openai import AsyncOpenAI
import structlog

from src.state import AgentState

logger = structlog.get_logger()


async def generate_social(state: AgentState) -> AgentState:
    """Generate X and LinkedIn posts from the article draft."""
    # Skip for interactive tasks
    if state.task_type == "interactive":
        return state

    # Skip if no draft
    if not state.draft or state.draft.startswith("["):
        return state

    # If writer already produced social posts, keep them
    if state.social_posts:
        logger.info("social_already_present", platforms=list(state.social_posts.keys()))
        return state

    logger.info("social_start", draft_len=len(state.draft))

    client = AsyncOpenAI()

    # Use first 2000 chars of draft for context — enough to understand the topic
    draft_preview = state.draft[:2000]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1024,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate social media posts for technical articles. "
                        "Return JSON with exactly two keys:\n"
                        '{"x": "tweet text here", "linkedin": "linkedin post text here"}\n\n'
                        "Rules for X (Twitter):\n"
                        "- Max 280 characters per tweet\n"
                        "- For longer content, use a thread: 1/ first tweet\\n\\n2/ second tweet\n"
                        "- Hook developers — make them stop scrolling\n"
                        "- End with [GIST_URL] placeholder\n\n"
                        "Rules for LinkedIn:\n"
                        "- 3-5 sentences for developer/startup audience\n"
                        "- Lead with an insight or hot take, NOT 'I just published...'\n"
                        "- End with [GIST_URL] placeholder\n"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Write social posts for this article:\n\n"
                        f"**Task:** {state.task}\n\n"
                        f"**Article preview:**\n{draft_preview}"
                    ),
                },
            ],
        )

        data = json.loads(response.choices[0].message.content)
        state.social_posts = {
            "x": data.get("x", ""),
            "linkedin": data.get("linkedin", ""),
        }
        logger.info("social_done", platforms=list(state.social_posts.keys()))

    except Exception as e:
        logger.error("social_failed", error=str(e))
        state.social_posts = {}

    return state
