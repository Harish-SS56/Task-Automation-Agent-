"""
Tool Registry - Manages and provides access to all tools.
"""

from typing import Any, Dict

from ..tools.command_executor import CommandExecutorTool
from ..tools.file_operations import FileOperationsTool
from ..tools.git_operations import GitOperationsTool
from ..tools.web_operations import WebOperationsTool


class ToolRegistry:
    """Registry for managing and accessing tools."""

    def __init__(self, base_path: str = "."):
        """
        Initialize the tool registry.

        Args:
            base_path: Base path for file operations
        """
        self.base_path = base_path
        self._tools = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize all available tools."""
        self._tools["file_operations"] = FileOperationsTool(base_path=self.base_path)
        self._tools["git_operations"] = GitOperationsTool(base_path=self.base_path)
        self._tools["command_executor"] = CommandExecutorTool()
        self._tools["web_operations"] = WebOperationsTool()

    def get_tool(self, tool_name: str):
        """
        Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_name)

    def execute_tool(self, tool_name: str, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool operation.

        Args:
            tool_name: Name of the tool
            operation: Operation to perform
            **kwargs: Arguments for the operation

        Returns:
            Result dictionary
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {"success": False, "error": f"Tool not found: {tool_name}"}

        if not hasattr(tool, operation):
            return {
                "success": False,
                "error": f"Operation '{operation}' not found on tool '{tool_name}'",
            }

        try:
            method = getattr(tool, operation)
            result = method(**kwargs)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing {tool_name}.{operation}: {str(e)}",
            }

    def list_tools(self) -> list:
        """List all available tools."""
        return list(self._tools.keys())

    def list_operations(self, tool_name: str) -> list:
        """
        List available operations for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List of operation names
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return []

        # Get all methods that don't start with underscore
        operations = [
            name
            for name in dir(tool)
            if not name.startswith("_") and callable(getattr(tool, name))
        ]

        return operations
