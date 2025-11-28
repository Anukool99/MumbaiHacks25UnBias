import os
from typing import Any, Dict


class GeminiAdapter:
    """
    Placeholder adapter for calling the real Gemini API.
    Not implemented yet — added so the architecture is ready.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Would call the actual Gemini API.
        For now, raise NotImplementedError so it's clear when tests accidentally
        invoke this branch.
        """
        raise NotImplementedError("Gemini API integration not implemented yet.")


class MockGeminiAdapter:
    """
    Deterministic mock adapter used when GEMINI_API_KEY is NOT set.
    Makes tests stable.
    """

    async def generate(self, prompt: str) -> Dict[str, Any]:
        return {
            "mock": True,
            "prompt_received": prompt,
            "response": "This is a deterministic mock Gemini response.",
        }


def get_gemini_adapter():
    """
    Load the real Gemini adapter only if GEMINI_API_KEY is set.
    Otherwise return the mock adapter.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return GeminiAdapter(api_key)
    return MockGeminiAdapter()
