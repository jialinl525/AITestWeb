@echo off
echo Starting FastAPI server...
python -m uvicorn main:app --reload --port 8000
pause
