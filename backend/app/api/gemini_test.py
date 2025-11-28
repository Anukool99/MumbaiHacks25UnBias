from fastapi import APIRouter
from pydantic import BaseModel
from app.services.gemini_adapter import get_gemini_adapter

router = APIRouter()

class PromptInput(BaseModel):
    prompt: str

@router.post("/gemini/test")
async def gemini_test(input: PromptInput):
    adapter = get_gemini_adapter()
    response = await adapter.generate(input.prompt)
    return {"adapter": adapter.__class__.__name__, "response": response}
