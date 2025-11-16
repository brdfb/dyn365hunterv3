#!/bin/bash
# G21 Phase 0: Git Tag Script
# Creates a git tag for pre-refactor snapshot

set -e

TAG_NAME="pre-refactor-v1.0.0"

echo "🔄 G21 Phase 0: Creating git tag..."
echo "🏷️  Tag name: ${TAG_NAME}"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed or not in PATH"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if tag already exists
if git rev-parse "${TAG_NAME}" > /dev/null 2>&1; then
    echo "⚠️  Warning: Tag ${TAG_NAME} already exists"
    read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "${TAG_NAME}"
        if git rev-parse --verify "refs/remotes/origin/${TAG_NAME}" > /dev/null 2>&1; then
            echo "⚠️  Warning: Tag exists on remote. You may need to delete it manually:"
            echo "   git push origin :refs/tags/${TAG_NAME}"
        fi
    else
        echo "❌ Aborted: Tag already exists"
        exit 1
    fi
fi

# Get current commit hash
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "📍 Current commit: ${CURRENT_COMMIT}"
echo "🌿 Current branch: ${CURRENT_BRANCH}"

# Create tag with message
git tag -a "${TAG_NAME}" -m "G21 Pre-Refactor Snapshot

Created before Architecture Refactor (G21).
This tag marks the state before removing CRM-lite features (Notes/Tags/Favorites)
and adding Sales Engine.

Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Commit: ${CURRENT_COMMIT}
Branch: ${CURRENT_BRANCH}"

echo "✅ Tag created successfully!"

# Ask if user wants to push to remote
read -p "Push tag to remote? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin "${TAG_NAME}"
    echo "✅ Tag pushed to remote"
else
    echo "ℹ️  Tag created locally. Push manually with: git push origin ${TAG_NAME}"
fi

echo ""
echo "✅ Phase 0.2: Git tag completed"
echo "📝 Next step: Collect usage metrics (scripts/g21_phase0_metrics.sh)"

