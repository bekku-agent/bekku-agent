"""Router node — classifies task into content | interactive | feedback."""

from __future__ import annotations

import json

from openai import AsyncOpenAI
import structlog

from src.state import AgentState

logger = structlog.get_logger()

VALID_TYPES = {"content", "interactive", "feedback"}


async def route(state: AgentState) -> AgentState:
    """Classify the task into one of three types using gpt-4o."""
    logger.info("router_start", task=state.task[:80])

    client = AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4o",
        max_tokens=64,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify the user's task into exactly one category.\n\n"
                    "- content: ANY task that requires producing a long-form written artifact — "
                    "blog posts, tutorials, guides, articles, application letters, essays, case studies. "
                    "If the task says 'write', 'draft', 'publish', 'create', or asks a big open-ended question "
                    "that needs a multi-paragraph response, it is CONTENT.\n"
                    "- interactive: short, quick questions that need a brief direct answer — "
                    "'how do I...', 'what is...', 'explain...'. Only use this for questions "
                    "that can be answered in a few sentences.\n"
                    "- feedback: product feedback, API critiques, feature requests, "
                    "improvement suggestions specifically about RevenueCat's product.\n\n"
                    "When in doubt, choose content.\n\n"
                    'Return JSON: {"task_type": "<content|interactive|feedback>"}'
                ),
            },
            {"role": "user", "content": state.task},
        ],
    )

    try:
        data = json.loads(response.choices[0].message.content)
        task_type = data.get("task_type", "content")
        if task_type not in VALID_TYPES:
            task_type = "content"
    except (json.JSONDecodeError, KeyError):
        logger.warning("router_parse_failed", raw=response.choices[0].message.content[:100])
        task_type = "content"

    state.task_type = task_type
    logger.info("router_done", task_type=task_type)
    return state
