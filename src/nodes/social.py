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

    # Use more of the draft for content threads — need the actual substance
    draft_preview = state.draft[:4000]

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate social media content from technical articles. "
                        "The goal is to deliver REAL VALUE in the post itself — not just tease a link. "
                        "Developers should learn something from reading the post alone.\n\n"
                        "Return JSON with exactly two keys:\n"
                        '{"x": "thread text here", "linkedin": "linkedin post text here"}\n\n'
                        "Rules for X (Twitter) thread:\n"
                        "- Write a 4-8 tweet thread that teaches the key insight from the article\n"
                        "- Format: 1/ first tweet\\n\\n2/ second tweet\\n\\n3/ third tweet\n"
                        "- Tweet 1 is the hook — a bold claim, surprising fact, or question\n"
                        "- Middle tweets deliver the actual content: concepts, code snippets, step-by-step\n"
                        "- Include short code snippets inline where relevant (use backticks)\n"
                        "- Last tweet links to the full article: 'Full article: [GIST_URL]'\n"
                        "- Each tweet max 280 characters\n"
                        "- Tag @RevenueCat if the content is about RevenueCat\n\n"
                        "Rules for LinkedIn:\n"
                        "- Write a substantial post (8-12 sentences) that stands alone as content\n"
                        "- Lead with a provocative insight or counterintuitive observation\n"
                        "- Include the key technical takeaway — what should developers do differently?\n"
                        "- Use line breaks between paragraphs for readability\n"
                        "- End with 'Full article: [GIST_URL]'\n"
                        "- Tag @RevenueCat if the content is about RevenueCat\n"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Write social posts for this article. Deliver the actual value — "
                        f"don't just link to it.\n\n"
                        f"**Task:** {state.task}\n\n"
                        f"**Article content:**\n{draft_preview}"
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
