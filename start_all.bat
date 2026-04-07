@echo off
REM FPV Nexus v4.0 - Complete Setup Script
REM This script installs all dependencies and starts both backend and frontend

echo.
echo ====================================================
echo   FPV Nexus v4.0 - MERN Stack Setup
echo   Multi-Dam Interactive Analysis System
echo ====================================================
echo.

REM Get the project root directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

echo [STEP 1] Checking Python Environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.12+ and try again
    pause
    exit /b 1
)
python --version
echo [OK] Python environment ready
echo.

echo [STEP 2] Installing Backend Dependencies...
pip install -r backend/requirements.txt --quiet
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo Attempting individual installation...
    pip install fastapi uvicorn pydantic numpy pandas scipy pvlib --quiet
)
echo [OK] Backend dependencies installed
echo.

echo [STEP 3] Installing Frontend Dependencies...
cd frontend
npm install --quiet
if errorlevel 1 (
    echo ERROR: npm installation failed
    cd ..
    pause
    exit /b 1
)
echo [OK] Frontend dependencies installed
cd ..
echo.

echo [STEP 4] Verifying Backend...
python -c "from backend.main import app; print('[OK] Backend imports successful')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Backend import failed
    pause
    exit /b 1
)
echo [OK] Backend verified
echo.

echo [STEP 5] Verifying Frontend React App...
if exist "frontend/node_modules/react" (
    echo [OK] React installed
) else (
    echo ERROR: React not found
    pause
    exit /b 1
)
echo.

echo ====================================================
echo   Setup Complete! Ready to Start
echo ====================================================
echo.
echo Starting services...
echo.

REM Start backend in new window
echo [STARTING] Backend API (Port 8000)...
start "FPV-Backend" cmd /k "cd /d "%PROJECT_ROOT%" && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 >nul

REM Start frontend in new window
echo [STARTING] Frontend React (Port 3000)...
start "FPV-Frontend" cmd /k "cd /d "%PROJECT_ROOT%frontend" && npm start"
timeout /t 3 >nul

echo.
echo ====================================================
echo   Services Started!
echo ====================================================
echo.
echo Backend API:     http://localhost:8000
echo Frontend App:    http://localhost:3000
echo API Docs:        http://localhost:8000/docs
echo.
echo Opening http://localhost:3000 in browser...
timeout /t 3 >nul
start http://localhost:3000

echo.
echo Press any key in this window to stop services...
pause

REM Kill the services
taskkill /FI "WINDOWTITLE eq FPV-Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq FPV-Frontend*" /T /F >nul 2>&1

echo Services stopped.
pause
