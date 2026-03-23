"""Writer agent node — produces markdown output from task + research context."""

from __future__ import annotations

from pathlib import Path

from openai import AsyncOpenAI
import structlog

from src.state import AgentState
from src.tools.skills import load_skills

logger = structlog.get_logger()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
SKILL_MD = Path(__file__).parent.parent.parent / "skill.md"

# Map task_type to system prompt file
_PROMPT_FILES = {
    "content": "writer.md",
    "interactive": "interactive.md",
    "feedback": "feedback_writer.md",
}


def _parse_social_posts(raw: str) -> dict[str, str]:
    """Parse social post section into {platform: text} dict."""
    posts = {}
    current_key = None
    current_lines: list[str] = []

    for line in raw.splitlines():
        line_lower = line.strip().lower()
        if line_lower.startswith("**x (") or line_lower.startswith("**x:**") or "tweet" in line_lower and line.startswith("**"):
            if current_key and current_lines:
                posts[current_key] = "\n".join(current_lines).strip()
            current_key = "x"
            current_lines = []
        elif line_lower.startswith("**linkedin"):
            if current_key and current_lines:
                posts[current_key] = "\n".join(current_lines).strip()
            current_key = "linkedin"
            current_lines = []
        elif current_key:
            current_lines.append(line)

    if current_key and current_lines:
        posts[current_key] = "\n".join(current_lines).strip()

    return posts


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

    # Load Bekku's identity and context from skill.md
    bekku_context = ""
    if SKILL_MD.exists():
        bekku_context = SKILL_MD.read_text()

    # Build user message depending on available context
    parts = [f"**Task:** {state.task}"]

    if bekku_context:
        parts.append(
            f"**About You (Bekku) — use this to write as yourself, with real details:**\n\n"
            f"{bekku_context}"
        )

    if state.plan:
        parts.append(f"**Strategic Plan (from Planner):**\n\n{state.plan}")

    if state.research_context:
        parts.append(f"**Research Context:**\n\n{state.research_context}")

    if state.task_type == "interactive":
        parts.append("Respond directly and concisely in markdown.")
    elif state.task_type == "feedback":
        parts.append(
            "Structure your feedback with: Observation, Impact, Suggestion. "
            "MUST be under 2800 characters total."
        )
    else:
        parts.append(
            "Write a concise, technically deep article in markdown. "
            "MUST be under 2800 characters total — this goes directly to LinkedIn. "
            "Include real code snippets with actual SDK methods from the research context. "
            "No generic descriptions — show working code. "
            "No metadata headers (title:, summary:, etc). Just the article."
        )

    user_content = "\n\n".join(parts)

    try:
        response = await client.chat.completions.create(
            model="o3",
            max_completion_tokens=16384,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        draft = response.choices[0].message.content

        # Strip wrapping ```markdown fences if the LLM wrapped the whole output
        if draft.startswith("```markdown"):
            draft = draft[len("```markdown"):].strip()
            if draft.endswith("```"):
                draft = draft[:-3].strip()
        elif draft.startswith("```md"):
            draft = draft[len("```md"):].strip()
            if draft.endswith("```"):
                draft = draft[:-3].strip()

        # Strip any ---SOCIAL--- section if the model included one
        if "---SOCIAL---" in draft:
            draft = draft.split("---SOCIAL---", 1)[0].strip()

        # Fix unclosed code fences — count ``` occurrences, add closing if odd
        fence_count = draft.count("```")
        if fence_count % 2 != 0:
            draft += "\n```"
            logger.warning("writer_fixed_unclosed_fence")

        state.draft = draft
    except Exception as e:
        logger.error("writer_failed", error=str(e))
        state.draft = f"[Writer error: {e}]"
        state.error = str(e)

    logger.info("writer_done", draft_len=len(state.draft))
    return state
