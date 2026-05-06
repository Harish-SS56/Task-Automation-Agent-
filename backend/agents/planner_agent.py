"""
Planner Agent - Creates optimal execution plans from task breakdowns.
Implements Planning, Prioritization, and Reasoning patterns.
"""

import json
from typing import Any, Dict, List

from ..models import ExecutionPlan, Goal, TaskPriority
from .base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Agent that creates execution plans from task breakdowns."""

    def __init__(self):
        super().__init__(temperature=0.2)

    def create_plan(
        self, goal: Goal, learned_patterns: List[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """
        Create an execution plan from a goal's tasks.

        Args:
            goal: Goal with decomposed tasks
            learned_patterns: Optional patterns learned from past executions

        Returns:
            ExecutionPlan with ordered tasks and parallel groups
        """
        self.log(f"Creating execution plan for goal: {goal.description}")

        prompt = self._create_planning_prompt(goal, learned_patterns)
        response = self._call_llm(prompt)

        try:
            plan_data = self._parse_json_response(response)
            plan = self._create_plan_from_response(goal, plan_data)

            self.log(
                f"Created plan with {len(plan.tasks)} tasks in {len(plan.parallel_groups)} parallel groups"
            )
            return plan

        except Exception as e:
            self.log(f"Error creating plan: {str(e)}", "ERROR")
            # Fallback: simple sequential plan
            return self._create_fallback_plan(goal)

    def _create_planning_prompt(
        self, goal: Goal, learned_patterns: List[Dict[str, Any]] = None
    ) -> str:
        """Create the prompt for planning."""
        tasks_json = []
        for task in goal.tasks:
            tasks_json.append(
                {
                    "id": task.id,
                    "description": task.description,
                    "priority": task.priority.value,
                    "dependencies": task.dependencies,
                    "tool": task.tool,
                }
            )

        patterns_str = ""
        if learned_patterns:
            patterns_str = f"\n\nLearned Patterns from Past Executions:\n{json.dumps(learned_patterns, indent=2, default=str)}"

        return f"""You are an expert at creating optimal execution plans for task automation.

Your job is to analyze a set of tasks and create an efficient execution plan that:
1. Respects task dependencies
2. Identifies opportunities for parallel execution
3. Orders tasks by priority
4. Optimizes for efficiency and resource usage

Goal: {goal.description}

Tasks to plan:
{json.dumps(tasks_json, indent=2, default=str)}{patterns_str}

Analyze these tasks and create an execution plan. Consider:
- What are the dependencies between tasks?
- Which tasks can be executed in parallel?
- What is the optimal order considering priorities and dependencies?
- Are there any learned patterns that suggest better approaches?

Return your response as a JSON object with this structure:
{{
    "task_order": ["task_id_1", "task_id_2", ...],
    "parallel_groups": [
        ["task_id_1", "task_id_2"],
        ["task_id_3"]
    ],
    "reasoning": "Explanation of the planning strategy",
    "estimated_duration_minutes": 10.5
}}

The parallel_groups array should contain groups of task IDs that can be executed simultaneously. Tasks in the same group have no dependencies on each other."""

    def _create_plan_from_response(
        self, goal: Goal, plan_data: Dict[str, Any]
    ) -> ExecutionPlan:
        """Create an ExecutionPlan from the planning response."""
        # Create a map of task IDs to tasks
        task_map = {task.id: task for task in goal.tasks}

        # Update task order if provided
        ordered_tasks = []
        if "task_order" in plan_data:
            for task_id in plan_data["task_order"]:
                if task_id in task_map:
                    ordered_tasks.append(task_map[task_id])
        else:
            # Use original order if no order specified
            ordered_tasks = goal.tasks

        # Add any tasks not in the order
        for task in goal.tasks:
            if task not in ordered_tasks:
                ordered_tasks.append(task)

        # Extract parallel groups
        parallel_groups = plan_data.get("parallel_groups", [])

        # Validate parallel groups contain valid task IDs
        valid_parallel_groups = []
        for group in parallel_groups:
            valid_group = [tid for tid in group if tid in task_map]
            if valid_group:
                valid_parallel_groups.append(valid_group)

        plan = ExecutionPlan(
            goal_id=goal.id,
            tasks=ordered_tasks,
            parallel_groups=valid_parallel_groups,
            estimated_duration=plan_data.get("estimated_duration_minutes"),
        )

        return plan

    def _create_fallback_plan(self, goal: Goal) -> ExecutionPlan:
        """Create a simple sequential fallback plan."""
        # Sort by priority (critical -> high -> medium -> low)
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }

        sorted_tasks = sorted(
            goal.tasks, key=lambda t: priority_order.get(t.priority, 2)
        )

        return ExecutionPlan(
            goal_id=goal.id,
            tasks=sorted_tasks,
            parallel_groups=[],
            estimated_duration=None,
        )
