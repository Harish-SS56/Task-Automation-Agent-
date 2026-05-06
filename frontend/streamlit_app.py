"""
Streamlit UI for the Task Automation Agent.
"""

import sys
from pathlib import Path

import streamlit as st

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path.parent))

from backend.core.orchestrator import TaskOrchestrator  # noqa: E402


def main():
    st.set_page_config(
        page_title="Task Automation Agent", page_icon="🤖", layout="wide"
    )

    st.title("Intelligent Task Automation Agent")
    st.markdown(
        "An autonomous AI agent that takes high-level goals, breaks them down into tasks, "
        "plans execution, adapts to obstacles, and learns from experience."
    )

    # Initialize session state
    if "orchestrator" not in st.session_state:
        # Output goes to 'output/' subfolder — keeps agent files separate from created projects
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        st.session_state.orchestrator = TaskOrchestrator(base_path=str(output_dir))

    if "current_session" not in st.session_state:
        st.session_state.current_session = None

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Choose a page",
            ["Execute Goal", "View Progress", "Session History", "Learned Patterns"],
        )
        st.divider()
        output_dir = Path(__file__).parent.parent / "output"
        st.caption("📁 **Output folder:**")
        st.code(str(output_dir), language=None)

    # Main content
    if page == "Execute Goal":
        show_execute_goal()
    elif page == "View Progress":
        show_progress()
    elif page == "Session History":
        show_session_history()
    elif page == "Learned Patterns":
        show_learned_patterns()


def show_execute_goal():
    """Show the goal execution interface."""
    st.header("Execute a Goal")

    goal_description = st.text_area(
        "Describe your goal",
        placeholder="e.g., Set up a new Python project with FastAPI, git repository, and README",
        height=120,
    )

    context = st.text_area(
        "Additional context (optional)",
        placeholder="Any additional information that might help...",
        height=100,
    )

    execute_button = st.button("Execute Goal", type="primary")

    if execute_button and goal_description:
        # Clear any stale human-input state from previous runs
        st.session_state.orchestrator.pending_human_inputs.clear()

        with st.spinner("⚙️ Executing goal — this may take a moment..."):
            try:
                context_dict = {"context": context} if context.strip() else {}

                session = st.session_state.orchestrator.execute_goal(
                    goal_description, context_dict
                )
                st.session_state.current_session = session
                st.success("✅ Goal execution completed!")
                _show_session_summary(session)

            except Exception as e:
                st.error(f"Error executing goal: {str(e)}")

    elif execute_button and not goal_description:
        st.warning("Please describe your goal before clicking Execute.")

    # -----------------------------------------------------------------------
    # Pending human-input requests
    # Snapshot the keys to avoid "dictionary changed size during iteration"
    # -----------------------------------------------------------------------
    pending = dict(st.session_state.orchestrator.pending_human_inputs)
    if pending:
        st.subheader("⚠️ Human Input Required")
        st.info(
            "The agent needs your confirmation before proceeding with "
            "the following tasks:"
        )

        for request_id, request in pending.items():
            # The key may have been removed already (e.g. on a rerun after submit)
            if request_id not in st.session_state.orchestrator.pending_human_inputs:
                continue

            with st.expander(f"📋 {request.question[:80]}...", expanded=True):
                st.write(request.question)

                if request.options:
                    response = st.radio(
                        "Choose an option",
                        request.options,
                        key=f"input_{request_id}",
                    )
                else:
                    response = st.text_input(
                        "Your response",
                        key=f"input_{request_id}",
                    )

                if st.button("Submit Response", key=f"submit_{request_id}"):
                    # provide_human_input already removes the key internally.
                    # Use pop() as a safety guard to avoid KeyError on rerun.
                    result = st.session_state.orchestrator.provide_human_input(
                        request_id, response
                    )
                    # Also ensure it's gone from our snapshot (belt-and-suspenders)
                    st.session_state.orchestrator.pending_human_inputs.pop(
                        request_id, None
                    )

                    if result.get("success"):
                        st.success("✅ Response submitted!")
                        st.rerun()
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")


def show_progress():
    """Show progress of current execution."""
    st.header("Execution Progress")

    if not st.session_state.current_session:
        st.info("No active session. Execute a goal to see progress.")
        return

    session = st.session_state.current_session

    try:
        progress = st.session_state.orchestrator.progress_tracker.get_progress(
            session.goal, session.execution_plan
        )

        st.metric("Completion", f"{progress['completion_percentage']:.1f}%")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("✅ Completed", progress["completed"])
        with col2:
            st.metric("❌ Failed", progress["failed"])
        with col3:
            st.metric("🔄 In Progress", progress["in_progress"])
        with col4:
            st.metric("⏳ Pending", progress["pending"])

        st.subheader("Task Details")
        task_summary = (
            st.session_state.orchestrator.progress_tracker.get_task_status_summary(
                session.execution_plan
            )
        )

        for task_info in task_summary:
            emoji = {
                "completed": "✅",
                "failed": "❌",
                "in_progress": "🔄",
                "pending": "⏳",
                "waiting_for_human": "👤",
            }.get(task_info["status"], "❓")

            with st.expander(f"{emoji} {task_info['description']}"):
                st.write(f"**Status:** {task_info['status']}")
                st.write(f"**Priority:** {task_info['priority']}")
                if task_info.get("error"):
                    st.error(f"Error: {task_info['error']}")

    except Exception as e:
        st.error(f"Error loading progress: {str(e)}")


def _show_session_summary(session):
    """Show a summary of a session."""
    st.write(f"**Goal:** {session.goal.description}")
    st.write(f"**Status:** {session.goal.status.value}")

    # Task breakdown
    if session.execution_plan and session.execution_plan.tasks:
        completed = sum(
            1 for t in session.execution_plan.tasks if t.status.value == "completed"
        )
        total = len(session.execution_plan.tasks)
        st.write(f"**Tasks:** {completed}/{total} completed")

        with st.expander("📋 Task Breakdown"):
            for task in session.execution_plan.tasks:
                emoji = {
                    "completed": "✅",
                    "failed": "❌",
                    "in_progress": "🔄",
                    "pending": "⏳",
                }.get(task.status.value, "❓")
                st.write(f"{emoji} {task.description}")
                if task.error:
                    st.caption(f"   ⚠️ {task.error}")

    # Adaptations / learnings
    if session.adaptations:
        with st.expander("🧠 Learnings & Recommendations"):
            for adaptation in session.adaptations:
                if adaptation.recommendations:
                    for rec in adaptation.recommendations:
                        st.write(f"- {rec}")


def show_session_history():
    """Show history of past sessions."""
    st.header("Session History")

    orchestrator = st.session_state.orchestrator
    session_ids = orchestrator.memory_manager.list_sessions()

    if not session_ids:
        st.info("No past sessions found. Execute some goals to build history!")
        return

    selected_id = st.selectbox("Select a session", session_ids)
    if selected_id:
        session = orchestrator.memory_manager.load_session(selected_id)
        if session:
            _show_session_summary(session)
        else:
            st.error("Could not load session data.")


def show_learned_patterns():
    """Show learned patterns."""
    st.header("Learned Patterns")

    orchestrator = st.session_state.orchestrator
    patterns = orchestrator.memory_manager.get_patterns()

    if not patterns:
        st.info("No patterns learned yet. Execute some goals to start learning!")
        return

    st.write(f"Found **{len(patterns)}** learned patterns")

    all_types = sorted(set(p.pattern_type for p in patterns))
    pattern_type = st.selectbox("Filter by type", ["All"] + all_types)

    filtered = patterns if pattern_type == "All" else [
        p for p in patterns if p.pattern_type == pattern_type
    ]

    for pattern in filtered[:20]:
        with st.expander(
            f"{pattern.pattern_type} — Confidence: {pattern.confidence:.2f}"
        ):
            st.write(f"**Outcome:** {pattern.outcome}")
            st.write(f"**Context:** {pattern.context}")
            st.write(f"**Usage Count:** {pattern.usage_count}")


if __name__ == "__main__":
    main()
