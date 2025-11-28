from fastapi import APIRouter
from pydantic import BaseModel
import re

router = APIRouter()


class AngleInput(BaseModel):
    text: str


class AngleOutput(BaseModel):
    angle_summary: str
    dominant_emotions: list
    framing_patterns: list
    evidence_spans: list
    confidence: float


CRISIS_WORDS = {"crisis", "disaster"}
BLAME_WORDS = {"fault", "blame", "responsible", "negligence", "accused"}


@router.post("/angle", response_model=AngleOutput)
async def analyze_angle(payload: AngleInput):
    text = payload.text.lower()

    dominant_emotions = []
    framing_patterns = []
    evidence_spans = []

    # --- Crisis / Fear Heuristic ---
    if any(w in text for w in CRISIS_WORDS):
        dominant_emotions.append("fear")
        framing_patterns.append("crisis")
        # extract phrase containing crisis context
        spans = []
        for w in CRISIS_WORDS:
            if w in text:
                spans.append(w)
        evidence_spans.extend(spans)

    # --- Blame Pattern ---
    if any(w in text for w in BLAME_WORDS):
        framing_patterns.append("blame")
        spans = []
        for w in BLAME_WORDS:
            if w in text:
                spans.append(w)
        evidence_spans.extend(spans)

    # --- Anecdotal Pattern (no numbers, personal storytelling pattern) ---
    contains_numbers = bool(re.search(r"\d+", text))
    anecdotal_markers = ["i saw", "i heard", "my friend", "people say", "someone told"]
    if not contains_numbers and any(m in text for m in anecdotal_markers):
        framing_patterns.append("anecdotal")
        spans = [m for m in anecdotal_markers if m in text]
        evidence_spans.extend(spans)

    # summary is just simple explanation of patterns
    summary_parts = []
    if "crisis" in framing_patterns:
        summary_parts.append("The text frames the situation as a crisis.")
    if "blame" in framing_patterns:
        summary_parts.append("The text assigns blame to an actor or group.")
    if "anecdotal" in framing_patterns:
        summary_parts.append("The text relies on anecdotal storytelling.")
    if not summary_parts:
        summary_parts.append("The text does not strongly match predefined patterns.")

    angle_summary = " ".join(summary_parts)

    return AngleOutput(
        angle_summary=angle_summary,
        dominant_emotions=dominant_emotions,
        framing_patterns=framing_patterns,
        evidence_spans=evidence_spans,
        confidence=1.0,  # deterministic for testing
    )
