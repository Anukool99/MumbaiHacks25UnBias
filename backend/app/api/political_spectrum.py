from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict
import json

from app.services.gemini_adapter import get_gemini_adapter

router = APIRouter()
gemini = get_gemini_adapter()  # Real or mock automatically


class SpectrumInput(BaseModel):
    text: str


# --------------------------
# 🔥 IMPROVED SYSTEM PROMPT
# + FEW-SHOT EXAMPLES
# --------------------------

BASE_PROMPT = """
You are a political-spectrum classifier.

Your job is to analyze a piece of text and return its political characteristics as strict JSON:
{
  "left_right_score": float from -1.0 (strong left) to +1.0 (strong right),
  "populist_score": float from 0.0 (non-populist) to 1.0 (strong populism),
  "cluster": one of [
      "left", "center-left", "centrist", "center-right", "right",
      "populist-left", "populist-right"
  ]
}

You MUST:
- ONLY output valid JSON.
- Never include commentary.
- Base your output strictly on the text content.
- Use nuanced political reasoning, not keyword heuristics.

--------------------------
FEW-SHOT EXAMPLES
--------------------------

EXAMPLE 1:
Text:
"The government should regulate corporations to prevent exploitation and ensure workers have protections."

JSON Response:
{
  "left_right_score": -0.45,
  "populist_score": 0.10,
  "cluster": "left"
}

---

EXAMPLE 2:
Text:
"The elites have ignored the will of ordinary people. We must take back control and restore power to the people."

JSON Response:
{
  "left_right_score": 0.05,
  "populist_score": 0.90,
  "cluster": "populist-right"
}

---

END OF FEW-SHOT EXAMPLES
--------------------------

Now classify the following text:
"""


# --------------------------
# 🚀 ENDPOINT
# --------------------------

@router.post("/political-spectrum")
async def political_spectrum(input: SpectrumInput):
    """
    Uses Gemini to classify political spectrum.
    Falls back to mock adapter if API key missing.
    """

    prompt = BASE_PROMPT + "\n" + input.text

    gemini_response = await gemini.generate(prompt)

    # If adapter error
    if "error" in gemini_response:
        return {
            "mock": True,
            "error": gemini_response["error"],
            "fallback_result": {
                "left_right_score": 0.0,
                "populist_score": 0.0,
                "cluster": "centrist"
            }
        }

    # If mock adapter was used
    if gemini_response.get("mock"):
        return gemini_response

    raw = gemini_response.get("raw_response", "")

    # Try to parse the JSON
    try:
        parsed = json.loads(raw)
        return parsed
    except Exception:
        # Attempt to recover JSON even if Gemini adds stray text
        try:
            cleaned = extract_json(raw)
            return json.loads(cleaned)
        except Exception:
            return {
                "error": "Gemini returned invalid JSON",
                "raw_response": raw
            }


# --------------------------
# 🛠 JSON RECOVERY
# --------------------------

def extract_json(text: str) -> str:
    """
    Extract the first {...} block from text.
    Helps when Gemini accidentally wraps JSON in text.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found")
    return text[start:end+1]
