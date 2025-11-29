from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import httpx
import os
import json

from app.models.db import supabase
from app.services.gemini_adapter import get_gemini_adapter

router = APIRouter()

# Base URL for internal API calls (local or deployment)
INTERNAL_API_BASE = os.getenv("INTERNAL_API_BASE", "http://localhost:8000").rstrip("/")
print(f"🔧 INTERNAL_API_BASE = {INTERNAL_API_BASE}")


class AnalyzeById(BaseModel):
    article_id: UUID

class AnalyzeRaw(BaseModel):
    text: str
    url: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[str] = None


@router.post("/analyze")
async def analyze(payload: dict):
    """Unified analyze endpoint"""

    # STEP 1 — Load or create article
    if "article_id" in payload:
        article_id = payload["article_id"]
        res = supabase.table("articles").select("*").eq("id", str(article_id)).execute()
        if not res.data:
            raise HTTPException(404, "Article not found")
        article = res.data[0]
    else:
        raw = AnalyzeRaw(**payload)
        insert_res = supabase.table("articles").insert({
            "title": raw.title or "Untitled",
            "content": raw.text,
            "author": raw.source or None,
        }).execute()

        if not insert_res.data:
            raise HTTPException(500, "Failed to create article")

        article = insert_res.data[0]
        article_id = article["id"]

    # STEP 2 — Call /spans
    async with httpx.AsyncClient(timeout=60.0) as client:
        spans_resp = await client.post(
            f"{INTERNAL_API_BASE}/api/spans",
            json={"text": article["content"]},
        )
    spans_json = spans_resp.json()

    # STEP 3 — Call /angle
    async with httpx.AsyncClient(timeout=60.0) as client:
        angle_resp = await client.post(
            f"{INTERNAL_API_BASE}/api/angle",
            json={"text": article["content"]},
        )
    angle_json = angle_resp.json()

    angle_fp_res = supabase.table("angle_fingerprints").insert({
        "article_id": article_id,
        "patterns": angle_json.get("framing_patterns", []),
        "emotions": angle_json.get("dominant_emotions", []),
        "evidence": angle_json.get("evidence_spans", []),
    }).execute()
    angle_fp_id = angle_fp_res.data[0]["id"]

    # STEP 4 — Call /political-spectrum
    async with httpx.AsyncClient(timeout=60.0) as client:
        spectrum_resp = await client.post(
            f"{INTERNAL_API_BASE}/api/political-spectrum",
            json={"text": article["content"]},
        )
    spectrum_json = spectrum_resp.json()

    spectrum_fp_res = supabase.table("spectrum_fingerprints").insert({
        "article_id": article_id,
        "left_right_score": spectrum_json["left_right_score"],
        "populist_score": spectrum_json["populist_score"],
        "cluster": spectrum_json["cluster"],
    }).execute()
    spectrum_fp_id = spectrum_fp_res.data[0]["id"]

    # STEP 5 — Gemini Reflection
    adapter = get_gemini_adapter()
    prompt = (
        "Analyze political framing severity and detect missing biases.\n\n"
        f"TEXT:\n{article['content']}\n\n"
        f"SPANS:\n{spans_json}\n\n"
        f"ANGLE:\n{angle_json}\n\n"
        f"SPECTRUM:\n{spectrum_json}\n\n"
    )
    reflection = {"first": await adapter.generate(prompt)}

    # STEP 6 — Save spans in DB
    for span in spans_json.get("spans", []):
        supabase.table("spans").insert({
            "article_id": article_id,
            "span_type": span.get("type"),
            "text": span.get("text"),
            "start_index": span.get("start"),
            "end_index": span.get("end"),
        }).execute()

    # STEP 7 — Save full analysis
    analysis_res = supabase.table("analyses").insert({
    "article_id": article_id,
    "spans": json.dumps(spans_json),
    "angle": json.dumps(angle_json),
    "spectrum": json.dumps(spectrum_json),
    "gemini_reflection": json.dumps(reflection),
}).execute()

    analysis_id = analysis_res.data[0]["id"]

    # STEP 8 — Response
    return {
        "article_id": article_id,
        "analysis_id": analysis_id,
        "angle_fingerprint_id": angle_fp_id,
        "spectrum_fingerprint_id": spectrum_fp_id,
        "spans": spans_json,
        "angle": angle_json,
        "spectrum": spectrum_json,
        "reflection": reflection,
    }
