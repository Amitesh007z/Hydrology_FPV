"""
Vercel Python entrypoint.

This file exposes `app` at repository root so Vercel can detect and run
the FastAPI backend from this monorepo layout.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent
BACKEND_DIR = ROOT / "backend"

# Ensure backend-local imports like `thermal_data` resolve on Vercel.
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.main import app  # noqa: E402

