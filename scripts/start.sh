#!/bin/bash
source venv/bin/activate
echo "[INFO] Starting FastAPI backend..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

cd dashboard || exit 1

echo "[INFO] Installing React dependencies..."
npm install

echo "[INFO] Building React frontend..."
npm run build

echo "[INFO] Serving React dashboard on http://localhost:3000"
npx serve -s dist -l 3000