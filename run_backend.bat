@echo off
REM FPV Nexus Dashboard - Quick Start Script for Windows

echo.
echo ================================================
echo     FPV NEXUS DASHBOARD - QUICK START
echo ================================================
echo.

REM Get current directory
cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
echo OK - Python found

echo.
echo [2/3] Installing dependencies...
python -m pip install -q fastapi uvicorn pydantic numpy pandas scipy pvlib 2>nul
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo OK - All packages installed

echo.
echo [3/3] Starting FastAPI Backend...
echo.
echo Starting on http://localhost:8000
echo API docs: http://localhost:8000/docs
echo Health check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause
