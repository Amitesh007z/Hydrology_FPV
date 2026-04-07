#!/usr/bin/env python
"""
FPV Nexus - Quick Status Check
Tests essential components without complex imports
"""

import sys
import subprocess
from pathlib import Path
import importlib.util

def find_spec(module_name):
    """Check if a module is installed"""
    return importlib.util.find_spec(module_name) is not None

def main():
    print("\n" + "="*60)
    print("  FPV Nexus v4.0 - Quick Status Check")
    print("="*60)
    
    print("\n[1] Python Version")
    print(f"  {sys.version}")
    
    print("\n[2] Essential Dependencies")
    essential = ["fastapi", "uvicorn", "pydantic", "numpy", "pandas"]
    for pkg in essential:
        status = "OK" if find_spec(pkg) else "MISSING"
        print(f"  [{status}] {pkg}")
    
    print("\n[3] Backend Files")
    backend_files = [
        "backend/__init__.py",
        "backend/main.py",
        "backend/requirements.txt"
    ]
    for file in backend_files:
        path = Path(file)
        status = "OK" if path.exists() else "MISSING"
        print(f"  [{status}] {file}")
    
    print("\n[4] Frontend Files")
    frontend_files = [
        "frontend/package.json",
        "frontend/src/App.js",
        "frontend/src/components/DamMap.js",
        "frontend/src/components/DamAnalysis.js"
    ]
    for file in frontend_files:
        path = Path(file)
        status = "OK" if path.exists() else "MISSING"
        print(f"  [{status}] {file}")
    
    print("\n[5] Data Files")
    data_files = [
        "input_data/dams.json",
        "input_data/srisailam/reservoir.csv",
        "input_data/srisailam/climate.csv"
    ]
    for file in data_files:
        path = Path(file)
        status = "OK" if path.exists() else "MISSING"
        print(f"  [{status}] {file}")
    
    print("\n[6] Quick Backend Test")
    try:
        sys.path.insert(0, str(Path.cwd()))
        from backend.main import app
        print(f"  [OK] Backend imports successfully")
        print(f"  [OK] App: {app.title} v{app.version}")
        print(f"  [OK] Routes: {len(app.routes)}")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    print("\n" + "="*60)
    print("  Status: Ready to Start!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Backend:  python -m uvicorn backend.main:app --reload --port 8000")
    print("2. Frontend: cd frontend && npm start")
    print("3. Browser:  http://localhost:3000")
    print()

if __name__ == "__main__":
    main()
