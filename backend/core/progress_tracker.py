"""
Progress Tracker - Tracks execution progress and provides status updates.
"""

from datetime import datetime
from typing import Any, Dict, List

from ..models import ExecutionPlan, Goal, TaskStatus


class ProgressTracker:
    """Tracks progress of goal execution."""

    def __init__(self):
        self.start_time: Dict[str, datetime] = {}
        self.task_start_times: Dict[str, datetime] = {}

    def start_goal(self, goal_id: str):
        """Mark goal execution as started."""
        self.start_time[goal_id] = datetime.now()

    def start_task(self, task_id: str):
        """Mark task execution as started."""
        self.task_start_times[task_id] = datetime.now()

    def get_progress(self, goal: Goal, execution_plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Get current progress for a goal.

        Args:
            goal: The goal being tracked
            execution_plan: The execution plan

        Returns:
            Progress information dictionary
        """
        total_tasks = len(execution_plan.tasks)
        completed_tasks = sum(
            1 for t in execution_plan.tasks if t.status == TaskStatus.COMPLETED
        )
        failed_tasks = sum(
            1 for t in execution_plan.tasks if t.status == TaskStatus.FAILED
        )
        in_progress_tasks = sum(
            1 for t in execution_plan.tasks if t.status == TaskStatus.IN_PROGRESS
        )
        pending_tasks = sum(
            1 for t in execution_plan.tasks if t.status == TaskStatus.PENDING
        )

        completion_percentage = (
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        )

        elapsed_time = None
        if goal.id in self.start_time:
            elapsed = datetime.now() - self.start_time[goal.id]
            elapsed_time = elapsed.total_seconds()

        estimated_remaining = None
        if execution_plan.estimated_duration and elapsed_time:
            estimated_remaining = max(
                0, execution_plan.estimated_duration * 60 - elapsed_time
            )

        return {
            "goal_id": goal.id,
            "goal_status": goal.status.value,
            "total_tasks": total_tasks,
            "completed": completed_tasks,
            "failed": failed_tasks,
            "in_progress": in_progress_tasks,
            "pending": pending_tasks,
            "completion_percentage": completion_percentage,
            "elapsed_time_seconds": elapsed_time,
            "estimated_remaining_seconds": estimated_remaining,
            "success_rate": (completed_tasks / total_tasks * 100)
            if total_tasks > 0
            else 0,
        }

    def get_task_status_summary(
        self, execution_plan: ExecutionPlan
    ) -> List[Dict[str, Any]]:
        """
        Get status summary for all tasks.

        Args:
            execution_plan: The execution plan

        Returns:
            List of task status dictionaries
        """
        summary = []
        for task in execution_plan.tasks:
            task_info = {
                "id": task.id,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "retry_count": task.retry_count,
            }

            if task.started_at:
                task_info["started_at"] = task.started_at.isoformat()
            if task.completed_at:
                task_info["completed_at"] = task.completed_at.isoformat()
            if task.error:
                task_info["error"] = task.error

            summary.append(task_info)

        return summary
