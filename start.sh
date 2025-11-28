#!/bin/bash

# Start FastAPI application with uvicorn
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload