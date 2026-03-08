"""Researcher agent node — fetches and compiles context from RC docs and APIs."""

from __future__ import annotations

from pathlib import Path

from openai import AsyncOpenAI
import structlog

from src.state import AgentState
from src.tools.web_tools import fetch_rc_docs

logger = structlog.get_logger()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "researcher.md"


async def research(state: AgentState) -> AgentState:
    """Research a topic using RevenueCat docs and web sources."""
    logger.info("researcher_start", topic=state.topic)
    state.current_step = "research"

    system_prompt = PROMPT_PATH.read_text()

    # Fetch RC documentation
    sources: list[str] = []
    context_parts: list[str] = []

    try:
        rc_docs = await fetch_rc_docs()
        context_parts.append(f"## RevenueCat Documentation Index\n\n{rc_docs[:8000]}")
        sources.append("https://www.revenuecat.com/docs/llms.txt")
    except Exception as e:
        logger.warning("rc_docs_fetch_failed", error=str(e))

    # Use OpenAI to synthesize research
    client = AsyncOpenAI()
    docs_context = "\n\n---\n\n".join(context_parts)

    response = await client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Research the following topic for a technical blog post:\n\n"
                    f"**Topic:** {state.topic}\n\n"
                    f"Here is the RevenueCat documentation context:\n\n{docs_context}\n\n"
                    f"Compile comprehensive research context for the Writer agent."
                ),
            },
        ],
    )

    state.research_context = response.choices[0].message.content
    state.sources = sources
    logger.info("researcher_done", context_length=len(state.research_context))
    return state
