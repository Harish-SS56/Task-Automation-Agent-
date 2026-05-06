"""
Command Executor Tool - Executes system commands safely.
"""

import shlex
import subprocess
from typing import Any, Dict, Optional


class CommandExecutorTool:
    """Tool for executing system commands."""

    def __init__(self, allowed_commands: Optional[list] = None, timeout: int = 30):
        """
        Initialize the command executor.

        Args:
            allowed_commands: List of allowed command prefixes (for safety)
            timeout: Command execution timeout in seconds
        """
        self.allowed_commands = allowed_commands or []
        self.timeout = timeout

    def execute(
        self, command: str, cwd: Optional[str] = None, shell: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a system command.

        Args:
            command: Command to execute
            cwd: Working directory for command execution
            shell: Whether to use shell execution

        Returns:
            Result dictionary with output and status
        """
        try:
            # Safety check: validate command if allowed_commands is set
            if self.allowed_commands:
                command_lower = command.lower()
                if not any(
                    command_lower.startswith(allowed)
                    for allowed in self.allowed_commands
                ):
                    return {
                        "success": False,
                        "error": f"Command not in allowed list: {command}",
                    }

            # Parse command if not using shell
            if not shell:
                try:
                    cmd_parts = shlex.split(command)
                except ValueError:
                    # If parsing fails, use shell mode
                    shell = True

            # Execute command
            result = subprocess.run(
                command if shell else cmd_parts,
                shell=shell,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                encoding="utf-8",
                errors="replace",
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {self.timeout} seconds",
                "command": command,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": command}

    def execute_safe(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a command with additional safety checks.
        Only allows safe commands like git, npm, pip, python, etc.

        Args:
            command: Command to execute
            cwd: Working directory

        Returns:
            Result dictionary
        """
        # Define safe command prefixes
        safe_prefixes = [
            "git",
            "npm",
            "pip",
            "python",
            "python3",
            "node",
            "npx",
            "yarn",
            "pnpm",
            "ls",
            "pwd",
            "cd",
            "mkdir",
            "echo",
        ]

        command_lower = command.lower().strip()

        # Check if command starts with a safe prefix
        is_safe = any(command_lower.startswith(prefix) for prefix in safe_prefixes)

        if not is_safe:
            return {
                "success": False,
                "error": f"Command not in safe list: {command}",
                "requires_confirmation": True,
            }

        return self.execute(command, cwd=cwd)
