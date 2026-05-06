"""
File Operations Tool - Handles file system operations.
"""

from pathlib import Path
from typing import Any, Dict


class FileOperationsTool:
    """Tool for file system operations."""

    def __init__(self, base_path: str = "."):
        """
        Initialize the file operations tool.

        Args:
            base_path: Base directory for file operations (for safety)
        """
        self.base_path = Path(base_path).resolve()

    def create_file(
        self, file_path: str, content: str = "", overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new file.

        Args:
            file_path: Path to the file (relative to base_path)
            content: Content to write to the file
            overwrite: Whether to overwrite if file exists

        Returns:
            Result dictionary with success status and details
        """
        try:
            full_path = self.base_path / file_path
            full_path = full_path.resolve()

            # Safety check: ensure path is within base_path
            if not str(full_path).startswith(str(self.base_path)):
                return {
                    "success": False,
                    "error": "Path outside base directory not allowed",
                }

            # Check if file exists
            if full_path.exists() and not overwrite:
                return {"success": False, "error": f"File already exists: {file_path}"}

            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            full_path.write_text(content, encoding="utf-8")

            return {
                "success": True,
                "file_path": str(full_path),
                "message": f"File created: {file_path}",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a file.

        Args:
            file_path: Path to the file (relative to base_path)

        Returns:
            Result dictionary with file content
        """
        try:
            full_path = self.base_path / file_path
            full_path = full_path.resolve()

            # Safety check
            if not str(full_path).startswith(str(self.base_path)):
                return {
                    "success": False,
                    "error": "Path outside base directory not allowed",
                }

            if not full_path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            content = full_path.read_text(encoding="utf-8")

            return {"success": True, "content": content, "file_path": str(full_path)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """
        Create a directory.

        Args:
            dir_path: Path to the directory (relative to base_path)

        Returns:
            Result dictionary with success status
        """
        try:
            full_path = self.base_path / dir_path
            full_path = full_path.resolve()

            # Safety check
            if not str(full_path).startswith(str(self.base_path)):
                return {
                    "success": False,
                    "error": "Path outside base directory not allowed",
                }

            full_path.mkdir(parents=True, exist_ok=True)

            return {
                "success": True,
                "dir_path": str(full_path),
                "message": f"Directory created: {dir_path}",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, dir_path: str = ".") -> Dict[str, Any]:
        """
        List directory contents.

        Args:
            dir_path: Path to the directory (relative to base_path)

        Returns:
            Result dictionary with directory contents
        """
        try:
            full_path = self.base_path / dir_path
            full_path = full_path.resolve()

            # Safety check
            if not str(full_path).startswith(str(self.base_path)):
                return {
                    "success": False,
                    "error": "Path outside base directory not allowed",
                }

            if not full_path.exists():
                return {"success": False, "error": f"Directory not found: {dir_path}"}

            if not full_path.is_dir():
                return {
                    "success": False,
                    "error": f"Path is not a directory: {dir_path}",
                }

            items = []
            for item in full_path.iterdir():
                items.append(
                    {
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "path": str(item.relative_to(self.base_path)),
                    }
                )

            return {"success": True, "items": items, "path": str(full_path)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(
        self, file_path: str, require_confirmation: bool = True
    ) -> Dict[str, Any]:
        """
        Delete a file.

        Args:
            file_path: Path to the file (relative to base_path)
            require_confirmation: Whether confirmation is required (for safety)

        Returns:
            Result dictionary with success status
        """
        try:
            full_path = self.base_path / file_path
            full_path = full_path.resolve()

            # Safety check
            if not str(full_path).startswith(str(self.base_path)):
                return {
                    "success": False,
                    "error": "Path outside base directory not allowed",
                }

            if not full_path.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            if require_confirmation:
                return {
                    "success": False,
                    "error": "Deletion requires confirmation",
                    "requires_confirmation": True,
                }

            full_path.unlink()

            return {"success": True, "message": f"File deleted: {file_path}"}

        except Exception as e:
            return {"success": False, "error": str(e)}
