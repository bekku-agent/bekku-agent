"""Bekku — LangGraph orchestrator with intent-based routing."""

from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
import structlog

from src.nodes.publisher import publish
from src.nodes.reporter import report
from src.nodes.researcher import research
from src.nodes.router import route
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
    """Conditional edge: skip researcher for interactive tasks."""
    if state.task_type == "interactive":
        return "writer"
    return "researcher"


def _route_after_writer(state: AgentState) -> str:
    """Conditional edge: skip publisher for interactive tasks."""
    if state.task_type == "interactive":
        return "reporter"
    return "publisher"


# --- Build graph ---

def _build_graph():
    """Build the Bekku pipeline graph with conditional routing.

    content/feedback: router → researcher → writer → publisher → reporter
    interactive:      router → writer → reporter
    """
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("router", route)
    graph.add_node("researcher", research)
    graph.add_node("writer", write)
    graph.add_node("publisher", publish)
    graph.add_node("reporter", report)

    # Entry
    graph.set_entry_point("router")

    # Conditional: router → researcher or writer
    graph.add_conditional_edges(
        "router",
        _route_after_router,
        {"researcher": "researcher", "writer": "writer"},
    )

    # researcher always → writer
    graph.add_edge("researcher", "writer")

    # Conditional: writer → publisher or reporter
    graph.add_conditional_edges(
        "writer",
        _route_after_writer,
        {"publisher": "publisher", "reporter": "reporter"},
    )

    # publisher always → reporter
    graph.add_edge("publisher", "reporter")

    # Finish
    graph.set_finish_point("reporter")

    return graph.compile()


# Module-level compiled graph — referenced by langgraph.json
graph = _build_graph()


# --- CLI ---

async def run(task: str) -> AgentState:
    """Run the full pipeline for a task."""
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
