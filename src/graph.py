"""Bekku — LangGraph orchestrator for the multi-agent content pipeline."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from langgraph.graph import StateGraph
import structlog

from src.nodes.publisher import publish
from src.nodes.reporter import report
from src.nodes.researcher import research
from src.nodes.writer import write
from src.state import AgentState, Mode

load_dotenv()
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer(),
    ],
)
logger = structlog.get_logger()


def build_async_graph() -> StateGraph:
    """Build the async content production graph."""
    graph = StateGraph(AgentState)

    graph.add_node("research", research)
    graph.add_node("write", write)
    graph.add_node("publish", publish)
    graph.add_node("report", report)

    graph.set_entry_point("research")
    graph.add_edge("research", "write")
    graph.add_edge("write", "publish")
    graph.add_edge("publish", "report")
    graph.set_finish_point("report")

    return graph.compile()


async def run_async_pipeline(topic: str) -> AgentState:
    """Run the full async content pipeline for a topic."""
    logger.info("pipeline_start", topic=topic)

    graph = build_async_graph()
    initial_state = AgentState(topic=topic, mode=Mode.ASYNC)

    result = await graph.ainvoke(initial_state)

    logger.info(
        "pipeline_done",
        title=result.title if hasattr(result, "title") else result.get("title", ""),
        gist_url=result.gist_url if hasattr(result, "gist_url") else result.get("gist_url", ""),
    )
    return result


async def run_interactive(prompt: str) -> str:
    """Run interactive mode — respond to a live prompt."""
    from openai import AsyncOpenAI

    system_prompt = (Path(__file__).parent / "prompts" / "interactive.md").read_text()
    client = AsyncOpenAI()

    response = await client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: bekku <topic>")
        print("       bekku --interactive <prompt>")
        sys.exit(1)

    if sys.argv[1] == "--interactive":
        prompt = " ".join(sys.argv[2:])
        result = asyncio.run(run_interactive(prompt))
        print(result)
    else:
        topic = " ".join(sys.argv[1:])
        result = asyncio.run(run_async_pipeline(topic))
        if hasattr(result, "gist_url"):
            url = result.gist_url
        else:
            url = result.get("gist_url", "N/A")
        print(f"\nPublished: {url}")


if __name__ == "__main__":
    main()
