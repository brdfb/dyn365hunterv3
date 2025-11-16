#!/bin/bash
# G21 Phase 0: Usage Metrics Collection Script
# Collects endpoint usage metrics for Notes/Tags/Favorites endpoints

set -e

METRICS_DIR="docs/g21-phase0-metrics"
METRICS_FILE="${METRICS_DIR}/usage_metrics_$(date +%Y%m%d_%H%M%S).json"

# Create metrics directory if it doesn't exist
mkdir -p "${METRICS_DIR}"

echo "🔄 G21 Phase 0: Collecting usage metrics..."
echo "📁 Metrics file: ${METRICS_FILE}"

# Check if we have access to database
if [ -f /.dockerenv ] || [ -n "${DOCKER_CONTAINER}" ]; then
    # Running inside Docker
    DB_HOST="postgres"
    DB_USER="dyn365hunter"
    DB_NAME="dyn365hunter"
    DB_CMD="docker-compose exec -T postgres psql -U ${DB_USER} -d ${DB_NAME}"
else
    # Running locally
    if [ -f .env ]; then
        source .env
        DB_CMD="psql ${HUNTER_DATABASE_URL}"
    else
        echo "❌ Error: .env file not found. Please set HUNTER_DATABASE_URL manually."
        exit 1
    fi
fi

# Create Python script for metrics collection
cat > /tmp/g21_metrics.py << 'EOF'
import json
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Get database URL
db_url = os.getenv("HUNTER_DATABASE_URL", "postgresql://dyn365hunter:dyn365hunter@localhost:5432/dyn365hunter")

# Create engine and session
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

try:
    metrics = {
        "collection_date": datetime.utcnow().isoformat(),
        "endpoints": {},
        "database_counts": {},
        "notes": {
            "total_notes": 0,
            "domains_with_notes": 0,
            "avg_notes_per_domain": 0.0,
            "recent_notes_7d": 0,
            "recent_notes_30d": 0
        },
        "tags": {
            "total_tags": 0,
            "domains_with_tags": 0,
            "avg_tags_per_domain": 0.0,
            "manual_tags": 0,
            "auto_tags": 0,
            "recent_tags_7d": 0,
            "recent_tags_30d": 0
        },
        "favorites": {
            "total_favorites": 0,
            "unique_users": 0,
            "domains_favorited": 0,
            "recent_favorites_7d": 0,
            "recent_favorites_30d": 0
        }
    }

    # Notes metrics
    notes_query = text("""
        SELECT 
            COUNT(*) as total_notes,
            COUNT(DISTINCT domain) as domains_with_notes,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as recent_7d,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_30d
        FROM notes
    """)
    notes_result = session.execute(notes_query).fetchone()
    if notes_result:
        metrics["notes"]["total_notes"] = notes_result[0] or 0
        metrics["notes"]["domains_with_notes"] = notes_result[1] or 0
        metrics["notes"]["recent_notes_7d"] = notes_result[2] or 0
        metrics["notes"]["recent_notes_30d"] = notes_result[3] or 0
        if notes_result[1] and notes_result[1] > 0:
            metrics["notes"]["avg_notes_per_domain"] = round(notes_result[0] / notes_result[1], 2)

    # Tags metrics
    tags_query = text("""
        SELECT 
            COUNT(*) as total_tags,
            COUNT(DISTINCT domain) as domains_with_tags,
            COUNT(*) FILTER (WHERE tag NOT IN ('security-risk', 'migration-ready', 'expire-soon', 'weak-spf', 'google-workspace', 'local-mx')) as manual_tags,
            COUNT(*) FILTER (WHERE tag IN ('security-risk', 'migration-ready', 'expire-soon', 'weak-spf', 'google-workspace', 'local-mx')) as auto_tags,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as recent_7d,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_30d
        FROM tags
    """)
    tags_result = session.execute(tags_query).fetchone()
    if tags_result:
        metrics["tags"]["total_tags"] = tags_result[0] or 0
        metrics["tags"]["domains_with_tags"] = tags_result[1] or 0
        metrics["tags"]["manual_tags"] = tags_result[2] or 0
        metrics["tags"]["auto_tags"] = tags_result[3] or 0
        metrics["tags"]["recent_tags_7d"] = tags_result[4] or 0
        metrics["tags"]["recent_tags_30d"] = tags_result[5] or 0
        if tags_result[1] and tags_result[1] > 0:
            metrics["tags"]["avg_tags_per_domain"] = round(tags_result[0] / tags_result[1], 2)

    # Favorites metrics
    favorites_query = text("""
        SELECT 
            COUNT(*) as total_favorites,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(DISTINCT domain) as domains_favorited,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as recent_7d,
            COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_30d
        FROM favorites
    """)
    favorites_result = session.execute(favorites_query).fetchone()
    if favorites_result:
        metrics["favorites"]["total_favorites"] = favorites_result[0] or 0
        metrics["favorites"]["unique_users"] = favorites_result[1] or 0
        metrics["favorites"]["domains_favorited"] = favorites_result[2] or 0
        metrics["favorites"]["recent_favorites_7d"] = favorites_result[3] or 0
        metrics["favorites"]["recent_favorites_30d"] = favorites_result[4] or 0

    # Database counts
    db_counts_query = text("""
        SELECT 
            (SELECT COUNT(*) FROM companies) as total_companies,
            (SELECT COUNT(*) FROM notes) as total_notes,
            (SELECT COUNT(*) FROM tags) as total_tags,
            (SELECT COUNT(*) FROM favorites) as total_favorites
    """)
    db_counts_result = session.execute(db_counts_query).fetchone()
    if db_counts_result:
        metrics["database_counts"] = {
            "total_companies": db_counts_result[0] or 0,
            "total_notes": db_counts_result[1] or 0,
            "total_tags": db_counts_result[2] or 0,
            "total_favorites": db_counts_result[3] or 0
        }

    # Note: API endpoint call counts would require application logs or APM
    # For now, we'll note that this requires manual collection from logs
    metrics["endpoints"] = {
        "note": "API endpoint call counts require application logs or APM. Manual collection needed.",
        "endpoints_to_monitor": [
            "POST /leads/{domain}/notes",
            "GET /leads/{domain}/notes",
            "PUT /leads/{domain}/notes/{note_id}",
            "DELETE /leads/{domain}/notes/{note_id}",
            "POST /leads/{domain}/tags",
            "GET /leads/{domain}/tags",
            "DELETE /leads/{domain}/tags/{tag_id}",
            "POST /leads/{domain}/favorite",
            "GET /leads?favorite=true",
            "DELETE /leads/{domain}/favorite"
        ]
    }

    print(json.dumps(metrics, indent=2))

finally:
    session.close()
EOF

# Run metrics collection
if [ -f /.dockerenv ] || [ -n "${DOCKER_CONTAINER}" ]; then
    # Running in Docker
    docker-compose exec -T api python /tmp/g21_metrics.py > "${METRICS_FILE}" 2>&1 || {
        echo "⚠️  Warning: Metrics collection failed. Creating placeholder file..."
        echo '{"error": "Metrics collection failed - manual collection required"}' > "${METRICS_FILE}"
    }
else
    # Running locally
    python3 /tmp/g21_metrics.py > "${METRICS_FILE}" 2>&1 || {
        echo "⚠️  Warning: Metrics collection failed. Creating placeholder file..."
        echo '{"error": "Metrics collection failed - manual collection required"}' > "${METRICS_FILE}"
    }
fi

# Cleanup
rm -f /tmp/g21_metrics.py

if [ -f "${METRICS_FILE}" ] && [ -s "${METRICS_FILE}" ]; then
    echo "✅ Metrics collected successfully!"
    echo "📊 Metrics file: ${METRICS_FILE}"
    echo ""
    echo "📋 Summary:"
    cat "${METRICS_FILE}" | python3 -m json.tool 2>/dev/null | head -20 || cat "${METRICS_FILE}" | head -20
else
    echo "❌ Error: Metrics file is empty or not created!"
    exit 1
fi

echo ""
echo "✅ Phase 0.3: Usage metrics collection completed"
echo "📝 Next step: Create dependency map (docs/g21-phase0-metrics/DEPENDENCY-MAP.md)"

