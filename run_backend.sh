#!/bin/bash
# FPV Nexus Dashboard - Quick Start Script for Mac/Linux

echo ""
echo "================================================"
echo "     FPV NEXUS DASHBOARD - QUICK START"
echo "================================================"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "[1/3] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.11+"
    exit 1
fi
python3 --version
echo "OK - Python found"

echo ""
echo "[2/3] Installing dependencies..."
python3 -m pip install -q fastapi uvicorn pydantic numpy pandas scipy pvlib
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi
echo "OK - All packages installed"

echo ""
echo "[3/3] Starting FastAPI Backend..."
echo ""
echo "Starting on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo "Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
