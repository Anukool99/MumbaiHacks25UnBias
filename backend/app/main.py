from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api import (
    health,
    articles,
    spans,
    angle,
    gemini_test,
    analyze,
    political_spectrum,
    text_extractor,
    rewrite
)

# Load env variables
load_dotenv()

app = FastAPI(title="UnBias API", version="1.0.0")

# =========================
# CORS CONFIG — REQUIRED FOR FRONTEND
# =========================
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
    "*"  # keep for development — remove in production if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTES
# =========================
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(articles.router, prefix="/api", tags=["articles"])
app.include_router(spans.router, prefix="/api", tags=["spans"])
app.include_router(angle.router, prefix="/api", tags=["angle"])
app.include_router(gemini_test.router, prefix="/api", tags=["gemini_test"])
app.include_router(political_spectrum.router, prefix="/api", tags=["political_spectrum"])
app.include_router(text_extractor.router, prefix="/api", tags=["text_extractor"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(rewrite.router, prefix="/api", tags=["rewrite"])


@app.get("/")
async def root():
    return {"message": "UnBias API"}
