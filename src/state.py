"""Bekku agent state schema."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Mode(str, Enum):
    ASYNC = "async"
    INTERACTIVE = "interactive"


@dataclass
class AgentState:
    """State passed between LangGraph nodes."""

    # Input
    topic: str = ""
    mode: Mode = Mode.ASYNC
    prompt: str = ""  # For interactive mode

    # Researcher output
    research_context: str = ""
    sources: list[str] = field(default_factory=list)

    # Writer output
    title: str = ""
    summary: str = ""
    body: str = ""
    tags: list[str] = field(default_factory=list)

    # Publisher output
    gist_url: str = ""
    commit_sha: str = ""

    # Reporter
    activity_log: list[dict[str, Any]] = field(default_factory=list)

    # Interactive mode response
    response: str = ""

    # Control flow
    error: str = ""
    current_step: str = ""
