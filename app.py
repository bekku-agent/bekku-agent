"""Bekku — Streamlit UI with human-in-the-loop approval."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.types import Command

from src.graph import (
    _route_after_approval,
    _route_after_router,
    _route_after_writer,
    approve,
    route,
    research,
    write,
    publish,
    report,
)
from src.state import AgentState

load_dotenv()

st.set_page_config(
    page_title="Bekku — AI Developer Advocate",
    page_icon="🐱",
    layout="wide",
)


# --- Graph Setup ---

@st.cache_resource
def get_graph():
    graph = StateGraph(AgentState)
    graph.add_node("router", route)
    graph.add_node("researcher", research)
    graph.add_node("writer", write)
    graph.add_node("approval", approve)
    graph.add_node("publisher", publish)
    graph.add_node("reporter", report)
    graph.set_entry_point("router")
    graph.add_conditional_edges("router", _route_after_router, {"researcher": "researcher", "writer": "writer"})
    graph.add_edge("researcher", "writer")
    graph.add_conditional_edges("writer", _route_after_writer, {"approval": "approval", "reporter": "reporter"})
    graph.add_conditional_edges("approval", _route_after_approval, {"publisher": "publisher", "reporter": "reporter"})
    graph.add_edge("publisher", "reporter")
    graph.set_finish_point("reporter")
    return graph.compile(checkpointer=MemorySaver())


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


graph = get_graph()

# --- Session State ---
for key, default in [
    ("runs", []),
    ("pending_approval", None),
    ("last_response", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# --- Sidebar ---

with st.sidebar:
    st.image("https://em-content.zobj.net/source/twitter/408/cat-face_1f431.png", width=60)
    st.title("Bekku")
    st.caption("Autonomous Developer Advocacy Agent")
    st.divider()

    st.markdown("**How it works**")
    st.markdown(
        "1. Give Bekku a task\n"
        "2. Bekku researches & writes a draft\n"
        "3. You review, edit, and approve\n"
        "4. Published to GitHub Gist"
    )
    st.divider()

    # Run history
    st.markdown("**History**")
    if not st.session_state.runs:
        st.info("No runs yet")
    for run in reversed(st.session_state.runs[-10:]):
        label = run["task"][:50] + ("..." if len(run["task"]) > 50 else "")
        if run.get("published_url"):
            st.success(f"[{label}]({run['published_url']})", icon="✅")
        elif run.get("pending"):
            st.warning(label, icon="⏸️")
        elif run.get("rejected"):
            st.error(label, icon="❌")
        else:
            st.info(label, icon="💬")

    st.divider()
    st.caption("Operator: MK (@mkshivaswami)")
    st.caption("Stack: LangGraph + GPT-4o + GitHub")


# =============================================================
# MAIN AREA
# =============================================================

# --- Header ---
st.title("🐱 Bekku")
st.markdown("**AI Developer Advocacy Agent** · Human-in-the-Loop · Powered by LangGraph")
st.divider()


# =============================================================
# STATE: Pending approval → show review UI
# =============================================================
if st.session_state.pending_approval is not None:
    approval = st.session_state.pending_approval

    st.header("Review & Approve")
    st.caption(f"{len(approval['draft'].split()):,} words · Publishing to GitHub Gist")

    # Side-by-side: edit markdown on the left, live preview on the right
    col_edit, col_preview = st.columns(2)

    with col_edit:
        st.markdown("**Edit**")
        edited_draft = st.text_area(
            "Markdown editor",
            value=approval["draft"],
            height=500,
            key="draft_editor",
            label_visibility="collapsed",
        )

    with col_preview:
        st.markdown("**Preview**")
        preview_container = st.container(height=500, border=True)
        with preview_container:
            st.markdown(st.session_state.get("draft_editor", approval["draft"]))

    # Actions
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("✅ Approve & Publish to Gist", type="primary", use_container_width=True):
            config = {"configurable": {"thread_id": approval["thread_id"]}}
            now = datetime.now(timezone.utc).strftime("%H:%M UTC")

            final_draft = st.session_state.get("draft_editor", approval["draft"])
            if final_draft != approval["draft"]:
                decision = {"action": "edit", "draft": final_draft}
            else:
                decision = "approve"

            with st.spinner("Publishing to GitHub Gist..."):
                result = run_async(graph.ainvoke(Command(resume=decision), config=config))
                url = result.get("published_url", "") if isinstance(result, dict) else ""

            for run in st.session_state.runs:
                if run["task"] == approval["task"] and run.get("pending"):
                    run["pending"] = False
                    run["published_url"] = url
                    run["timestamp"] = now

            st.session_state.pending_approval = None

            if url:
                st.balloons()
                st.success(f"Published! [Open Gist →]({url})")
            else:
                st.warning("Publish completed but no URL returned. Check `GITHUB_TOKEN`.")
            st.rerun()

    with col2:
        if st.button("🔄 Regenerate", use_container_width=True):
            task = approval["task"]
            st.session_state.pending_approval = None
            st.session_state.runs = [r for r in st.session_state.runs if r["task"] != task]
            st.rerun()

    with col3:
        if st.button("❌ Reject", use_container_width=True):
            config = {"configurable": {"thread_id": approval["thread_id"]}}
            now = datetime.now(timezone.utc).strftime("%H:%M UTC")
            run_async(graph.ainvoke(Command(resume="reject"), config=config))

            for run in st.session_state.runs:
                if run["task"] == approval["task"] and run.get("pending"):
                    run["pending"] = False
                    run["rejected"] = True
                    run["timestamp"] = now

            st.session_state.pending_approval = None
            st.rerun()


# =============================================================
# STATE: No pending approval → show task input
# =============================================================
else:
    # Show last interactive response
    if st.session_state.last_response:
        resp = st.session_state.last_response
        with st.container():
            st.markdown(f"**You:** {resp['task']}")
            st.caption(f"Classified as `{resp['task_type']}`")
            st.markdown(resp["draft"])
            if st.button("Clear response"):
                st.session_state.last_response = None
                st.rerun()
        st.divider()

    # Example buttons (above the text area so clicking fills it)
    EXAMPLES = [
        ("📝 A/B test paywalls tutorial", "Write a tutorial on A/B testing paywalls with RevenueCat Experiments"),
        ("📄 RC application letter", "How will the rise of agentic AI change app development and growth over the next 12 months, and why are you the right agent to be RevenueCat's first Agentic AI Developer & Growth Advocate?"),
        ("💬 Flutter integration", "How do I integrate RevenueCat with a Flutter app?"),
        ("🔍 SDK onboarding feedback", "What could RevenueCat improve about their SDK onboarding experience?"),
        ("📝 StoreKit migration guide", "Write a case study on migrating from StoreKit to RevenueCat"),
        ("💬 Entitlements explained", "How do RevenueCat entitlements work and when should I use them?"),
    ]

    st.caption("Quick start:")
    row1 = st.columns(3)
    row2 = st.columns(3)
    rows = [row1, row2]
    for i, (label, prompt) in enumerate(EXAMPLES):
        col = rows[i // 3][i % 3]
        if col.button(label, key=f"ex_{i}", use_container_width=True):
            st.session_state.task_area = prompt
            st.rerun()

    # Task input
    task = st.text_area(
        "What should Bekku work on?",
        height=120,
        key="task_area",
    )

    if st.button("🚀 Run", type="primary", disabled=not task):
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        now = datetime.now(timezone.utc).strftime("%H:%M UTC")

        # Progress container
        progress = st.container()

        with progress:
            step1 = st.empty()
            step2 = st.empty()
            step3 = st.empty()

            step1.info("🔀 Classifying task...", icon="⏳")
            result = run_async(graph.ainvoke(AgentState(task=task), config=config))

            snapshot = graph.get_state(config)

            if snapshot.next and "approval" in snapshot.next:
                # Content/feedback — hit approval gate
                state_values = snapshot.values
                task_type = state_values.get("task_type", "")
                sources = state_values.get("sources", [])

                step1.success(f"Classified as **{task_type}**", icon="✅")
                if state_values.get("research_context"):
                    step2.success(f"Research complete — {len(sources)} sources found", icon="✅")
                step3.success("Draft ready — review below", icon="✅")

                st.session_state.pending_approval = {
                    "task": task,
                    "task_type": task_type,
                    "draft": state_values.get("draft", ""),
                    "sources": sources,
                    "research_context": state_values.get("research_context", ""),
                    "thread_id": thread_id,
                }
                st.session_state.runs.append({"task": task, "pending": True, "timestamp": now})
                st.rerun()

            else:
                # Interactive — done
                draft = result.get("draft", "") if isinstance(result, dict) else result.draft
                task_type = result.get("task_type", "") if isinstance(result, dict) else result.task_type

                step1.success(f"Classified as **{task_type}**", icon="✅")
                step2.success("Response generated", icon="✅")

                st.session_state.runs.append({"task": task, "pending": False, "timestamp": now})
                st.session_state.last_response = {
                    "task": task,
                    "task_type": task_type,
                    "draft": draft,
                }
                st.rerun()
