#!/bin/bash
# Production Deployment Script - Hunter v1.0
# Deploys Hunter v1.0 to production environment
#
# Usage:
#   bash scripts/deploy_production.sh [--dry-run] [--skip-backup] [--skip-tests]
#
# Options:
#   --dry-run        : Show what would be done without executing
#   --skip-backup    : Skip database backup (not recommended)
#   --skip-tests     : Skip smoke tests (not recommended)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
SKIP_BACKUP=false
SKIP_TESTS=false

for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            exit 1
            ;;
    esac
done

# Configuration
VERSION="v1.0.0"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-./backups}"
LOG_FILE="${LOG_FILE:-./logs/deploy_${TIMESTAMP}.log}"

# Create directories if they don't exist
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    log "${GREEN}✅ $1${NC}"
}

log_warning() {
    log "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    log "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local errors=0
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        errors=$((errors + 1))
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        errors=$((errors + 1))
    fi
    
    # Check required environment variables
    if [ -z "$DATABASE_URL" ]; then
        log_error "DATABASE_URL environment variable is not set"
        errors=$((errors + 1))
    fi
    
    if [ -z "$REDIS_URL" ]; then
        log_error "REDIS_URL environment variable is not set"
        errors=$((errors + 1))
    fi
    
    if [ "$errors" -gt 0 ]; then
        log_error "Prerequisites check failed. Please fix the errors above."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Database backup
backup_database() {
    if [ "$SKIP_BACKUP" = true ]; then
        log_warning "Skipping database backup (--skip-backup flag set)"
        return 0
    fi
    
    log_info "Creating database backup..."
    
    local backup_file="${BACKUP_DIR}/backup_pre_${VERSION}_${TIMESTAMP}.sql"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would create backup: $backup_file"
        return 0
    fi
    
    # Extract database connection details from DATABASE_URL
    # Format: postgresql://user:password@host:port/database
    if [[ "$DATABASE_URL" =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        local db_user="${BASH_REMATCH[1]}"
        local db_pass="${BASH_REMATCH[2]}"
        local db_host="${BASH_REMATCH[3]}"
        local db_port="${BASH_REMATCH[4]}"
        local db_name="${BASH_REMATCH[5]}"
        
        # Use pg_dump if available, otherwise use docker exec
        if command -v pg_dump &> /dev/null; then
            PGPASSWORD="$db_pass" pg_dump -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" > "$backup_file"
        else
            # Try using docker exec if postgres container is running
            if docker ps | grep -q postgres; then
                docker exec -e PGPASSWORD="$db_pass" $(docker ps | grep postgres | awk '{print $1}') \
                    pg_dump -U "$db_user" -d "$db_name" > "$backup_file"
            else
                log_error "Cannot create backup: pg_dump not available and postgres container not running"
                exit 1
            fi
        fi
        
        if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
            log_success "Database backup created: $backup_file"
        else
            log_error "Database backup failed or file is empty"
            exit 1
        fi
    else
        log_error "Invalid DATABASE_URL format. Expected: postgresql://user:password@host:port/database"
        exit 1
    fi
}

# Run Alembic migration
run_migration() {
    log_info "Running Alembic migration..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would run: alembic upgrade head"
        return 0
    fi
    
    # Check if using docker-compose or docker compose
    local docker_cmd="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        docker_cmd="docker compose"
    fi
    
    # Check current migration version
    log_info "Current migration version:"
    $docker_cmd exec -T api alembic current || log_warning "Could not get current migration version"
    
    # Run migration
    if $docker_cmd exec -T api alembic upgrade head; then
        log_success "Database migration completed"
        
        # Verify migration
        log_info "Verifying migration..."
        $docker_cmd exec -T api alembic current
    else
        log_error "Database migration failed"
        exit 1
    fi
}

# Build and deploy
deploy_application() {
    log_info "Building and deploying application..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would run: docker-compose build --no-cache api"
        log_info "[DRY RUN] Would run: docker-compose up -d"
        return 0
    fi
    
    # Check if using docker-compose or docker compose
    local docker_cmd="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        docker_cmd="docker compose"
    fi
    
    # Build
    log_info "Building Docker image..."
    if $docker_cmd build --no-cache api; then
        log_success "Docker image built successfully"
    else
        log_error "Docker build failed"
        exit 1
    fi
    
    # Deploy
    log_info "Deploying application..."
    if $docker_cmd up -d; then
        log_success "Application deployed"
    else
        log_error "Deployment failed"
        exit 1
    fi
}

# Wait for services
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would wait for PostgreSQL and FastAPI"
        return 0
    fi
    
    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL (max 60s)..."
    local timeout=60
    local counter=0
    local docker_cmd="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        docker_cmd="docker compose"
    fi
    
    while [ $counter -lt $timeout ]; do
        if $docker_cmd exec -T postgres pg_isready -U dyn365hunter > /dev/null 2>&1; then
            log_success "PostgreSQL is ready"
            break
        fi
        sleep 1
        counter=$((counter + 1))
        echo -n "."
    done
    
    if [ $counter -eq $timeout ]; then
        log_error "PostgreSQL failed to start within ${timeout}s"
        exit 1
    fi
    
    echo ""
    
    # Wait for FastAPI
    log_info "Waiting for FastAPI (max 60s)..."
    counter=0
    while [ $counter -lt $timeout ]; do
        if curl -f http://localhost:8000/healthz/live > /dev/null 2>&1; then
            log_success "FastAPI is ready"
            break
        fi
        sleep 1
        counter=$((counter + 1))
        echo -n "."
    done
    
    if [ $counter -eq $timeout ]; then
        log_error "FastAPI failed to start within ${timeout}s"
        log_error "Check logs: $docker_cmd logs api"
        exit 1
    fi
    
    echo ""
}

# Run smoke tests
run_smoke_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "Skipping smoke tests (--skip-tests flag set)"
        return 0
    fi
    
    log_info "Running smoke tests..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would run smoke tests"
        return 0
    fi
    
    local errors=0
    
    # Test health endpoints
    log_info "Testing health endpoints..."
    if curl -f http://localhost:8000/healthz/live > /dev/null 2>&1; then
        log_success "Liveness probe: OK"
    else
        log_error "Liveness probe: FAILED"
        errors=$((errors + 1))
    fi
    
    if curl -f http://localhost:8000/healthz/ready > /dev/null 2>&1; then
        log_success "Readiness probe: OK"
    else
        log_error "Readiness probe: FAILED"
        errors=$((errors + 1))
    fi
    
    # Test core endpoints
    log_info "Testing core endpoints..."
    if curl -f http://localhost:8000/api/v1/leads > /dev/null 2>&1; then
        log_success "Leads endpoint: OK"
    else
        log_error "Leads endpoint: FAILED"
        errors=$((errors + 1))
    fi
    
    # Test Sales Engine endpoint
    log_info "Testing Sales Engine endpoint..."
    # Use a test domain (this will return 404 if domain doesn't exist, but endpoint should be accessible)
    if curl -f http://localhost:8000/api/v1/leads/test.example.com/sales-summary > /dev/null 2>&1; then
        log_success "Sales Engine endpoint: OK"
    else
        # 404 is acceptable for non-existent domain
        local status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/leads/test.example.com/sales-summary)
        if [ "$status_code" = "404" ]; then
            log_success "Sales Engine endpoint: OK (404 for non-existent domain is expected)"
        else
            log_error "Sales Engine endpoint: FAILED (status: $status_code)"
            errors=$((errors + 1))
        fi
    fi
    
    if [ $errors -gt 0 ]; then
        log_error "Smoke tests failed ($errors errors)"
        exit 1
    fi
    
    log_success "All smoke tests passed"
}

# Main deployment flow
main() {
    log ""
    log "=========================================================="
    log "🚀 Hunter v1.0 Production Deployment"
    log "=========================================================="
    log ""
    log "Version: $VERSION"
    log "Timestamp: $TIMESTAMP"
    log "Log file: $LOG_FILE"
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi
    
    log ""
    
    # Pre-deployment checks
    check_prerequisites
    
    # Backup
    backup_database
    
    # Migration
    run_migration
    
    # Deploy
    deploy_application
    
    # Wait for services
    wait_for_services
    
    # Smoke tests
    run_smoke_tests
    
    # Success
    log ""
    log "=========================================================="
    log_success "🎉 Deployment Complete!"
    log "=========================================================="
    log ""
    log "📋 Access URLs:"
    log "   - API: http://localhost:8000"
    log "   - API Docs: http://localhost:8000/docs"
    log "   - Health Check: http://localhost:8000/healthz"
    log "   - Mini UI: http://localhost:8000/mini-ui/"
    log ""
    log "📊 Useful commands:"
    log "   - View logs: docker-compose logs -f api"
    log "   - Check health: curl http://localhost:8000/healthz"
    log "   - Rollback: See docs/active/ROLLBACK-PLAN.md"
    log ""
}

# Run main function
main

