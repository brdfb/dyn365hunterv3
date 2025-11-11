#!/bin/bash
# Documentation Management Script
# Helps organize and archive documentation

set -e

DOCS_DIR="docs"
ACTIVE_DIR="$DOCS_DIR/active"
ARCHIVE_DIR="$DOCS_DIR/archive"
PROMPTS_DIR="$DOCS_DIR/prompts"
TODOS_DIR="$DOCS_DIR/todos"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function archive_file() {
    local file=$1
    local source_dir=$2
    local dest_dir=$3
    
    if [ ! -f "$source_dir/$file" ]; then
        echo "❌ File not found: $source_dir/$file"
        return 1
    fi
    
    local date=$(date +%Y-%m-%d)
    local archived_name="${date}-${file}"
    
    mv "$source_dir/$file" "$dest_dir/$archived_name"
    echo "✅ Archived: $file → $dest_dir/$archived_name"
}

function list_active() {
    echo -e "${GREEN}Active Documentation:${NC}"
    echo "==================="
    if [ -d "$ACTIVE_DIR" ] && [ "$(ls -A $ACTIVE_DIR 2>/dev/null)" ]; then
        ls -lh "$ACTIVE_DIR" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
    else
        echo "  (empty)"
    fi
    echo ""
}

function list_archived() {
    echo -e "${YELLOW}Archived Documentation:${NC}"
    echo "====================="
    if [ -d "$ARCHIVE_DIR" ] && [ "$(ls -A $ARCHIVE_DIR 2>/dev/null)" ]; then
        ls -lh "$ARCHIVE_DIR" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
    else
        echo "  (empty)"
    fi
    echo ""
}

function archive_todo() {
    local todo_file=$1
    if [ -z "$todo_file" ]; then
        echo "Usage: $0 archive-todo <todo-file>"
        echo "Example: $0 archive-todo G1-foundation.md"
        return 1
    fi
    
    archive_file "$todo_file" "$TODOS_DIR" "$ARCHIVE_DIR"
}

function archive_prompt() {
    local prompt_file=$1
    if [ -z "$prompt_file" ]; then
        echo "Usage: $0 archive-prompt <prompt-file>"
        echo "Example: $0 archive-prompt 2025-11-12-initial-setup.md"
        return 1
    fi
    
    archive_file "$prompt_file" "$PROMPTS_DIR" "$ARCHIVE_DIR"
}

function archive_active() {
    local file=$1
    if [ -z "$file" ]; then
        echo "Usage: $0 archive-active <file>"
        echo "Example: $0 archive-active ACTIONS.json"
        return 1
    fi
    
    archive_file "$file" "$ACTIVE_DIR" "$ARCHIVE_DIR"
}

function create_todo() {
    local phase=$1
    local name=$2
    
    if [ -z "$phase" ] || [ -z "$name" ]; then
        echo "Usage: $0 create-todo <phase> <name>"
        echo "Example: $0 create-todo G2 database-schema"
        return 1
    fi
    
    local date=$(date +%Y-%m-%d)
    local filename="${phase}-${name}.md"
    local filepath="$TODOS_DIR/$filename"
    
    cat > "$filepath" << EOF
# TODO: ${phase} - ${name}

**Date Created**: ${date}
**Status**: In Progress
**Phase**: ${phase}

## Tasks

- [ ] Task 1
- [ ] Task 2

## Notes

[Add notes here]
EOF
    
    echo "✅ Created TODO: $filepath"
}

function create_prompt() {
    local name=$1
    
    if [ -z "$name" ]; then
        echo "Usage: $0 create-prompt <name>"
        echo "Example: $0 create-prompt database-design"
        return 1
    fi
    
    local date=$(date +%Y-%m-%d)
    local filename="${date}-${name}.md"
    local filepath="$PROMPTS_DIR/$filename"
    
    cat > "$filepath" << EOF
# ${name}

**Date**: ${date}
**Context**: [Brief description]
**Status**: Active

## Prompt

[The actual prompt]

## Response Summary

[Key points from the response]

## Actions Taken

- [ ] Action 1
- [ ] Action 2

## Key Decisions

[Important decisions made]
EOF
    
    echo "✅ Created prompt: $filepath"
}

# Main command handler
case "$1" in
    list)
        list_active
        list_archived
        ;;
    archive-todo)
        archive_todo "$2"
        ;;
    archive-prompt)
        archive_prompt "$2"
        ;;
    archive-active)
        archive_active "$2"
        ;;
    create-todo)
        create_todo "$2" "$3"
        ;;
    create-prompt)
        create_prompt "$2"
        ;;
    *)
        echo "Documentation Management Script"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  list                    - List active and archived documentation"
        echo "  archive-todo <file>     - Archive a TODO file"
        echo "  archive-prompt <file>   - Archive a prompt file"
        echo "  archive-active <file>   - Archive an active documentation file"
        echo "  create-todo <phase> <name> - Create a new TODO file"
        echo "  create-prompt <name>    - Create a new prompt file"
        echo ""
        echo "Examples:"
        echo "  $0 list"
        echo "  $0 archive-todo G1-foundation.md"
        echo "  $0 create-todo G2 database-schema"
        echo "  $0 create-prompt api-design"
        ;;
esac

