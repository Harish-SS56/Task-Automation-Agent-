"""
Task Orchestrator - Coordinates all agents and manages the execution workflow.
"""

from datetime import datetime
from typing import Any, Callable, Dict, Optional

from ..agents.adaptation_agent import AdaptationAgent
from ..agents.executor_agent import ExecutorAgent
from ..agents.goal_decomposer import GoalDecomposerAgent
from ..agents.human_interface_agent import HumanInterfaceAgent
from ..agents.planner_agent import PlannerAgent
from ..agents.reasoning_agent import ReasoningAgent
from ..models import (
    ExecutionPlan,
    ExecutionResult,
    GoalSession,
    HumanInputRequest,
    TaskStatus,
)
from .memory_manager import MemoryManager
from .progress_tracker import ProgressTracker
from .tool_registry import ToolRegistry


class TaskOrchestrator:
    """Orchestrates the execution of goals using all agents."""

    def __init__(
        self,
        base_path: str = ".",
        human_input_callback: Optional[Callable[[HumanInputRequest], Any]] = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            base_path: Base path for file operations
            human_input_callback: Optional callback for handling human input requests
        """
        self.tool_registry = ToolRegistry(base_path=base_path)
        self.memory_manager = MemoryManager()
        self.progress_tracker = ProgressTracker()

        # Initialize agents
        self.goal_decomposer = GoalDecomposerAgent()
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent(tool_registry=self.tool_registry)
        self.adaptation_agent = AdaptationAgent()
        self.human_interface = HumanInterfaceAgent()
        self.reasoning_agent = ReasoningAgent()

        self.human_input_callback = human_input_callback
        self.pending_human_inputs: Dict[str, HumanInputRequest] = {}
        self._current_session = None  # tracks the most recent GoalSession

    def execute_goal(
        self, goal_description: str, context: Dict[str, Any] = None
    ) -> GoalSession:
        """
        Execute a goal from start to finish.

        Args:
            goal_description: Natural language description of the goal
            context: Optional context information

        Returns:
            GoalSession with complete execution results
        """
        # Step 1: Decompose goal
        goal = self.goal_decomposer.decompose_goal(goal_description, context)
        goal.status = TaskStatus.IN_PROGRESS
        goal.started_at = datetime.now()

        # Step 2: Create execution plan
        learned_patterns = self.memory_manager.get_patterns()
        patterns_dict = [p.dict() for p in learned_patterns]
        execution_plan = self.planner.create_plan(goal, patterns_dict)

        # Step 3: Create session
        session = GoalSession(id=goal.id, goal=goal, execution_plan=execution_plan)
        self._current_session = session  # make available for human input lookups

        self.progress_tracker.start_goal(goal.id)

        # Step 4: Execute tasks
        execution_results = self._execute_plan(execution_plan, session)
        session.results = execution_results

        # Step 5: Adapt and learn
        adaptation_update = self.adaptation_agent.analyze_and_adapt(
            goal, execution_results, learned_patterns
        )
        session.adaptations.append(adaptation_update)

        # Save learned patterns
        self.memory_manager.save_patterns(adaptation_update.patterns_learned)

        # Step 6: Update goal status
        all_completed = all(
            t.status == TaskStatus.COMPLETED for t in execution_plan.tasks
        )
        all_failed = all(t.status == TaskStatus.FAILED for t in execution_plan.tasks)

        if all_completed:
            goal.status = TaskStatus.COMPLETED
            goal.result = {"success": True, "tasks_completed": len(execution_results)}
        elif all_failed:
            goal.status = TaskStatus.FAILED
            goal.result = {"success": False, "tasks_failed": len(execution_results)}
        else:
            goal.status = TaskStatus.IN_PROGRESS

        goal.completed_at = datetime.now()
        session.completed_at = datetime.now()

        # Step 7: Save session
        self.memory_manager.save_session(session)

        return session

    def _execute_plan(
        self, execution_plan: ExecutionPlan, session: GoalSession
    ) -> list[ExecutionResult]:
        """Execute all tasks in the plan."""
        results = []
        task_map = {task.id: task for task in execution_plan.tasks}

        # Execute tasks in order, respecting dependencies and parallel groups
        executed_tasks = set()

        # Process parallel groups first
        for group in execution_plan.parallel_groups:
            # Execute tasks in parallel group
            for task_id in group:
                if task_id in task_map:
                    task = task_map[task_id]
                    if self._can_execute_task(task, executed_tasks):
                        result = self._execute_task_with_checks(task, session)
                        results.append(result)
                        executed_tasks.add(task_id)

        # Execute remaining tasks sequentially
        for task in execution_plan.tasks:
            if task.id not in executed_tasks:
                if self._can_execute_task(task, executed_tasks):
                    result = self._execute_task_with_checks(task, session)
                    results.append(result)
                    executed_tasks.add(task.id)

        return results

    def _can_execute_task(self, task, executed_tasks: set) -> bool:
        """Check if a task can be executed (dependencies satisfied)."""
        if not task.dependencies:
            return True

        return all(dep_id in executed_tasks for dep_id in task.dependencies)

    def _execute_task_with_checks(self, task, session: GoalSession) -> ExecutionResult:
        """Execute a task with human interface checks."""
        # Check if human input is needed
        if self.human_interface.should_escalate(task):
            request = self.human_interface.create_input_request(
                session.goal, task, "This task requires human confirmation or input"
            )

            session.human_inputs.append(request)
            self.pending_human_inputs[request.id] = request

            # If we have a callback, use it
            if self.human_input_callback:
                response = self.human_input_callback(request)
                processed = self.human_interface.process_human_response(
                    request, response
                )

                if not processed.get("success"):
                    # Human declined or invalid response
                    task.status = TaskStatus.FAILED
                    task.error = "Human input required but not provided"
                    return ExecutionResult(
                        task_id=task.id,
                        success=False,
                        error="Human input required",
                        execution_time=0.0,
                    )
            else:
                # No callback - mark as waiting
                task.status = TaskStatus.WAITING_FOR_HUMAN
                return ExecutionResult(
                    task_id=task.id,
                    success=False,
                    error="Waiting for human input",
                    execution_time=0.0,
                )

        # Execute the task
        self.progress_tracker.start_task(task.id)
        result = self.executor.execute_task(task)

        return result

    def provide_human_input(self, request_id: str, response: Any) -> Dict[str, Any]:
        """
        Provide human input for a pending request.

        Args:
            request_id: ID of the request
            response: Human's response

        Returns:
            Result dictionary
        """
        if request_id not in self.pending_human_inputs:
            return {"success": False, "error": f"Request {request_id} not found"}

        request = self.pending_human_inputs[request_id]
        processed = self.human_interface.process_human_response(request, response)

        if processed.get("success"):
            # Remove from pending now that it's resolved
            del self.pending_human_inputs[request_id]

            # Try to find and retry the task from the current session
            task = None
            if self._current_session and request.task_id:
                for t in self._current_session.execution_plan.tasks:
                    if t.id == request.task_id:
                        task = t
                        break

            if task:
                task.status = TaskStatus.PENDING
                result = self.executor.execute_task(task)
                return {"success": True, "execution_result": result.dict()}

            return {"success": True, "message": "Input received"}

        return processed

    def get_progress(self, goal_id: str) -> Dict[str, Any]:
        """
        Get progress for a goal.

        Args:
            goal_id: ID of the goal

        Returns:
            Progress information
        """
        # This would need to load the session
        # For now, return basic info
        return {"goal_id": goal_id, "status": "in_progress"}

    def use_reasoning(self, problem: str, context: Dict[str, Any] = None):
        """
        Use reasoning agent to solve a complex problem.

        Args:
            problem: Problem to solve
            context: Additional context

        Returns:
            ReasoningResult
        """
        return self.reasoning_agent.reason(problem, context)
