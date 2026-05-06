"""
Goal Decomposer Agent - Breaks down high-level goals into actionable tasks.
Implements Goal Setting and Planning patterns.
"""

import json
import uuid
from typing import Any, Dict, List

from ..models import Goal, Task, TaskPriority
from .base_agent import BaseAgent


class GoalDecomposerAgent(BaseAgent):
    """Agent that decomposes high-level goals into actionable tasks."""

    def __init__(self):
        super().__init__(temperature=0.3)

    def decompose_goal(
        self, goal_description: str, context: Dict[str, Any] = None
    ) -> Goal:
        """
        Break down a high-level goal into actionable tasks.

        Args:
            goal_description: Natural language description of the goal
            context: Optional context information

        Returns:
            Goal object with decomposed tasks
        """
        self.log(f"Decomposing goal: {goal_description}")

        prompt = self._create_decomposition_prompt(goal_description, context)
        response = self._call_llm(prompt)

        try:
            decomposition = self._parse_json_response(response)
            tasks = self._create_tasks_from_decomposition(decomposition)

            goal = Goal(id=str(uuid.uuid4()), description=goal_description, tasks=tasks)

            self.log(f"Goal decomposed into {len(tasks)} tasks")
            return goal

        except Exception as e:
            self.log(f"Error decomposing goal: {str(e)}", "ERROR")
            # Fallback: create a single task for the entire goal
            return self._create_fallback_goal(goal_description)

    def _create_decomposition_prompt(
        self, goal_description: str, context: Dict[str, Any] = None
    ) -> str:
        """Create the prompt for goal decomposition."""
        context_str = ""
        if context:
            context_str = f"\n\nContext: {json.dumps(context, indent=2, default=str)}"

        return f"""You are an expert at breaking down high-level goals into actionable, specific tasks.

Your job is to analyze a goal and decompose it into a series of concrete, executable tasks. Each task should:
1. Be specific and actionable
2. Have clear dependencies (what must be done first)
3. Have an appropriate priority level
4. Specify what tool or action is needed

Goal to decompose: {goal_description}{context_str}

Analyze this goal and break it down into tasks. Consider:
- What are the logical steps to achieve this goal?
- What dependencies exist between tasks?
- Which tasks can be done in parallel?
- What tools or operations are needed for each task?

Return your response as a JSON object with this structure:
{{
    "tasks": [
        {{
            "description": "Clear description of what needs to be done",
            "priority": "low|medium|high|critical",
            "dependencies": ["task_id_1", "task_id_2"],
            "tool": "file_operations|git_operations|command_executor|web_operations",
            "tool_params": {{"key": "value"}}
        }}
    ],
    "reasoning": "Brief explanation of the decomposition strategy"
}}

Make sure each task is specific enough to be executed independently. Think about the order of operations and dependencies carefully."""

    def _create_tasks_from_decomposition(
        self, decomposition: Dict[str, Any]
    ) -> List[Task]:
        """Create Task objects from the decomposition response."""
        tasks = []
        task_map = {}  # For handling dependencies

        if "tasks" not in decomposition:
            raise ValueError("Decomposition must include 'tasks' array")

        # First pass: create all tasks
        for idx, task_data in enumerate(decomposition["tasks"]):
            task_id = str(uuid.uuid4())

            # Map description-based dependencies to IDs
            if "dependencies" in task_data:
                # Store original dependencies for second pass
                task_data["_original_deps"] = task_data["dependencies"]

            task = Task(
                id=task_id,
                description=task_data.get("description", f"Task {idx + 1}"),
                priority=TaskPriority(task_data.get("priority", "medium")),
                tool=task_data.get("tool"),
                tool_params=task_data.get("tool_params", {}),
            )

            tasks.append(task)
            task_map[task_id] = task

        # Second pass: resolve dependencies
        for idx, task_data in enumerate(decomposition["tasks"]):
            if "_original_deps" in task_data:
                # For now, we'll use description matching or index-based dependencies
                # In a more sophisticated system, we'd use better dependency resolution
                deps = task_data["_original_deps"]
                if isinstance(deps, list) and len(deps) > 0:
                    # Simple approach: use previous tasks as dependencies if specified
                    # In production, you'd want more sophisticated dependency resolution
                    pass

        return tasks

    def _create_fallback_goal(self, goal_description: str) -> Goal:
        """Create a fallback goal with a single task."""
        task = Task(
            id=str(uuid.uuid4()),
            description=goal_description,
            priority=TaskPriority.MEDIUM,
        )

        return Goal(id=str(uuid.uuid4()), description=goal_description, tasks=[task])
