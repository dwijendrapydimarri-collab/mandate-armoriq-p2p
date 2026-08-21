"""
MANDATE — Root Launch Entrypoint
Runs the unified FastAPI application (serving both the backend API and the compiled frontend)
on http://127.0.0.1:8008.

Usage:
    python run.py
    python run.py --port 8008 --host 0.0.0.0
"""

import sys
import os
import argparse
import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MANDATE Mission Control Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8008, help="Port to bind (default: 8008)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    # Ensure repository root is on sys.path
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    print(f"\n=======================================================")
    print(f"  MANDATE — Autonomous Procure-to-Pay Mission Control  ")
    print(f"  Server starting at http://{args.host}:{args.port}")
    print(f"  API Docs available at http://{args.host}:{args.port}/docs")
    print(f"=======================================================\n")

    uvicorn.run("backend.main:app", host=args.host, port=args.port, reload=args.reload)
