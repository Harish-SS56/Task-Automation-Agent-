"""
Base agent class — common functionality shared by all agents.
"""

import json
import re
from typing import Any, Dict





class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.3):
        """
        Initialize the base agent.

        Args:
            model_name: Fallback model if GEMINI_MODEL env var is not set.
                        Note: GEMINI_MODEL in .env always takes priority.
            temperature: LLM sampling temperature.
        """
        from ..utils.gemini_client import create_llm
        self.llm = create_llm(model_name=model_name, temperature=temperature)
        self.model_name = model_name
        self.temperature = temperature

    def _create_prompt(self, template: str, **kwargs) -> str:
        """Return the raw template string (LangChain-free)."""
        return template

    def _call_llm(self, prompt: str, **kwargs) -> str:
        """
        Call the LLM with a prompt string.

        Gemini requires at least one human-role message — sending as
        ("human", ...) is compatible with all LangChain providers.

        Args:
            prompt: The prompt to send.
            **kwargs: If provided, format the prompt string with these values.

        Returns:
            LLM response as a plain string.
        """
        try:
            if kwargs:
                prompt = prompt.format(**kwargs)

            # Always send as a human message — Gemini rejects system-only messages.
            response = self.llm.invoke([("human", prompt)])
            return response.content

        except Exception as e:
            raise RuntimeError(f"Error calling LLM: {str(e)}")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling markdown code blocks.

        Returns:
            Parsed dict, or {'raw_response': response} if parsing fails.
        """
        # Strip markdown code fences first
        fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
        if fence:
            response = fence.group(1)

        # Try to isolate the outermost JSON object
        obj = re.search(r"\{.*\}", response, re.DOTALL)
        if obj:
            response = obj.group(0)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}

    def log(self, message: str, level: str = "INFO") -> None:
        """Simple print-based logger (override for proper logging)."""
        print(f"[{level}] {self.__class__.__name__}: {message}")
