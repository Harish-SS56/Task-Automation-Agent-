"""
Reasoning Agent - Solves complex problems using chain-of-thought reasoning.
Implements Reasoning and Reflection patterns.
"""

import json
from typing import Any, Dict

from ..models import ReasoningResult, ReasoningStep
from .base_agent import BaseAgent


class ReasoningAgent(BaseAgent):
    """Agent that uses chain-of-thought reasoning to solve complex problems."""

    def __init__(self):
        super().__init__(temperature=0.3)

    def reason(self, problem: str, context: Dict[str, Any] = None) -> ReasoningResult:
        """
        Solve a complex problem using chain-of-thought reasoning.

        Args:
            problem: Problem to solve
            context: Additional context information

        Returns:
            ReasoningResult with reasoning steps and solution
        """
        self.log(f"Reasoning about problem: {problem[:100]}...")

        prompt = self._create_reasoning_prompt(problem, context)
        response = self._call_llm(prompt)

        try:
            reasoning_data = self._parse_json_response(response)
            result = self._create_reasoning_result(problem, reasoning_data)

            self.log(f"Generated reasoning with {len(result.steps)} steps")
            return result

        except Exception as e:
            self.log(f"Error in reasoning: {str(e)}", "ERROR")
            # Fallback: simple reasoning result
            return self._create_fallback_result(problem)

    def _create_reasoning_prompt(
        self, problem: str, context: Dict[str, Any] = None
    ) -> str:
        """Create prompt for chain-of-thought reasoning."""
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2, default=str)}"

        return f"""You are an expert problem solver. Use chain-of-thought reasoning to solve the following problem step by step.

Problem: {problem}{context_str}

Think through this problem systematically:
1. Break down the problem into smaller parts
2. Analyze each part carefully
3. Consider multiple approaches
4. Evaluate the pros and cons of each approach
5. Choose the best solution
6. Explain your reasoning at each step

Return your reasoning as a JSON object:
{{
    "steps": [
        {{
            "step_number": 1,
            "thought": "What I'm thinking about in this step",
            "conclusion": "What I conclude from this step"
        }}
    ],
    "final_solution": "The final solution or recommendation",
    "confidence": 0.0-1.0,
    "alternatives_considered": ["alternative 1", "alternative 2"]
}}

Be thorough and show your reasoning process clearly."""

    def _create_reasoning_result(
        self, problem: str, reasoning_data: Dict[str, Any]
    ) -> ReasoningResult:
        """Create ReasoningResult from LLM response."""
        steps = []
        if "steps" in reasoning_data:
            for step_data in reasoning_data["steps"]:
                step = ReasoningStep(
                    step_number=step_data.get("step_number", len(steps) + 1),
                    thought=step_data.get("thought", ""),
                    conclusion=step_data.get("conclusion"),
                )
                steps.append(step)

        # If no steps provided, create a single step from the response
        if not steps:
            steps.append(
                ReasoningStep(
                    step_number=1,
                    thought=reasoning_data.get("reasoning", "Analyzed the problem"),
                    conclusion=reasoning_data.get("final_solution"),
                )
            )

        result = ReasoningResult(
            problem=problem,
            steps=steps,
            final_solution=reasoning_data.get("final_solution", "No solution found"),
            confidence=reasoning_data.get("confidence", 0.5),
            alternatives_considered=reasoning_data.get("alternatives_considered", []),
        )

        return result

    def _create_fallback_result(self, problem: str) -> ReasoningResult:
        """Create a fallback reasoning result."""
        return ReasoningResult(
            problem=problem,
            steps=[
                ReasoningStep(
                    step_number=1,
                    thought="Analyzing the problem",
                    conclusion="Unable to complete full reasoning analysis",
                )
            ],
            final_solution="Manual review recommended",
            confidence=0.3,
            alternatives_considered=[],
        )
