"""
Web Operations Tool - Handles web requests and operations.
"""

import time
from typing import Any, Dict, Optional

import requests


class WebOperationsTool:
    """Tool for web operations."""

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize the web operations tool.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TaskAutomationAgent/1.0"})

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a GET request.

        Args:
            url: URL to request
            params: Query parameters
            headers: Additional headers

        Returns:
            Result dictionary with response data
        """
        for attempt in range(self.max_retries):
            try:
                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)

                response = self.session.get(
                    url, params=params, headers=request_headers, timeout=self.timeout
                )

                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "content": response.text,
                    "headers": dict(response.headers),
                    "url": response.url,
                }

            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": f"Request timed out after {self.timeout} seconds",
                    }
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    return {"success": False, "error": str(e)}
                time.sleep(1)

        return {"success": False, "error": "Max retries exceeded"}

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Make a POST request.

        Args:
            url: URL to request
            data: Form data
            json_data: JSON data
            headers: Additional headers

        Returns:
            Result dictionary with response data
        """
        try:
            request_headers = self.session.headers.copy()
            if headers:
                request_headers.update(headers)

            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
            )

            return {
                "success": response.status_code in [200, 201],
                "status_code": response.status_code,
                "content": response.text,
                "headers": dict(response.headers),
                "url": response.url,
            }

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def download_file(self, url: str, save_path: str) -> Dict[str, Any]:
        """
        Download a file from a URL.

        Args:
            url: URL to download from
            save_path: Path to save the file

        Returns:
            Result dictionary
        """
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return {
                "success": True,
                "file_path": save_path,
                "size": len(response.content),
            }

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
