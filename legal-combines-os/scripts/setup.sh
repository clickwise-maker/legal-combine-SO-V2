#!/bin/bash
# scripts/setup.sh
# Setup script for Legal Combines OS development environment

set -e

echo "=== Legal Combines OS — Setup ==="

# Backend dependencies
echo "[1/4] Installing backend dependencies..."
pip install -r backend/requirements.txt

# Frontend dependencies
echo "[2/4] Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps
cd ..

# Environment file
echo "[3/4] Checking .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env from .env.example — edit it with your real secrets."
else
    echo "  .env already exists."
fi

# Database tables
echo "[4/4] Initializing database tables (requires DB running)..."
python -c "from backend.utils.database import Database; Database.init_db(); print('  Tables created.')" || \
    echo "  WARNING: DB init skipped — start PostgreSQL first."

echo ""
echo "=== Setup complete ==="
echo "Start backend:  uvicorn backend.main:app --reload"
echo "Start frontend: cd frontend && npm run dev"