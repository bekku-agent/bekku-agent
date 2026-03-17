"""Planner agent node — reads skill files and produces strategic guidance for the writer."""

from __future__ import annotations

from pathlib import Path

from openai import AsyncOpenAI
import structlog

from src.state import AgentState
from src.tools.skills import load_skills

logger = structlog.get_logger()

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "planner.md"
SKILL_MD = Path(__file__).parent.parent.parent / "skill.md"


async def plan(state: AgentState) -> AgentState:
    """Read skill files and produce strategic guidance for the current task."""
    logger.info("planner_start", task=state.task[:80])

    system_prompt = PROMPT_PATH.read_text()
    skill_context = load_skills("planner")

    if skill_context:
        system_prompt += f"\n\n## Accumulated Knowledge\n\n{skill_context}"

    # Load Bekku identity context
    bekku_context = ""
    if SKILL_MD.exists():
        bekku_context = SKILL_MD.read_text()

    parts = [f"**Task:** {state.task}"]
    if state.task_type:
        parts.append(f"**Task Type:** {state.task_type}")
    if bekku_context:
        parts.append(f"**Bekku Context:**\n\n{bekku_context}")

    parts.append(
        "Produce a strategic brief to guide the writer. "
        "Reference specific data from the skill files above."
    )

    user_content = "\n\n".join(parts)

    client = AsyncOpenAI()

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        state.plan = response.choices[0].message.content
        logger.info("planner_done", plan_len=len(state.plan))
    except Exception as e:
        logger.error("planner_failed", error=str(e))
        state.plan = ""  # Non-fatal — writer can proceed without a plan

    return state
