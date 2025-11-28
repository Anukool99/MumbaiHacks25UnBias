from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import health, articles,spans,angle, gemini_test, analyze, political_spectrum

# Load environment variables from .env file if it exists
load_dotenv()

app = FastAPI(title="UnBias API", version="1.0.0")

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(articles.router, prefix="/api", tags=["articles"])
app.include_router(spans.router, prefix="/api", tags=["spans"])
app.include_router(angle.router, prefix="/api", tags=["angle"])
app.include_router(gemini_test.router, prefix="/api", tags=["gemini_test"])
app.include_router(political_spectrum.router, prefix="/api", tags=["political_spectrum"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])

@app.get("/")
async def root():
    return {"message": "UnBias API"}

