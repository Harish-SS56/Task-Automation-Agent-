"""Core modules for orchestration and system management."""

# Avoid circular imports: do NOT import TaskOrchestrator here.
# Import each class directly when needed:
#   from backend.core.orchestrator import TaskOrchestrator
#   from backend.core.memory_manager import MemoryManager
from .memory_manager import MemoryManager
from .progress_tracker import ProgressTracker
from .tool_registry import ToolRegistry

__all__ = [
    "TaskOrchestrator",
    "MemoryManager",
    "ProgressTracker",
    "ToolRegistry",
]
