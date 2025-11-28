from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SpectrumInput(BaseModel):
    text: str

@router.post("/political-spectrum")
async def political_spectrum(input: SpectrumInput):
    """
    Simple deterministic scoring (mock).
    Real version will use GeminiAdapter.
    """
    text = input.text.lower()

    score = 0.0
    populism = 0.0

    # Mock heuristics
    if "government" in text or "policy" in text:
        score += 0.2
    if "corporate" in text:
        score -= 0.2

    if "people" in text:
        populism += 0.3
    if "elite" in text:
        populism += 0.4

    cluster = "centrist"
    if score < -0.2:
        cluster = "left"
    elif score > 0.2:
        cluster = "right"

    return {
        "left_right_score": score,
        "populist_score": populism,
        "cluster": cluster,
    }
