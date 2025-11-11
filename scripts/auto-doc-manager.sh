#!/bin/bash
# Auto Documentation Manager
# Automatically manages documentation lifecycle

set -e

DOCS_DIR="docs"
TODOS_DIR="$DOCS_DIR/todos"
ACTIVE_DIR="$DOCS_DIR/active"
ARCHIVE_DIR="$DOCS_DIR/archive"
PROMPTS_DIR="$DOCS_DIR/prompts"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function check_completed_todos() {
    echo -e "${BLUE}Checking for completed TODOs...${NC}"
    
    local archived=0
    for todo in "$TODOS_DIR"/*.md; do
        if [ -f "$todo" ]; then
            local filename=$(basename "$todo")
            # Skip README
            if [[ "$filename" == "README.md" ]]; then
                continue
            fi
            
            # Check if status is "Completed"
            if grep -q "^\*\*Status\*\*: Completed" "$todo"; then
                echo -e "${YELLOW}Found completed TODO: $filename${NC}"
                scripts/manage_docs.sh archive-todo "$filename"
                archived=$((archived + 1))
            fi
        fi
    done
    
    if [ $archived -eq 0 ]; then
        echo "✅ No completed TODOs to archive"
    else
        echo -e "${GREEN}✅ Archived $archived TODO(s)${NC}"
    fi
}

function check_active_count() {
    local count=$(find "$ACTIVE_DIR" -type f ! -name "README.md" 2>/dev/null | wc -l)
    
    if [ $count -gt 7 ]; then
        echo -e "${YELLOW}⚠️  Warning: $count active files (recommended: < 7)${NC}"
        echo "   Consider archiving old documentation"
        return 1
    else
        echo -e "${GREEN}✅ Active files: $count (OK)${NC}"
        return 0
    fi
}

function check_old_prompts() {
    echo -e "${BLUE}Checking for old prompts (7+ days)...${NC}"
    
    local today=$(date +%s)
    local archived=0
    
    for prompt in "$PROMPTS_DIR"/*.md; do
        if [ -f "$prompt" ]; then
            local filename=$(basename "$prompt")
            # Skip README
            if [[ "$filename" == "README.md" ]]; then
                continue
            fi
            
            # Extract date from filename (YYYY-MM-DD-)
            if [[ "$filename" =~ ^([0-9]{4}-[0-9]{2}-[0-9]{2})- ]]; then
                local prompt_date="${BASH_REMATCH[1]}"
                local prompt_timestamp=$(date -d "$prompt_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$prompt_date" +%s 2>/dev/null || echo 0)
                
                if [ $prompt_timestamp -gt 0 ]; then
                    local days_old=$(( (today - prompt_timestamp) / 86400 ))
                    
                    if [ $days_old -gt 7 ]; then
                        # Check if prompt is still referenced (simple check)
                        local still_referenced=$(grep -r "$filename" "$ACTIVE_DIR" "$TODOS_DIR" 2>/dev/null | wc -l)
                        
                        if [ $still_referenced -eq 0 ]; then
                            echo -e "${YELLOW}Found old unreferenced prompt: $filename (${days_old} days old)${NC}"
                            scripts/manage_docs.sh archive-prompt "$filename"
                            archived=$((archived + 1))
                        fi
                    fi
                fi
            fi
        fi
    done
    
    if [ $archived -eq 0 ]; then
        echo "✅ No old prompts to archive"
    else
        echo -e "${GREEN}✅ Archived $archived old prompt(s)${NC}"
    fi
}

function auto_cleanup() {
    echo -e "${BLUE}🧹 Running automatic cleanup...${NC}"
    echo ""
    
    check_completed_todos
    echo ""
    
    check_active_count
    echo ""
    
    check_old_prompts
    echo ""
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

function show_status() {
    echo -e "${BLUE}📊 Documentation Status${NC}"
    echo "===================="
    echo ""
    
    scripts/manage_docs.sh list
    
    echo -e "${BLUE}Active TODO Count:${NC}"
    local todo_count=$(find "$TODOS_DIR" -type f ! -name "README.md" 2>/dev/null | wc -l)
    echo "  $todo_count TODO(s)"
    echo ""
    
    echo -e "${BLUE}Active Prompt Count:${NC}"
    local prompt_count=$(find "$PROMPTS_DIR" -type f ! -name "README.md" 2>/dev/null | wc -l)
    echo "  $prompt_count prompt(s)"
    echo ""
}

# Main
case "$1" in
    cleanup)
        auto_cleanup
        ;;
    status)
        show_status
        ;;
    check-todos)
        check_completed_todos
        ;;
    check-prompts)
        check_old_prompts
        ;;
    *)
        echo "Auto Documentation Manager"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  cleanup       - Run automatic cleanup (archive completed TODOs, old prompts)"
        echo "  status       - Show documentation status"
        echo "  check-todos   - Check and archive completed TODOs"
        echo "  check-prompts - Check and archive old prompts"
        echo ""
        echo "Examples:"
        echo "  $0 cleanup      # Full automatic cleanup"
        echo "  $0 status       # Show current status"
        echo "  $0 check-todos  # Archive completed TODOs only"
        ;;
esac

