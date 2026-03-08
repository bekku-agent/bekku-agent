"""Writer agent node — produces technical content from research context."""

from __future__ import annotations

import json
from pathlib import Path

from openai import AsyncOpenAI
import structlog

from src.state import AgentState

logger = structlog.get_logger()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "writer.md"


def _extract_json(raw: str) -> dict:
    """Extract JSON from a response that may be wrapped in code fences."""
    # Strip code fences if present
    text = raw.strip()
    if text.startswith("```json"):
        text = text[len("```json"):]
    elif text.startswith("```"):
        text = text[len("```"):]
    if text.endswith("```"):
        text = text[:-len("```")]

    return json.loads(text.strip())


async def write(state: AgentState) -> AgentState:
    """Generate technical content from research context."""
    logger.info("writer_start", topic=state.topic)
    state.current_step = "write"

    system_prompt = PROMPT_PATH.read_text()

    client = AsyncOpenAI()
    response = await client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Write a technical blog post on the following topic:\n\n"
                    f"**Topic:** {state.topic}\n\n"
                    f"**Research Context:**\n\n{state.research_context}\n\n"
                    f"Return your output as JSON with keys: title, summary, body, tags"
                ),
            },
        ],
    )

    raw = response.choices[0].message.content

    try:
        data = _extract_json(raw)
        state.title = data.get("title", state.topic)
        state.summary = data.get("summary", "")
        state.body = data.get("body", raw)
        state.tags = data.get("tags", [])
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning("writer_json_parse_failed", error=str(e), raw_preview=raw[:200])
        state.title = state.topic
        state.body = raw

    logger.info("writer_done", title=state.title, has_summary=bool(state.summary), tag_count=len(state.tags))
    return state
