from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import re

router = APIRouter()


class SpanRequest(BaseModel):
    text: str


class Span(BaseModel):
    label: str
    span_text: str
    start: int
    end: int
    confidence: float


class SpanResponse(BaseModel):
    spans: List[Span]


HEURISTICS = [
    # label, patterns, confidence

    # --- Existing (kept) ---
    ("Overgeneralization", 
        [r"\balways\b", r"\bnever\b", r"\bmost\b", r"\bmuch of\b", r"\beveryone\b", r"\bno one\b"],
        0.70
    ),

    ("Intent Attribution", 
        [r"\bdeliberately\b", r"\bintentionally\b", r"\bon purpose\b", r"\btrying to\b"],
        0.65
    ),

    ("Loaded Language", 
        [r"\balarming\b", r"\bdisastrous\b", r"\bcatastrophic\b", r"\bshocking\b"],
        0.60
    ),

    ("Paternalistic", 
        [r"\bmakes it difficult\b", r"\bcannot\b", r"\bunable to\b", r"\bincapable of\b"],
        0.55
    ),

    # --- New Categories ---

    # Emotional exaggeration
    ("Emotional Reasoning",
        [r"\bI feel like\b", r"\bit feels like\b", r"\bseems like\b"],
        0.55
    ),

    # Claims of knowing someone’s internal emotional state
    ("Mind Reading",
        [r"\byou think\b", r"\byou believe\b", r"\byou clearly want\b"],
        0.58
    ),

    # Doom language
    ("Catastrophizing",
        [r"\bthis will ruin\b", r"\bthis is the end\b", r"\bworst case\b", r"\bterrible outcome\b"],
        0.62
    ),

    # Blaming, simplistic cause-effect
    ("Causal Oversimplification",
        [r"\bthe reason is\b", r"\bbecause of them\b", r"\bit’s their fault\b"],
        0.65
    ),

    # "Should" rules / moralization
    ("Moralizing / 'Should' Statements",
        [r"\byou should\b", r"\byou shouldn't\b", r"\byou ought to\b", r"\bthey must\b"],
        0.60
    ),

    # Absolutist / binary framing
    ("Black-and-White Thinking",
        [r"\beither\b", r"\bor else\b", r"\bonly option\b", r"\bthere is no alternative\b"],
        0.63
    ),

    # Insinuation without evidence
    ("Speculative Accusation",
        [r"\bprobably lying\b", r"\bclearly hiding\b", r"\bmust be cheating\b"],
        0.67
    ),

    ("Appeal to Fear",
        [r"\byou will lose\b", r"\byou will regret\b", r"\byou won't survive\b"],
        0.64
    ),

    # Minimizing, dismissing legitimate concerns
    ("Minimization",
        [r"\bnot a big deal\b", r"\byou're overreacting\b", r"\bit’s nothing\b"],
        0.52
    ),

    # Exaggerated certainty or expertise
    ("Unwarranted Certainty",
        [r"\bI know for a fact\b", r"\bthere is no doubt\b", r"\bguaranteed\b"],
        0.66
    ),

    # Implies universal shared beliefs
    ("Bandwagon / Common Knowledge",
        [r"\beveryone knows\b", r"\ball of us agree\b", r"\bcommon knowledge\b"],
        0.58
    ),

    # Claims of inherent group traits
    ("Stereotyping",
        [r"\bpeople like you\b", r"\bthey're all\b", r"\bthose people\b"],
        0.68
    ),

    # exaggerated causality patterns
    ("Slippery Slope",
        [r"\bwill lead to\b", r"\bthis is how it starts\b", r"\bnext thing you know\b"],
        0.64
    ),

    # framing attack as benevolence
    ("Passive-Aggressive / Faux-Concern",
        [r"\bjust trying to help\b", r"\bfor your own good\b"],
        0.57
    ),

    # gives impression of lack of agency
    ("Victim Language / External Locus",
        [r"\bI have no choice\b", r"\bthere’s nothing I can do\b"],
        0.56
    ),

    # infers traits from single actions
    ("Labelling",
        [r"\bI'm such a failure\b", r"\bthey're idiots\b"],
        0.59
    ),
]



def extract_spans(text: str) -> List[Span]:
    spans: List[Span] = []

    for label, patterns, conf in HEURISTICS:
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                start, end = match.span()
                spans.append(Span(
                    label=label,
                    span_text=text[start:end],
                    start=start,
                    end=end,
                    confidence=conf
                ))
    return spans


@router.post("/spans", response_model=SpanResponse)
async def detect_spans(payload: SpanRequest):
    spans = extract_spans(payload.text)
    return SpanResponse(spans=spans)
