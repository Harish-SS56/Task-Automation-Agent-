"""
Executor Agent - Executes tasks using available tools.
Implements Tool Use and Exception Handling patterns.
"""

import inspect
import time
from datetime import datetime
from typing import Any, Dict, Optional

from ..core.tool_registry import ToolRegistry
from ..models import ExecutionResult, Task, TaskStatus
from .base_agent import BaseAgent

# ---------------------------------------------------------------------------
# Param alias maps: LLM-generated key  →  actual method param name
# ---------------------------------------------------------------------------
_ALIAS_MAP: Dict[tuple, Dict[str, str]] = {
    ("file_operations", "create_file"): {
        "path": "file_path", "filename": "file_path", "name": "file_path",
        "file": "file_path", "filepath": "file_path",
        "text": "content", "data": "content", "body": "content",
    },
    ("file_operations", "create_directory"): {
        "path": "dir_path", "directory": "dir_path", "folder": "dir_path",
        "name": "dir_path", "dir": "dir_path", "dirname": "dir_path",
    },
    ("file_operations", "read_file"): {
        "path": "file_path", "filename": "file_path", "name": "file_path",
    },
    ("file_operations", "list_directory"): {
        "path": "dir_path", "directory": "dir_path", "folder": "dir_path",
    },
    ("file_operations", "delete_file"): {
        "path": "file_path", "filename": "file_path", "name": "file_path",
    },
    ("git_operations", "initialize_repo"): {
        "path": "repo_path", "directory": "repo_path", "dir": "repo_path",
        "repo": "repo_path", "folder": "repo_path",
    },
    ("git_operations", "create_branch"): {
        "branch": "branch_name", "name": "branch_name",
    },
    ("git_operations", "commit"): {
        "msg": "message", "commit_message": "message", "text": "message",
    },
    ("command_executor", "execute"): {
        "cmd": "command", "command_line": "command",
    },
    ("command_executor", "execute_safe"): {
        "cmd": "command", "command_line": "command",
    },
}

# Meta-keys that the LLM puts in tool_params but are not method arguments
_META_KEYS = {"action", "tool", "operation", "tool_name", "type"}


class ExecutorAgent(BaseAgent):
    """Agent that executes tasks using available tools."""

    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        """
        Initialize the executor agent.

        Args:
            tool_registry: Tool registry instance
        """
        super().__init__(temperature=0.1)
        self.tool_registry = tool_registry or ToolRegistry()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_task(self, task: Task) -> ExecutionResult:
        """
        Execute a task using the appropriate tool.

        Args:
            task: Task to execute

        Returns:
            ExecutionResult with outcome details
        """
        self.log(f"Executing task: {task.description}")

        start_time = time.time()
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()

        try:
            if not task.tool:
                task.tool = self._infer_tool(task.description)

            if not task.tool:
                return self._fail(
                    task,
                    "No tool specified and could not infer tool from task description",
                    start_time,
                )

            result = self._execute_tool_operation(task)
            execution_time = time.time() - start_time

            if result.get("success"):
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                return ExecutionResult(
                    task_id=task.id,
                    success=True,
                    output=str(result.get("message", result.get("content", "Task completed"))),
                    execution_time=execution_time,
                    metadata=result,
                )
            else:
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    self.log(f"Task failed, retrying ({task.retry_count}/{task.max_retries})")
                    time.sleep(1)
                    return self.execute_task(task)

                return self._fail(
                    task,
                    result.get("error", "Task execution failed"),
                    start_time,
                    metadata=result,
                )

        except Exception as e:
            self.log(f"Exception during task execution: {str(e)}", "ERROR")
            return self._fail(task, str(e), start_time)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fail(
        self,
        task: Task,
        error: str,
        start_time: float,
        metadata: Dict[str, Any] = None,
    ) -> ExecutionResult:
        task.status = TaskStatus.FAILED
        task.error = error
        task.completed_at = datetime.now()
        return ExecutionResult(
            task_id=task.id,
            success=False,
            error=error,
            execution_time=time.time() - start_time,
            metadata=metadata or {},
        )

    def _infer_tool(self, description: str) -> Optional[str]:
        """Infer which tool to use from task description."""
        d = description.lower()

        if any(k in d for k in ["git", "commit", "repository", "branch", "init repo"]):
            return "git_operations"
        if any(k in d for k in ["install", "pip ", "venv", "virtualenv", "npm ", "run ", "python -m"]):
            return "command_executor"
        if any(k in d for k in ["download", "http", "url", "fetch url", "web request"]):
            return "web_operations"
        if any(k in d for k in [
            "file", "directory", "folder", "readme", ".gitignore",
            "pyproject", "requirements", "create ", "write ", "read ",
        ]):
            return "file_operations"

        return None

    def _get_default_operation(self, tool_name: str, description: str) -> Optional[str]:
        """Infer the operation from the tool and task description."""
        d = description.lower()

        if tool_name == "file_operations":
            # Check directory BEFORE generic create (important priority!)
            if any(k in d for k in ["director", "folder", "mkdir"]):
                return "create_directory"
            if any(k in d for k in ["delete", "remov"]):
                return "delete_file"
            if any(k in d for k in ["read", "open", "view"]):
                return "read_file"
            if any(k in d for k in ["list", "show contents"]):
                return "list_directory"
            # Default: create_file for write/create
            return "create_file"

        if tool_name == "git_operations":
            if any(k in d for k in ["init", "initiali"]):
                return "initialize_repo"
            if any(k in d for k in ["branch"]):
                return "create_branch"
            if any(k in d for k in ["commit"]):
                return "commit"
            if any(k in d for k in ["push"]):
                return "push"
            if any(k in d for k in ["pull"]):
                return "pull"
            if any(k in d for k in ["status"]):
                return "get_status"
            return "get_status"

        if tool_name == "web_operations":
            if "download" in d:
                return "download_file"
            if "post" in d:
                return "post"
            return "get"

        if tool_name == "command_executor":
            return "execute_safe"

        return None

    def _clean_params(
        self, params: Dict[str, Any], tool_name: str, operation: str
    ) -> Dict[str, Any]:
        """
        Remove meta-keys and apply alias mapping so params match the method signature.
        """
        # 1. Drop LLM meta-keys
        cleaned = {k: v for k, v in params.items() if k not in _META_KEYS}

        # 2. Apply alias mapping
        aliases = _ALIAS_MAP.get((tool_name, operation), {})
        result = {}
        for k, v in cleaned.items():
            result[aliases.get(k, k)] = v

        return result

    def _filter_for_method(self, method, params: Dict[str, Any]) -> Dict[str, Any]:
        """Keep only kwargs the method actually accepts."""
        sig = inspect.signature(method)
        valid = set(sig.parameters.keys())
        return {k: v for k, v in params.items() if k in valid}

    def _derive_params_from_description(
        self, description: str, tool_name: str, operation: str, existing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Best-effort extraction of required params from task description when
        tool_params is empty or incomplete.
        """
        d = description
        params = dict(existing)

        if tool_name == "file_operations":
            if operation == "create_directory":
                if "dir_path" not in params:
                    # Extract quoted name or last noun-like token
                    import re
                    m = re.search(r"['\"`]([^'\"`]+)['\"`]", d)
                    if m:
                        params["dir_path"] = m.group(1)
                    else:
                        # Heuristic: look for words like "my_project", "src/", "tests/" in description
                        words = re.findall(r"[\w/]+", d)
                        candidates = [w for w in words if "/" in w or "_" in w or
                                      any(k in w.lower() for k in ["project", "src", "test", "app", "lib"])]
                        if candidates:
                            params["dir_path"] = candidates[0]
                        else:
                            params["dir_path"] = "new_project"

            elif operation == "create_file":
                if "file_path" not in params:
                    import re
                    # Look for known filenames
                    known = re.findall(
                        r"[\w/.-]+\.(?:md|py|txt|toml|cfg|ini|json|yaml|yml|gitignore|env)",
                        d, re.IGNORECASE
                    )
                    if known:
                        params["file_path"] = known[0]
                    elif ".gitignore" in d.lower():
                        params["file_path"] = ".gitignore"
                    else:
                        params["file_path"] = "output.txt"

                if "content" not in params:
                    params["content"] = ""

            elif operation in ("initialize_repo", "get_status", "commit"):
                if "repo_path" not in params:
                    params["repo_path"] = "."
                if operation == "commit" and "message" not in params:
                    params["message"] = "Initial commit"

        elif tool_name == "command_executor":
            if "command" not in params:
                import re
                # Try to extract a command from description
                # Look for python/pip/git/npm commands
                cmd_match = re.search(
                    r"(python\S*\s+\S+.*|pip\s+\S+.*|git\s+\S+.*|npm\s+\S+.*|virtualenv\s+\S+.*)",
                    d, re.IGNORECASE
                )
                if cmd_match:
                    params["command"] = cmd_match.group(1).strip()
                elif "virtual" in d.lower() or "venv" in d.lower():
                    params["command"] = "python -m venv .venv"
                elif "install" in d.lower():
                    params["command"] = "pip install -r requirements.txt"
                else:
                    params["command"] = "echo Task completed"

        return params

    def _execute_tool_operation(self, task: Task) -> Dict[str, Any]:
        """Execute the right tool method for a task with clean, correct params."""
        if not task.tool:
            return {"success": False, "error": "No tool specified"}

        # Parse "tool_name.operation" format
        tool_name = task.tool
        operation = None

        if "." in tool_name:
            tool_name, operation = tool_name.split(".", 1)

        params = dict(task.tool_params)

        # If operation encoded in params, extract it
        if "operation" in params:
            operation = params.pop("operation")

        # Determine operation if still missing
        if not operation:
            operation = self._get_default_operation(tool_name, task.description)

        if not operation:
            return {
                "success": False,
                "error": f"Could not determine operation for tool '{tool_name}'",
            }

        # Clean params: remove meta-keys + apply aliases
        params = self._clean_params(params, tool_name, operation)

        # Derive any missing required params from the task description
        params = self._derive_params_from_description(
            task.description, tool_name, operation, params
        )

        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool not found: {tool_name}"}

        if not hasattr(tool, operation):
            return {
                "success": False,
                "error": f"Operation '{operation}' not found on tool '{tool_name}'",
            }

        method = getattr(tool, operation)

        # Filter to only params the method actually accepts
        safe_params = self._filter_for_method(method, params)

        self.log(f"Calling {tool_name}.{operation}({safe_params})")
        return self.tool_registry.execute_tool(tool_name, operation, **safe_params)
