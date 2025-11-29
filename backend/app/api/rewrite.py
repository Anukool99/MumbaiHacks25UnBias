from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.gemini_adapter import get_gemini_adapter

router = APIRouter()

class RewriteInput(BaseModel):
    text: str

SYSTEM_PROMPT = """
You are an impartial rewriting engine designed to remove ideological, political,
nationalistic, emotional, or persuasive framing from written content.

Your task:
- Rewrite the given text in a strictly neutral, factual, emotionally toned-down tone.
- Remove implied judgments, blame, praise, or exaggeration.
- Remove crisis framing, fear language, or sensationalism.
- Avoid introducing **any new bias or opinion**.
- Preserve factual meaning and core information.
- Do NOT summarize; rewrite with similar length unless verbosity is unnecessary.
- Do NOT say "the original text said" — produce a clean rewritten text directly.
"""

@router.post("/unbias")
async def unbias_text(input: RewriteInput):
    try:
        adapter = get_gemini_adapter()

        prompt = (
            SYSTEM_PROMPT
            + "\n\nRewrite the following text neutrally:\n\n"
            + input.text
        )

        result = await adapter.generate(prompt)

        # handle failure or malformed output
        unbiased = None
        if isinstance(result, dict) and "raw_response" in result:
            unbiased = result["raw_response"]
        else:
            unbiased = str(result)

        return {
            "original_text": input.text,
            "unbiased_text": unbiased,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
