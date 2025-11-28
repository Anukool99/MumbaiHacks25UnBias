from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from app.models.db import supabase
from app.services.gemini_adapter import get_gemini_adapter
import httpx

router = APIRouter()

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
    """
    Unified analyze endpoint — handles:
    A) Load article by id
    B) Or create article from raw text
    """

    # ------------------------------------------------------------------
    # STEP 1 — Load or create article
    # ------------------------------------------------------------------

    if "article_id" in payload:
        article_id = payload["article_id"]

        article_res = supabase.table("articles").select("*").eq("id", str(article_id)).execute()

        if not article_res.data:
            raise HTTPException(404, "Article not found")

        article = article_res.data[0]

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

    # ------------------------------------------------------------------
    # STEP 2 — Call /api/spans
    # ------------------------------------------------------------------
    async with httpx.AsyncClient() as client:
        spans_resp = await client.post("http://localhost:8000/api/spans", json={"text": article["content"]})
    spans_json = spans_resp.json()

    # ------------------------------------------------------------------
    # STEP 3 — Call /api/angle
    # ------------------------------------------------------------------
    async with httpx.AsyncClient() as client:
        angle_resp = await client.post("http://localhost:8000/api/angle", json={"text": article["content"]})
    angle_json = angle_resp.json()

    # Store angle fingerprint separately
    angle_fingerprint_insert = supabase.table("angle_fingerprints").insert({
        "article_id": article_id,
        "patterns": angle_json.get("framing_patterns", []),
        "emotions": angle_json.get("dominant_emotions", []),
        "evidence": angle_json.get("evidence_spans", []),
    }).execute()

    fingerprint_id = angle_fingerprint_insert.data[0]["id"]

    # ------------------------------------------------------------------
    # STEP 4 — Gemini reflection pass
    # ------------------------------------------------------------------

    adapter = get_gemini_adapter()

    prompt = (
        f"Analyze the political framing severity for this article:\n\n"
        f"TEXT:\n{article['content']}\n\n"
        f"SPANS:\n{spans_json}\n\n"
        f"ANGLE:\n{angle_json}\n\n"
    )

    first_pass = await adapter.generate(prompt)
    second_pass = await adapter.generate(prompt)

    reflection = {
        "first": first_pass,
        "second": second_pass,
    }

    # ------------------------------------------------------------------
    # STEP 5 — Write spans to DB
    # ------------------------------------------------------------------
    for span in spans_json.get("spans", []):
        supabase.table("spans").insert({
            "article_id": article_id,
            "span_type": span.get("type"),
            "text": span.get("text"),
            "start_index": span.get("start"),
            "end_index": span.get("end"),
        }).execute()

    # ------------------------------------------------------------------
    # STEP 6 — Write analysis record
    # ------------------------------------------------------------------
    analysis_res = supabase.table("analyses").insert({
        "article_id": article_id,
        "spans": spans_json,
        "angle": angle_json,
        "gemini_reflection": reflection,
    }).execute()

    analysis_id = analysis_res.data[0]["id"]

    # ------------------------------------------------------------------
    # STEP 7 — Return final JSON
    # ------------------------------------------------------------------
    return {
        "article_id": article_id,
        "analysis_id": analysis_id,
        "fingerprint_id": fingerprint_id,
        "spans": spans_json,
        "angle": angle_json,
        "reflection": reflection,
    }
