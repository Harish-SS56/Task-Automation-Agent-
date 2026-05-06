"""
Adaptation Agent - Learns from execution outcomes and improves strategies.
Implements Adaptation, Memory, and Reflection patterns.
"""

import json
from datetime import datetime
from typing import List

from ..models import AdaptationUpdate, ExecutionResult, Goal, LearnedPattern
from .base_agent import BaseAgent


class AdaptationAgent(BaseAgent):
    """Agent that learns from outcomes and adapts strategies."""

    def __init__(self):
        super().__init__(temperature=0.3)

    def analyze_and_adapt(
        self,
        goal: Goal,
        execution_results: List[ExecutionResult],
        previous_patterns: List[LearnedPattern] = None,
    ) -> AdaptationUpdate:
        """
        Analyze execution results and generate adaptation updates.

        Args:
            goal: The goal that was executed
            execution_results: Results from task executions
            previous_patterns: Previously learned patterns

        Returns:
            AdaptationUpdate with learned patterns and recommendations
        """
        self.log(f"Analyzing execution results for goal: {goal.description}")

        # Analyze outcomes
        _ = self._calculate_success_rate(execution_results)
        patterns = self._identify_patterns(goal, execution_results, previous_patterns)
        recommendations = self._generate_recommendations(
            goal, execution_results, patterns
        )

        # Create adaptation update
        update = AdaptationUpdate(
            goal_id=goal.id, patterns_learned=patterns, recommendations=recommendations
        )

        self.log(
            f"Identified {len(patterns)} new patterns and {len(recommendations)} recommendations"
        )

        return update

    def _calculate_success_rate(self, results: List[ExecutionResult]) -> float:
        """Calculate the success rate of executions."""
        if not results:
            return 0.0

        successful = sum(1 for r in results if r.success)
        return successful / len(results)

    def _identify_patterns(
        self,
        goal: Goal,
        results: List[ExecutionResult],
        previous_patterns: List[LearnedPattern] = None,
    ) -> List[LearnedPattern]:
        """
        Identify patterns from execution results.

        Args:
            goal: The executed goal
            results: Execution results
            previous_patterns: Previously learned patterns

        Returns:
            List of learned patterns
        """
        patterns = []

        # Analyze successful tasks
        successful_tasks = [r for r in results if r.success]
        if successful_tasks:
            # Identify what made these successful
            pattern = LearnedPattern(
                id=f"pattern_{datetime.now().timestamp()}",
                pattern_type="successful_approach",
                context={
                    "goal_type": goal.description,
                    "successful_tasks": len(successful_tasks),
                    "total_tasks": len(results),
                },
                outcome="success",
                confidence=len(successful_tasks) / len(results) if results else 0.0,
                usage_count=1,
                last_used=datetime.now(),
            )
            patterns.append(pattern)

        # Analyze failed tasks
        failed_tasks = [r for r in results if not r.success]
        if failed_tasks:
            # Identify common failure patterns
            common_errors = {}
            for result in failed_tasks:
                error = result.error or "Unknown error"
                common_errors[error] = common_errors.get(error, 0) + 1

            for error, count in common_errors.items():
                pattern = LearnedPattern(
                    id=f"pattern_{datetime.now().timestamp()}_{len(patterns)}",
                    pattern_type="failed_approach",
                    context={
                        "goal_type": goal.description,
                        "error": error,
                        "occurrences": count,
                    },
                    outcome="failure",
                    confidence=count / len(failed_tasks),
                    usage_count=1,
                    last_used=datetime.now(),
                )
                patterns.append(pattern)

        # Use LLM to identify more sophisticated patterns
        if results:
            llm_patterns = self._identify_patterns_with_llm(goal, results)
            patterns.extend(llm_patterns)

        return patterns

    def _identify_patterns_with_llm(
        self, goal: Goal, results: List[ExecutionResult]
    ) -> List[LearnedPattern]:
        """Use LLM to identify patterns in execution results."""
        try:
            prompt = self._create_pattern_analysis_prompt(goal, results)
            response = self._call_llm(prompt)
            pattern_data = self._parse_json_response(response)

            patterns = []
            if "patterns" in pattern_data:
                for idx, p in enumerate(pattern_data["patterns"]):
                    pattern = LearnedPattern(
                        id=f"llm_pattern_{datetime.now().timestamp()}_{idx}",
                        pattern_type=p.get("type", "general"),
                        context=p.get("context", {}),
                        outcome=p.get("outcome", "unknown"),
                        confidence=p.get("confidence", 0.5),
                        usage_count=1,
                        last_used=datetime.now(),
                    )
                    patterns.append(pattern)

            return patterns

        except Exception as e:
            self.log(f"Error identifying patterns with LLM: {str(e)}", "ERROR")
            return []

    def _create_pattern_analysis_prompt(
        self, goal: Goal, results: List[ExecutionResult]
    ) -> str:
        """Create prompt for pattern analysis."""
        results_summary = []
        for result in results:
            results_summary.append(
                {
                    "success": result.success,
                    "error": result.error,
                    "execution_time": result.execution_time,
                }
            )

        return f"""Analyze the execution results and identify patterns that could help improve future goal execution.

Goal: {goal.description}

Execution Results:
{json.dumps(results_summary, indent=2, default=str)}

Identify patterns such as:
- What approaches led to success?
- What common errors occurred?
- What could be done differently?
- What strategies work well for this type of goal?

Return your analysis as JSON:
{{
    "patterns": [
        {{
            "type": "successful_approach|failed_approach|optimization",
            "context": {{"key": "value"}},
            "outcome": "success|failure|improvement",
            "confidence": 0.0-1.0,
            "insight": "What this pattern teaches us"
        }}
    ],
    "summary": "Overall analysis summary"
}}"""

    def _generate_recommendations(
        self, goal: Goal, results: List[ExecutionResult], patterns: List[LearnedPattern]
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check success rate
        success_rate = self._calculate_success_rate(results)
        if success_rate < 0.5:
            recommendations.append(
                "Consider breaking down the goal into smaller, more manageable tasks"
            )

        # Check for common errors
        failed_results = [r for r in results if not r.success]
        if failed_results:
            common_error = max(
                set(r.error for r in failed_results if r.error),
                key=lambda e: sum(1 for r in failed_results if r.error == e),
                default=None,
            )
            if common_error:
                recommendations.append(f"Address common error: {common_error}")

        # Check execution time
        avg_time = (
            sum(r.execution_time for r in results) / len(results) if results else 0
        )
        if avg_time > 30:
            recommendations.append(
                "Consider optimizing tasks that take longer than 30 seconds"
            )

        return recommendations
