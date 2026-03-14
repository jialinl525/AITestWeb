#!/bin/bash
echo "Starting FastAPI server..."
uvicorn main:app --reload --port 8000
