"""Bekku — LangGraph orchestrator with learning loop, intent routing, and human-in-the-loop approval.

Architecture (Larry-inspired learning loop):
  planner → router → researcher → writer → ⏸ approval → publisher → analyzer
     ▲                                                                   │
     └──────────── skills/*.md (compounding knowledge) ◄─────────────────┘
"""

from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from langgraph.types import interrupt, Command
import structlog

from src.nodes.analyzer import analyze
from src.nodes.planner import plan
from src.nodes.publisher import publish
from src.nodes.researcher import research
from src.nodes.router import route
from src.nodes.social import generate_social
from src.nodes.writer import write
from src.state import AgentState

load_dotenv()
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer(),
    ],
)
logger = structlog.get_logger()


# --- Routing logic ---

def _route_after_router(state: AgentState) -> str:
    """Conditional edge: interactive skips planner and goes straight to researcher.
    Content/feedback go through planner first for strategic guidance."""
    if state.task_type == "interactive":
        return "researcher"
    return "planner"


def _route_after_writer(state: AgentState) -> str:
    """Conditional edge: interactive skips social+approval, content goes to social."""
    if state.task_type == "interactive":
        return END
    return "social"


# --- Human-in-the-loop approval node ---

def approve(state: AgentState) -> AgentState:
    """Pause for operator approval before publishing.

    The operator can:
    - approve: continue to publisher as-is
    - edit: update the draft, then continue to publisher
    - reject: skip publisher, go straight to analyzer
    """
    decision = interrupt({
        "task": state.task,
        "task_type": state.task_type,
        "draft": state.draft,
        "sources": state.sources,
        "message": "Review the draft. Reply with: approve, reject, or provide edited content.",
    })

    if isinstance(decision, dict):
        action = decision.get("action", "approve")
        if action == "edit" and "draft" in decision:
            state.draft = decision["draft"]
            logger.info("draft_edited_by_operator")
        elif action == "reject":
            state.draft = "[Rejected by operator]"
            state.error = "Draft rejected by operator"
            logger.info("draft_rejected")
    elif isinstance(decision, str):
        if decision.lower() == "reject":
            state.draft = "[Rejected by operator]"
            state.error = "Draft rejected by operator"
            logger.info("draft_rejected")
        elif decision.lower() != "approve":
            # Treat any other string as an edited draft
            state.draft = decision
            logger.info("draft_edited_by_operator")

    return state


def _route_after_approval(state: AgentState) -> str:
    """Skip publisher if draft was rejected."""
    if state.error and "rejected" in state.error.lower():
        return "analyzer"
    return "publisher"


# --- Build graphs ---

def _build_graph():
    """Build the Bekku pipeline graph with learning loop, conditional routing, and HIL.

    content/feedback: router → planner → researcher → writer → social → ⏸ approval → publisher → analyzer
    interactive:      router → researcher (lightweight) → writer → END
    """
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("router", route)
    graph.add_node("planner", plan)
    graph.add_node("researcher", research)
    graph.add_node("writer", write)
    graph.add_node("social", generate_social)
    graph.add_node("approval", approve)
    graph.add_node("publisher", publish)
    graph.add_node("analyzer", analyze)

    # Entry: router classifies first (cheap — one small LLM call)
    graph.set_entry_point("router")

    # Conditional: router → planner (content/feedback) or researcher (interactive)
    graph.add_conditional_edges(
        "router",
        _route_after_router,
        {"planner": "planner", "researcher": "researcher"},
    )

    # planner → researcher
    graph.add_edge("planner", "researcher")

    # researcher always → writer
    graph.add_edge("researcher", "writer")

    # Conditional: writer → social (content/feedback) or END (interactive)
    graph.add_conditional_edges(
        "writer",
        _route_after_writer,
        {"social": "social", END: END},
    )

    # social → approval
    graph.add_edge("social", "approval")

    # Conditional: approval → publisher or analyzer (rejected skips publish)
    graph.add_conditional_edges(
        "approval",
        _route_after_approval,
        {"publisher": "publisher", "analyzer": "analyzer"},
    )

    # publisher always → analyzer
    graph.add_edge("publisher", "analyzer")

    return graph.compile()


# Module-level compiled graph — referenced by langgraph.json
graph = _build_graph()


# --- CLI ---

async def run(task: str) -> AgentState:
    """Run the pipeline. For content/feedback tasks, this will pause at approval."""
    logger.info("pipeline_start", task=task[:80])
    initial_state = AgentState(task=task)
    result = await graph.ainvoke(initial_state)
    logger.info("pipeline_done", task_type=result.get("task_type", ""), published_url=result.get("published_url", ""))
    return result


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.graph <task description>")
        print("\nExamples:")
        print('  python -m src.graph "Write a blog post about paywall best practices"')
        print('  python -m src.graph "How do I set up RevenueCat in a Flutter app?"')
        print('  python -m src.graph "What could RevenueCat improve about their API?"')
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    result = asyncio.run(run(task))

    # Print output
    task_type = result.get("task_type", "") if isinstance(result, dict) else result.task_type
    draft = result.get("draft", "") if isinstance(result, dict) else result.draft
    url = result.get("published_url", "") if isinstance(result, dict) else result.published_url

    print(f"\n{'='*60}")
    print(f"Task type: {task_type}")
    if url:
        print(f"Published: {url}")
    print(f"{'='*60}\n")
    print(draft)


if __name__ == "__main__":
    main()
