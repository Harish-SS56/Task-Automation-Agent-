"""
Memory Manager - Manages storage and retrieval of learned patterns and session data.
Implements Memory pattern.
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..models import Goal, GoalSession, LearnedPattern


# ---------------------------------------------------------------------------
# JSON encoder that handles datetime, date, UUID and any Pydantic model
# ---------------------------------------------------------------------------
class _SafeEncoder(json.JSONEncoder):
    """Serialize types that the standard JSON encoder can't handle."""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        # Pydantic v1 models
        if hasattr(obj, "dict"):
            return obj.dict()
        # Pydantic v2 models
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return super().default(obj)


def _safe_dumps(data: Any, **kwargs) -> str:
    """json.dumps that handles datetime/UUID/Pydantic objects."""
    return json.dumps(data, cls=_SafeEncoder, **kwargs)


def _safe_dump(data: Any, fp, **kwargs) -> None:
    """json.dump that handles datetime/UUID/Pydantic objects."""
    json.dump(data, fp, cls=_SafeEncoder, **kwargs)


def _model_to_dict(obj: Any) -> Any:
    """Recursively convert Pydantic models and datetimes to JSON-safe types."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if hasattr(obj, "dict"):          # Pydantic v1
        return _model_to_dict(obj.dict())
    if hasattr(obj, "model_dump"):    # Pydantic v2
        return _model_to_dict(obj.model_dump())
    if isinstance(obj, dict):
        return {k: _model_to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_model_to_dict(i) for i in obj]
    return obj


class MemoryManager:
    """Manages memory storage and retrieval."""

    def __init__(
        self, memory_dir: str = "data/memory", sessions_dir: str = "data/sessions"
    ):
        """
        Initialize the memory manager.

        Args:
            memory_dir: Directory for storing learned patterns
            sessions_dir: Directory for storing goal sessions
        """
        self.memory_dir = Path(memory_dir)
        self.sessions_dir = Path(sessions_dir)

        # Create directories if they don't exist
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.memory_dir / "learned_patterns.json"
        self._patterns: List[LearnedPattern] = []
        self._load_patterns()

    def save_pattern(self, pattern: LearnedPattern):
        """Save a learned pattern to memory."""
        self._patterns.append(pattern)
        self._save_patterns()

    def save_patterns(self, patterns: List[LearnedPattern]):
        """Save multiple learned patterns."""
        self._patterns.extend(patterns)
        self._save_patterns()

    def get_patterns(
        self,
        pattern_type: Optional[str] = None,
        context_filter: Optional[Dict[str, Any]] = None,
    ) -> List[LearnedPattern]:
        """
        Retrieve learned patterns.

        Args:
            pattern_type: Filter by pattern type
            context_filter: Filter by context keys

        Returns:
            List of matching patterns
        """
        patterns = self._patterns

        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]

        if context_filter:
            filtered = []
            for pattern in patterns:
                match = True
                for key, value in context_filter.items():
                    if key not in pattern.context or pattern.context[key] != value:
                        match = False
                        break
                if match:
                    filtered.append(pattern)
            patterns = filtered

        # Sort by confidence and usage count
        patterns.sort(key=lambda p: (p.confidence, p.usage_count), reverse=True)

        return patterns

    def update_pattern_usage(self, pattern_id: str):
        """Update pattern usage statistics."""
        for pattern in self._patterns:
            if pattern.id == pattern_id:
                pattern.usage_count += 1
                pattern.last_used = datetime.now()
                self._save_patterns()
                break

    def save_session(self, session: GoalSession):
        """Save a goal session to disk."""
        session_file = self.sessions_dir / f"{session.id}.json"

        session_data = {
            "id": session.id,
            "goal": _model_to_dict(session.goal),
            "execution_plan": _model_to_dict(session.execution_plan),
            "results": [_model_to_dict(r) for r in session.results],
            "adaptations": [_model_to_dict(a) for a in session.adaptations],
            "human_inputs": [_model_to_dict(h) for h in session.human_inputs],
            "reasoning_results": [_model_to_dict(r) for r in session.reasoning_results],
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat()
            if session.completed_at
            else None,
        }

        with open(session_file, "w", encoding="utf-8") as f:
            _safe_dump(session_data, f, indent=2)

    def load_session(self, session_id: str) -> Optional[GoalSession]:
        """Load a goal session from disk."""
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            from ..models import ExecutionPlan, GoalSession

            goal = Goal(**session_data["goal"])
            execution_plan = ExecutionPlan(**session_data["execution_plan"])

            session = GoalSession(
                id=session_data["id"],
                goal=goal,
                execution_plan=execution_plan,
                started_at=datetime.fromisoformat(session_data["started_at"]),
                completed_at=datetime.fromisoformat(session_data["completed_at"])
                if session_data.get("completed_at")
                else None,
            )

            return session

        except Exception as e:
            print(f"Error loading session: {e}")
            return None

    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        session_files = list(self.sessions_dir.glob("*.json"))
        return [f.stem for f in session_files]

    def _load_patterns(self):
        """Load learned patterns from disk."""
        if not self.patterns_file.exists():
            return

        try:
            with open(self.patterns_file, "r", encoding="utf-8") as f:
                patterns_data = json.load(f)

            self._patterns = [LearnedPattern(**p) for p in patterns_data]

        except Exception as e:
            print(f"Error loading patterns: {e}")
            self._patterns = []

    def _save_patterns(self):
        """Save learned patterns to disk."""
        try:
            patterns_data = [_model_to_dict(p) for p in self._patterns]

            with open(self.patterns_file, "w", encoding="utf-8") as f:
                _safe_dump(patterns_data, f, indent=2)

        except Exception as e:
            print(f"Error saving patterns: {e}")
