# Backend Dockerfile for Legal Combines OS
# Build context: project root (legal-combines-os/)
# Keeps `backend/` as a package so both relative (from ..models) and
# absolute (from backend.models) imports resolve via `uvicorn backend.main:app`.
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code (preserves the backend package layout)
COPY backend/ ./backend/

# Create non-root user
RUN useradd -m -u 1000 legaluser && chown -R legaluser:legaluser /app
USER legaluser

EXPOSE 8000

# Run as a module so `backend` is an importable package
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]