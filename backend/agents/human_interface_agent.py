"""
Human Interface Agent - Manages human interaction and escalation.
Implements Human-in-the-Loop and Routing patterns.

ESCALATION POLICY (conservative):
- Only escalate for truly destructive operations (delete, wipe, format, etc.)
- Ambiguous / multiple-approaches checks are done without LLM calls to save quota
  and to avoid incorrectly escalating routine setup tasks.
"""

import uuid
from typing import Any, Dict, List, Optional

from ..models import Goal, HumanInputRequest, Task
from .base_agent import BaseAgent


class HumanInterfaceAgent(BaseAgent):
    """Agent that manages human interaction and escalation."""

    def __init__(self):
        super().__init__(temperature=0.2)

    def should_escalate(self, task: Task, context: Dict[str, Any] = None) -> bool:
        """
        Determine if a task requires human input.

        Only escalates for genuinely destructive operations so that routine
        tasks (create directory, install packages, write files, etc.) run
        autonomously without interrupting the user.

        Args:
            task: Task to evaluate
            context: Additional context

        Returns:
            True if human input is needed
        """
        # Only stop for destructive operations that could cause data loss
        if self._is_destructive_operation(task):
            return True

        # Honour explicit escalation flags from context
        if context and context.get("requires_confirmation", False):
            return True

        # NOTE: _is_ambiguous and _has_multiple_approaches are intentionally
        # NOT called here because:
        #   1. They call the LLM for every task → burns API quota fast.
        #   2. The LLM almost always says "yes" for generic tasks, causing
        #      every single task to pause for human confirmation.
        return False

    def create_input_request(
        self,
        goal: Goal,
        task: Optional[Task],
        reason: str,
        options: Optional[List[str]] = None,
        context: Dict[str, Any] = None,
    ) -> HumanInputRequest:
        """
        Create a human input request.

        Args:
            goal: The goal being executed
            task: Optional task that triggered the request
            reason: Reason for requesting input
            options: Optional list of choices
            context: Additional context

        Returns:
            HumanInputRequest object
        """
        question = self._generate_question(goal, task, reason, options)

        request = HumanInputRequest(
            id=str(uuid.uuid4()),
            goal_id=goal.id,
            task_id=task.id if task else None,
            question=question,
            options=options,
            context=context or {},
        )

        self.log(f"Created human input request: {question[:80]}")
        return request

    def _is_destructive_operation(self, task: Task) -> bool:
        """Check if task involves destructive operations that risk data loss."""
        destructive_keywords = [
            "delete",
            "remove",
            "drop",
            "destroy",
            "clear",
            "uninstall",
            "format",
            "wipe",
            "truncate",
            "overwrite",
            "rm -rf",
        ]
        description_lower = task.description.lower()
        return any(keyword in description_lower for keyword in destructive_keywords)

    def _is_ambiguous(self, task: Task) -> bool:
        """
        Check if task requirements are ambiguous.
        Uses keyword matching only — NO LLM call to avoid quota usage.
        """
        ambiguous_indicators = [
            "maybe",
            "perhaps",
            "not sure",
            "unclear",
            "vague",
        ]
        description_lower = task.description.lower()
        return any(indicator in description_lower for indicator in ambiguous_indicators)

    def _has_multiple_approaches(self, task: Task) -> bool:
        """
        Deliberately returns False.

        Calling the LLM for every task to check for multiple approaches burns
        API quota and almost always returns True (since most tasks have more
        than one way to do them), causing every task to require human input.
        """
        return False

    def _generate_question(
        self,
        goal: Goal,
        task: Optional[Task],
        reason: str,
        options: Optional[List[str]] = None,
    ) -> str:
        """Generate a clear question for human input."""
        if task:
            base_question = f"Task: {task.description}\n\n{reason}\n\n"
        else:
            base_question = f"Goal: {goal.description}\n\n{reason}\n\n"

        if options:
            base_question += "Please choose one of the following options:\n"
            for idx, option in enumerate(options, 1):
                base_question += f"{idx}. {option}\n"
        else:
            base_question += "Please provide your input:"

        return base_question

    def process_human_response(
        self, request: HumanInputRequest, response: Any
    ) -> Dict[str, Any]:
        """
        Process human response to an input request.

        Args:
            request: The original request
            response: Human's response

        Returns:
            Processed response dictionary
        """
        request.resolved = True
        request.response = response

        # Validate response if options were provided
        if request.options:
            if isinstance(response, int) and 1 <= response <= len(request.options):
                selected_option = request.options[response - 1]
                return {
                    "success": True,
                    "selected_option": selected_option,
                    "index": response - 1,
                }
            elif isinstance(response, str) and response in request.options:
                return {"success": True, "selected_option": response}
            else:
                # Treat any non-empty response as confirmation when options exist
                if response:
                    return {"success": True, "selected_option": request.options[0]}
                return {
                    "success": False,
                    "error": "Invalid response. Please select from the provided options.",
                }

        return {"success": True, "response": response}
