#!/bin/bash
source venv/bin/activate
echo "[INFO] Starting FastAPI backend..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

cd dashboard || exit 1
echo "[INFO] Serving React dashboard on http://localhost:3000"
npm serve -s dist -l 3000