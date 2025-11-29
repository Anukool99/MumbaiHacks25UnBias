# angle_api.py
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Tuple
import re
from collections import defaultdict

router = APIRouter()

# ---------- Schemas ----------
class AngleInput(BaseModel):
    text: str
    mode: str = Field("heuristic", description="heuristic | llm (llm not implemented - placeholder)")

class AngleOutput(BaseModel):
    angle_summary: str
    dominant_emotions: List[str]
    framing_patterns: List[str]
    persuasion_techniques: List[str]
    evidence_spans: List[str]
    intensity_scores: Dict[str, float]
    angle_categories: List[str]
    confidence: float
    mode_used: str

# ---------- Lexicons & Patterns ----------
# Narrative angle lexicons grouped by angle -> set(words or phrases)
ANGLE_LEXICONS = {
    "crisis": {"crisis", "disaster", "catastrophic", "emergency", "collapse"},
    "blame": {"fault", "blame", "responsible", "negligence", "accused", "failure"},
    "moral-outrage": {"corrupt", "outrageous", "unethical", "immoral", "betrayal", "scandal"},
    "hero-villain": {"hero", "villain", "savior", "enemy", "fight against", "standing up to"},
    "underdog": {"little guy", "ordinary people", "underdog", "outmatched", "stacked against"},
    "economic-anxiety": {"job losses", "unemployment", "we can't afford", "economic collapse", "recession"},
    "health-risk": {"unsafe", "hazardous", "toxic", "life-threatening", "infectious"},
    "identity": {"people like us", "outsiders", "they don't understand", "not one of us"},
    "nostalgia": {"back when", "bring back", "golden age", "we used to"},
    "futurism": {"future", "next generation", "innovative", "transformative", "revolutionize"},
    "conspiracy": {"cover-up", "hidden agenda", "behind the scenes", "they don't want you to know"},
    "anecdotal": {"i saw", "i heard", "my friend", "people say", "someone told me"},
    "narrative-arc": {"at first", "initially", "but then", "however", "in the end", "finally", "as a result"},
}

# Persuasion techniques lexicons
PERSUASION_LEXICONS = {
    "bandwagon": {"everyone", "everybody", "people are", "everyone agrees", "join the crowd"},
    "appeal-to-authority": {"experts say", "scientists agree", "according to doctors", "research shows"},
    "emotional-exaggeration": {"catastrophic", "horrifying", "unbelievable", "outrageous", "shocking"},
    "absolutist": {"always", "never", "everyone", "no one", "guaranteed", "100%"},
    "urgency": {"act now", "time is running out", "before it's too late", "urgent"},
    "loaded-question": {"why would they", "how come they", "isn't it obvious"},
    "rhetorical-contrast": {"unlike them", "we choose", "they choose", "on the other hand"},
    "fear-appeal": {"fear", "afraid", "terrified", "panic", "scared"},
    "social-proof": {"reviews", "testimonials", "people say", "users report"},
}

# Map angle -> category (coarse grouping)
ANGLE_CATEGORY_MAP = {
    "crisis": "Fear / Threat",
    "blame": "Anger / Accountability",
    "moral-outrage": "Anger / Moral",
    "hero-villain": "Narrative / Characters",
    "underdog": "Identity / Power",
    "economic-anxiety": "Economic",
    "health-risk": "Health / Safety",
    "identity": "Identity",
    "nostalgia": "Nostalgia",
    "futurism": "Progress / Innovation",
    "conspiracy": "Conspiratorial",
    "anecdotal": "Anecdotal",
    "narrative-arc": "Narrative / Structure",
}

# Emotion mapping for quick assignment
ANGLE_TO_EMOTION = {
    "crisis": "fear",
    "blame": "anger",
    "moral-outrage": "anger",
    "hero-villain": "trust/antagonism",
    "underdog": "sympathy",
    "economic-anxiety": "anxiety",
    "health-risk": "fear",
    "identity": "belonging",
    "nostalgia": "nostalgia",
    "futurism": "hope",
    "conspiracy": "suspicion",
    "anecdotal": "empathy",
    "narrative-arc": "engagement",
}

# Helper regexes
SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')

# ---------- Utility functions ----------
def normalize_text(s: str) -> str:
    return s.strip().lower()

def find_sentences_with_terms(text: str, terms: List[str]) -> List[str]:
    sentences = SENTENCE_SPLIT_RE.split(text)
    found = []
    for s in sentences:
        sl = s.lower()
        for t in terms:
            if t in sl:
                found.append(s.strip())
                break
    return found

def match_lexicon(text: str, lexicon: Dict[str, set]) -> Tuple[List[str], Dict[str, int]]:
    """
    Return list of matched keys and counts.
    """
    matches = []
    counts = defaultdict(int)
    lowered = text.lower()
    # Sort lexicon values by descending length to prefer multi-word matches first
    for key, phrases in lexicon.items():
        for ph in sorted(phrases, key=len, reverse=True):
            if ph in lowered:
                counts[key] += lowered.count(ph)
    for k, v in counts.items():
        if v > 0:
            matches.append(k)
    return matches, counts

def compute_intensity(counts: Dict[str, int], total_words: int) -> Dict[str, float]:
    """
    Simple normalized intensity: occurrences / sqrt(total_words) scaled then clipped to [0,1].
    This keeps it deterministic and comparable across inputs.
    """
    scores = {}
    denom = max(1.0, total_words ** 0.5)
    for k, v in counts.items():
        raw = min(1.0, (v / denom))  # simple normalization
        scores[k] = round(raw, 3)
    return scores

# ---------- Main heuristic analyzer ----------
def heuristic_analyze(text: str) -> AngleOutput:
    if not text:
        return AngleOutput(
            angle_summary="No text provided.",
            dominant_emotions=[],
            framing_patterns=[],
            persuasion_techniques=[],
            evidence_spans=[],
            intensity_scores={},
            angle_categories=[],
            confidence=0.0,
            mode_used="heuristic",
        )

    norm_text = text.strip()
    lowered = norm_text.lower()
    total_words = len(re.findall(r"\w+", lowered))

    # Match angles
    angle_matches, angle_counts = match_lexicon(lowered, ANGLE_LEXICONS)

    # Match persuasion techniques
    pers_matches, pers_counts = match_lexicon(lowered, PERSUASION_LEXICONS)

    # Evidence spans: sentence-level evidence for both sets of matches
    evidence_spans = []
    # For angles: collect sentences containing any of the lexicon phrases for matched angles
    for angle in angle_matches:
        phrases = ANGLE_LEXICONS.get(angle, set())
        evidence_spans.extend(find_sentences_with_terms(norm_text, list(phrases)))
    # For persuasion techniques: add only sentences not already included
    for pers in pers_matches:
        phrases = PERSUASION_LEXICONS.get(pers, set())
        for s in find_sentences_with_terms(norm_text, list(phrases)):
            if s not in evidence_spans:
                evidence_spans.append(s)

    # Also attach short keyword spans (first N tokens) as secondary evidence
    # but keep sentences primary
    if not evidence_spans:
        # fallback: top matched words
        top_words = sorted(re.findall(r"\w+", lowered), key=lambda x: lowered.count(x), reverse=True)[:5]
        evidence_spans = [" ".join(top_words)]

    # Dominant emotions: map from angle matches
    emotion_set = []
    for a in angle_matches:
        em = ANGLE_TO_EMOTION.get(a)
        if em and em not in emotion_set:
            emotion_set.append(em)

    # Categories
    categories = []
    for a in angle_matches:
        cat = ANGLE_CATEGORY_MAP.get(a)
        if cat and cat not in categories:
            categories.append(cat)

    # Intensity scores
    intensity_scores = {}
    # Angles intensity
    intensity_scores.update({f"angle:{k}": v for k, v in compute_intensity(angle_counts, total_words).items()})
    # Persuasion intensity
    intensity_scores.update({f"persuasion:{k}": v for k, v in compute_intensity(pers_counts, total_words).items()})

    # Confidence heuristic: combine distinct signals and text length
    signal_strength = (len(angle_matches) + len(pers_matches))
    # normalize roughly: more signals + longer text -> higher confidence
    confidence = min(0.99, round(0.2 + 0.15 * signal_strength + 0.001 * total_words, 3))

    # Construct angle_summary
    summary_parts = []
    if angle_matches:
        summary_parts.append("Detected angles: " + ", ".join(angle_matches) + ".")
    if pers_matches:
        summary_parts.append("Detected persuasion techniques: " + ", ".join(pers_matches) + ".")
    if not summary_parts:
        summary_parts = ["No strong predefined angles or persuasion techniques detected."]

    angle_summary = " ".join(summary_parts)

    return AngleOutput(
        angle_summary=angle_summary,
        dominant_emotions=emotion_set,
        framing_patterns=angle_matches,
        persuasion_techniques=pers_matches,
        evidence_spans=evidence_spans,
        intensity_scores=intensity_scores,
        angle_categories=categories,
        confidence=confidence,
        mode_used="heuristic",
    )

# ---------- FastAPI endpoint ----------
@router.post("/angle", response_model=AngleOutput)
async def analyze_angle(payload: AngleInput):
    text = payload.text or ""
    mode = payload.mode or "heuristic"

    # Only heuristic implemented here. Hook for LLM can be plugged in later.
    if mode != "heuristic":
        # Placeholder behaviour: return heuristic analysis but mark mode_used accordingly.
        out = heuristic_analyze(text)
        out.mode_used = f"llm-fallback"
        return out

    return heuristic_analyze(text)

# ---------- App for standalone run ----------
app = FastAPI()
app.include_router(router, prefix="")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("angle_api:app", host="127.0.0.1", port=8000, reload=True)
