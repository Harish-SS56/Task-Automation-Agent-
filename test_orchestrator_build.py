from dotenv import load_dotenv
from backend.core.orchestrator import TaskOrchestrator

load_dotenv()


def test_orchestrator_build():
    print("Initializing TaskOrchestrator...")
    try:
        orchestrator = TaskOrchestrator(base_path=".")
        print("TaskOrchestrator initialized successfully.")

        # Verify agents are initialized
        print("Agents initialized:")
        print(f" - Goal Decomposer: {orchestrator.goal_decomposer}")
        print(f" - Planner: {orchestrator.planner}")
        print(f" - Executor: {orchestrator.executor}")
        print(f" - Adaptation: {orchestrator.adaptation_agent}")
        print(f" - Human Interface: {orchestrator.human_interface}")
        print(f" - Reasoning: {orchestrator.reasoning_agent}")

    except Exception as e:
        print(f"TaskOrchestrator build test failed: {e}")
        raise


if __name__ == "__main__":
    test_orchestrator_build()
