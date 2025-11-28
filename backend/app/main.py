from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import health, articles, angle

# Load environment variables from .env file if it exists
load_dotenv()

app = FastAPI(title="UnBias API", version="1.0.0")

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(articles.router, prefix="/api", tags=["articles"])
app.include_router(angle.router, prefix="/api", tags=["angle"])


@app.get("/")
async def root():
    return {"message": "UnBias API"}

