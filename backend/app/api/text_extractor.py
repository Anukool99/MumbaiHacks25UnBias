from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx
import os
from typing import Optional

router = APIRouter(
    prefix="/extract-text",
    tags=["Text Extraction"]
)

EXTRACTOR_API_URL = "https://extractorapi.com/api/v1/extractor/"
EXTRACTOR_API_KEY = os.getenv("EXTRACTOR_API_KEY")


class ExtractRequest(BaseModel):
    url: HttpUrl
    fields: Optional[str] = None        # optional (e.g., raw_text)
    js: Optional[bool] = False          # optional JS rendering
    wait: Optional[int] = None          # optional wait time


@router.post("/")
async def extract_text(request: ExtractRequest):
    """
    Receives a URL from the frontend and returns only the extracted text.
    """

    if not EXTRACTOR_API_KEY:
        raise HTTPException(status_code=500, detail="Extractor API key not configured.")

    params = {
        "apikey": EXTRACTOR_API_KEY,
        "url": request.url
    }

    if request.fields:
        params["fields"] = request.fields
    if request.js:
        params["js"] = "true"
    if request.wait:
        params["wait"] = request.wait

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(EXTRACTOR_API_URL, params=params)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"ExtractorAPI request failed: {exc}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="ExtractorAPI error.")

    data = response.json()

    if data.get("status") == "ERROR":
        raise HTTPException(status_code=400, detail="ExtractorAPI returned an error for this URL.")

    extracted_text = data.get("text")

    if not extracted_text:
        raise HTTPException(status_code=404, detail="No text found in article.")

    return {"text": extracted_text}
