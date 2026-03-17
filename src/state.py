"""Bekku agent state schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    """State passed between LangGraph nodes."""

    # Input
    task: str = ""
    task_type: str = ""  # "content" | "interactive" | "feedback"

    # Planner output
    plan: str = ""

    # Researcher output
    research_context: str = ""
    sources: list[str] = field(default_factory=list)

    # Writer output
    draft: str = ""
    social_posts: dict[str, str] = field(default_factory=dict)  # {"x": "...", "linkedin": "..."}

    # Publisher output
    published_url: str = ""

    # Tracking
    activity_log: list[dict[str, Any]] = field(default_factory=list)

    # Error tracking
    error: str = ""
