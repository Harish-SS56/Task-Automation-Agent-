"""
Git Operations Tool - Handles Git repository operations.
"""

from pathlib import Path
from typing import Any, Dict

from .command_executor import CommandExecutorTool


class GitOperationsTool:
    """Tool for Git operations."""

    def __init__(self, base_path: str = "."):
        """
        Initialize the Git operations tool.

        Args:
            base_path: Base directory for Git operations
        """
        self.base_path = Path(base_path).resolve()
        self.command_executor = CommandExecutorTool(allowed_commands=["git"])

    def initialize_repo(self, repo_path: str = ".") -> Dict[str, Any]:
        """
        Initialize a Git repository.

        Args:
            repo_path: Path to initialize (relative to base_path)

        Returns:
            Result dictionary
        """
        full_path = self.base_path / repo_path
        full_path = full_path.resolve()

        result = self.command_executor.execute("git init", cwd=str(full_path))

        if result["success"]:
            result["message"] = f"Git repository initialized in {repo_path}"

        return result

    def create_branch(self, branch_name: str, repo_path: str = ".") -> Dict[str, Any]:
        """
        Create a new Git branch.

        Args:
            branch_name: Name of the branch to create
            repo_path: Path to the repository

        Returns:
            Result dictionary
        """
        full_path = self.base_path / repo_path
        full_path = full_path.resolve()

        result = self.command_executor.execute(
            f"git checkout -b {branch_name}", cwd=str(full_path)
        )

        if result["success"]:
            result["message"] = f"Branch '{branch_name}' created"

        return result

    def commit(
        self, message: str, repo_path: str = ".", add_all: bool = True
    ) -> Dict[str, Any]:
        """
        Commit changes to Git.

        Args:
            message: Commit message
            repo_path: Path to the repository
            add_all: Whether to add all changes before committing

        Returns:
            Result dictionary
        """
        full_path = self.base_path / repo_path
        full_path = full_path.resolve()

        results = []

        # Add files if requested
        if add_all:
            add_result = self.command_executor.execute("git add -A", cwd=str(full_path))
            results.append(add_result)

        # Commit
        commit_result = self.command_executor.execute(
            f'git commit -m "{message}"', cwd=str(full_path)
        )
        results.append(commit_result)

        if commit_result["success"]:
            return {
                "success": True,
                "message": f"Changes committed: {message}",
                "details": results,
            }
        else:
            return {
                "success": False,
                "error": commit_result.get("error", "Commit failed"),
                "details": results,
            }

    def get_status(self, repo_path: str = ".") -> Dict[str, Any]:
        """
        Get Git repository status.

        Args:
            repo_path: Path to the repository

        Returns:
            Result dictionary with status information
        """
        full_path = self.base_path / repo_path
        full_path = full_path.resolve()

        result = self.command_executor.execute("git status", cwd=str(full_path))

        return result

    def get_current_branch(self, repo_path: str = ".") -> Dict[str, Any]:
        """
        Get the current Git branch.

        Args:
            repo_path: Path to the repository

        Returns:
            Result dictionary with branch name
        """
        full_path = self.base_path / repo_path
        full_path = full_path.resolve()

        result = self.command_executor.execute(
            "git branch --show-current", cwd=str(full_path)
        )

        if result["success"]:
            branch_name = result["stdout"].strip()
            return {"success": True, "branch": branch_name}
        else:
            return result

    def push(
        self, remote: str = "origin", branch: str = None, repo_path: str = "."
    ) -> Dict[str, Any]:
        """
        Push changes to a remote repository.

        Args:
            remote: Name of the remote
            branch: Name of the branch to push (defaults to current branch)
            repo_path: Path to the repository

        Returns:
            Result dictionary
        """
        full_path = self.base_path / repo_path
        full_path = full_path.resolve()

        if not branch:
            branch_result = self.get_current_branch(repo_path)
            if not branch_result["success"]:
                return branch_result
            branch = branch_result["branch"]

        result = self.command_executor.execute(
            f"git push {remote} {branch}", cwd=str(full_path)
        )

        if result["success"]:
            result["message"] = f"Changes pushed to {remote}/{branch}"

        return result

    def pull(
        self, remote: str = "origin", branch: str = None, repo_path: str = "."
    ) -> Dict[str, Any]:
        """
        Pull changes from a remote repository.

        Args:
            remote: Name of the remote
            branch: Name of the branch to pull (defaults to current branch)
            repo_path: Path to the repository

        Returns:
            Result dictionary
        """
        full_path = self.base_path / repo_path
        full_path = full_path.resolve()

        if not branch:
            branch_result = self.get_current_branch(repo_path)
            if not branch_result["success"]:
                return branch_result
            branch = branch_result["branch"]

        result = self.command_executor.execute(
            f"git pull {remote} {branch}", cwd=str(full_path)
        )

        if result["success"]:
            result["message"] = f"Changes pulled from {remote}/{branch}"

        return result

    def add_remote(self, name: str, url: str, repo_path: str = ".") -> Dict[str, Any]:
        """
        Add a remote repository.

        Args:
            name: Name of the remote
            url: URL of the remote
            repo_path: Path to the repository

        Returns:
            Result dictionary
        """
        full_path = self.base_path / repo_path
        full_path = full_path.resolve()

        result = self.command_executor.execute(
            f"git remote add {name} {url}", cwd=str(full_path)
        )

        if result["success"]:
            result["message"] = f"Remote '{name}' added with URL {url}"

        return result
