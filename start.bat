@echo off
echo Starting EduGenie Educational Assistant...
python -m uvicorn app:app --reload --port 8000
pause
