#!/bin/bash
# Automatic documentation update script
# Runs after code changes to update CHANGELOG, README, etc.

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Checking for documentation updates...${NC}"

# Check if there are uncommitted changes
if git diff --quiet && git diff --cached --quiet; then
    echo "No changes detected. Skipping documentation update."
    exit 0
fi

# Check for completed phases (TODO files with "Completed" status)
TODOS_DIR="docs/todos"
if [ -d "$TODOS_DIR" ]; then
    for todo_file in "$TODOS_DIR"/*.md; do
        if [ -f "$todo_file" ]; then
            # Check if TODO is marked as completed
            if grep -q "status.*completed" "$todo_file" 2>/dev/null || \
               grep -q "✅.*Completed" "$todo_file" 2>/dev/null; then
                phase=$(basename "$todo_file" .md)
                echo -e "${YELLOW}Found completed phase: $phase${NC}"
                echo "Run: scripts/manage_docs.sh phase-complete $phase"
            fi
        fi
    done
fi

# Check for new API endpoints (app/api/*.py)
API_DIR="app/api"
if [ -d "$API_DIR" ]; then
    new_endpoints=$(git diff --name-only HEAD -- "$API_DIR" 2>/dev/null || echo "")
    if [ -n "$new_endpoints" ]; then
        echo -e "${YELLOW}New API endpoints detected. Consider updating README.md${NC}"
    fi
fi

# Check for new test files
TEST_DIR="tests"
if [ -d "$TEST_DIR" ]; then
    new_tests=$(git diff --name-only HEAD -- "$TEST_DIR" 2>/dev/null || echo "")
    if [ -n "$new_tests" ]; then
        echo -e "${YELLOW}New test files detected. Consider updating CHANGELOG.md${NC}"
    fi
fi

echo -e "${GREEN}Documentation check complete.${NC}"
echo "Remember to:"
echo "  1. Update CHANGELOG.md for completed phases"
echo "  2. Update README.md Features section"
echo "  3. Archive completed TODO files"

