"""Writer agent node — produces markdown output from task + research context."""

from __future__ import annotations

from pathlib import Path

from openai import AsyncOpenAI
import structlog

from src.state import AgentState
from src.tools.skills import load_skills

logger = structlog.get_logger()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Map task_type to system prompt file
_PROMPT_FILES = {
    "content": "writer.md",
    "interactive": "interactive.md",
    "feedback": "feedback_writer.md",
}


def _load_system_prompt(task_type: str) -> str:
    """Load the appropriate system prompt for the task type."""
    filename = _PROMPT_FILES.get(task_type, "writer.md")
    path = PROMPTS_DIR / filename
    if not path.exists():
        # Fall back to the general writer prompt
        path = PROMPTS_DIR / "writer.md"
    return path.read_text()


async def write(state: AgentState) -> AgentState:
    """Generate markdown content based on task type and research context."""
    logger.info("writer_start", task_type=state.task_type, task=state.task[:80])

    system_prompt = _load_system_prompt(state.task_type)
    skill_key = "feedback_writer" if state.task_type == "feedback" else "writer"
    skill_context = load_skills(skill_key)
    if skill_context:
        system_prompt += f"\n\n## Accumulated Knowledge\n\n{skill_context}"
    client = AsyncOpenAI()

    # Build user message depending on available context
    parts = [f"**Task:** {state.task}"]
    if state.research_context:
        parts.append(f"**Research Context:**\n\n{state.research_context}")
    if state.task_type == "interactive":
        parts.append("Respond directly and concisely in markdown.")
    elif state.task_type == "feedback":
        parts.append("Structure your feedback with: Observation, Impact, Suggestion.")
    else:
        parts.append("Write a complete technical article in markdown.")

    user_content = "\n\n".join(parts)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        state.draft = response.choices[0].message.content
    except Exception as e:
        logger.error("writer_failed", error=str(e))
        state.draft = f"[Writer error: {e}]"
        state.error = str(e)

    logger.info("writer_done", draft_len=len(state.draft))
    return state
