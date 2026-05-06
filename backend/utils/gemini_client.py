"""
Gemini LLM client - Direct HTTP calls to Gemini API (no google-genai needed).
"""

import os
import json
import requests
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env
_root = Path(__file__).resolve().parent.parent.parent
for _p in [_root / ".env", Path.cwd() / ".env", Path.cwd().parent / ".env"]:
    if _p.exists():
        load_dotenv(_p, override=True)
        break
else:
    load_dotenv(override=True)


class GeminiLLM:
    """Direct Gemini API client using requests library."""
    
    def __init__(self, model: str, api_key: str, temperature: float = 0.3):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def invoke(self, messages):
        """Call Gemini API with messages."""
        # Convert messages to text
        text_parts = []
        for msg in messages:
            if isinstance(msg, tuple):
                _, text = msg
                text_parts.append(str(text))
            elif hasattr(msg, "content"):
                text_parts.append(str(msg.content))
            else:
                text_parts.append(str(msg))
        
        prompt = "\n\n".join(p for p in text_parts if p.strip())
        
        # Call Gemini API
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": 2048,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0].get("content", {})
                if "parts" in content and len(content["parts"]) > 0:
                    return GeminiResponse(content["parts"][0].get("text", ""))
            
            raise ValueError(f"Unexpected response format: {data}")
        
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")


class GeminiResponse:
    """Response wrapper matching LangChain interface."""
    
    def __init__(self, text: str):
        self.content = text


def create_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
):
    """Create a Gemini LLM client.
    
    No external dependencies needed - uses requests library only.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL") or model_name or "gemini-2.5-flash-lite"
    temp = temperature if temperature is not None else 0.3

    if not gemini_key:
        raise ValueError(
            "GEMINI_API_KEY is not set.\n"
            "Add it to your .env file:  GEMINI_API_KEY=your-key-here"
        )

    return GeminiLLM(model=gemini_model, api_key=gemini_key, temperature=temp)
