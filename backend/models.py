"""
Data models for the Task Automation Agent system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING_FOR_HUMAN = "waiting_for_human"


class TaskPriority(str, Enum):
    """Priority level of a task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Represents a single task in the execution plan."""

    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = Field(default_factory=list)
    tool: Optional[str] = None
    tool_params: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


class Goal(BaseModel):
    """Represents a high-level goal."""

    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    tasks: List[Task] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    requires_human_input: bool = False
    human_input: Optional[Dict[str, Any]] = None


class ExecutionPlan(BaseModel):
    """Represents an execution plan for a goal."""

    goal_id: str
    tasks: List[Task]
    parallel_groups: List[List[str]] = Field(default_factory=list)
    estimated_duration: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)


class ExecutionResult(BaseModel):
    """Result of executing a task."""

    task_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearnedPattern(BaseModel):
    """A pattern learned from past executions."""

    id: str
    pattern_type: str  # e.g., "successful_approach", "failed_approach"
    context: Dict[str, Any]
    outcome: str
    confidence: float = 0.0
    usage_count: int = 0
    last_used: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)


class AdaptationUpdate(BaseModel):
    """Update from the Adaptation Agent."""

    goal_id: str
    patterns_learned: List[LearnedPattern] = Field(default_factory=list)
    strategies_updated: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class HumanInputRequest(BaseModel):
    """Request for human input."""

    id: str
    goal_id: str
    task_id: Optional[str] = None
    question: str
    options: Optional[List[str]] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    resolved: bool = False
    response: Optional[Any] = None


class ReasoningStep(BaseModel):
    """A single step in chain-of-thought reasoning."""

    step_number: int
    thought: str
    conclusion: Optional[str] = None


class ReasoningResult(BaseModel):
    """Result of reasoning process."""

    problem: str
    steps: List[ReasoningStep]
    final_solution: str
    confidence: float
    alternatives_considered: List[str] = Field(default_factory=list)


class GoalSession(BaseModel):
    """A complete session of goal execution."""

    id: str
    goal: Goal
    execution_plan: ExecutionPlan
    results: List[ExecutionResult] = Field(default_factory=list)
    adaptations: List[AdaptationUpdate] = Field(default_factory=list)
    human_inputs: List[HumanInputRequest] = Field(default_factory=list)
    reasoning_results: List[ReasoningResult] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
