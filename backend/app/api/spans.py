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
    ("Overgeneralization", [r"\balways\b", r"\bnever\b", r"\bmost\b", r"\bmuch of\b"], 0.70),
    ("Intent Attribution", [r"\bdeliberately\b", r"\bintentionally\b"], 0.65),
    ("Loaded Language", [r"\balarming\b", r"\bdisastrous\b"], 0.60),
    ("Paternalistic", [r"\bmakes it difficult\b", r"\bcannot\b", r"\bunable to\b"], 0.55),
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
