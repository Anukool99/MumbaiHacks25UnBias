from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import health

# Load environment variables from .env file if it exists
load_dotenv()

app = FastAPI(title="UnBias API", version="1.0.0")

app.include_router(health.router, prefix="/api", tags=["health"])

@app.get("/")
async def root():
    return {"message": "UnBias API"}

