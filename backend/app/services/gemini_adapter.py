import os
from typing import Any, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file on import so GEMINI_API_KEY is always available
load_dotenv()


class GeminiAdapter:
    """
    Real functional Gemini API adapter.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

        genai.configure(api_key=api_key)
        # Use Gemini 1.5 Pro model; change model name if needed
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Calls the actual Gemini API and returns structured output.
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text if hasattr(response, "text") else str(response)
            return {
                "mock": False,
                "raw_response": text
            }
        except Exception as e:
            return {
                "mock": False,
                "error": str(e)
            }


class MockGeminiAdapter:
    """
    Deterministic mock adapter used when GEMINI_API_KEY is NOT set.
    Makes tests stable and avoids API cost.
    """

    async def generate(self, prompt: str) -> Dict[str, Any]:
        return {
            "mock": True,
            "prompt_received": prompt,
            "response": "This is a deterministic mock Gemini response.",
        }


def get_gemini_adapter():
    """
    Returns real Gemini adapter when API key exists;
    Otherwise returns stable mock adapter.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        print("🔹 Using REAL Gemini API")
        return GeminiAdapter(api_key)

    print("🔹 Using MOCK Gemini Adapter (no GEMINI_API_KEY found)")
    return MockGeminiAdapter()
