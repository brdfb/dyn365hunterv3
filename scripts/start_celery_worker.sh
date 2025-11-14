#!/bin/bash
# Start Celery worker for async task processing

# Set working directory
cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Start Celery worker
# -A: Celery app location
# -l: Log level
# --concurrency: Number of worker processes (5 recommended for DNS/WHOIS rate limiting)
# --max-tasks-per-child: Restart worker after N tasks (memory management)
celery -A app.core.celery_app.celery_app worker \
    --loglevel=info \
    --concurrency=5 \
    --max-tasks-per-child=50 \
    --time-limit=900 \
    --soft-time-limit=870

