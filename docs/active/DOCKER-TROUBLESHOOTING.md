# Docker Troubleshooting Guide

## Common Issues

### 1. Container Name Conflict

**Error:**
```
Error response from daemon: Conflict. The container name "/dyn365hunter-postgres" is already in use
```

**Solution:**
```bash
# Force remove existing containers
docker rm -f dyn365hunter-postgres dyn365hunter-api

# Or use cleanup script
bash scripts/cleanup-docker.sh

# Then start fresh
docker-compose up -d
```

### 2. Service Not Running

**Error:**
```
service "api" is not running
```

**Solution:**
```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs api

# Restart services
docker-compose restart

# Or rebuild
docker-compose up -d --build
```

### 3. Script Not Found in WSL

**Error:**
```
bash: scripts/run-tests-docker.sh: No such file or directory
```

**Cause:** WSL'deki proje klasörü ile Windows'taki farklı.

**Solution:**
```bash
# Option 1: Use Windows path in WSL
cd /mnt/c/CursorPro/DomainHunterv3

# Option 2: Copy project to WSL (recommended for better performance)
cp -r /mnt/c/CursorPro/DomainHunterv3 ~/projects/dyn365hunterv3
cd ~/projects/dyn365hunterv3

# Option 3: Run commands directly (no script needed)
docker-compose exec api pytest tests/ -v
```

### 4. Database Connection Issues

**Error:**
```
Test database not available: postgresql://...
```

**Solution:**
```bash
# Check if PostgreSQL container is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready -U dyn365hunter
```

### 5. Port Already in Use

**Error:**
```
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**
```bash
# Find process using port
lsof -i :8000  # Linux/WSL
netstat -ano | findstr :8000  # Windows

# Stop conflicting service or change port in docker-compose.yml
```

## Quick Fixes

### Complete Reset

```bash
# Stop and remove everything
docker-compose down -v
docker rm -f dyn365hunter-postgres dyn365hunter-api 2>/dev/null || true

# Remove images (optional)
docker rmi dyn365hunterv3-api 2>/dev/null || true

# Start fresh
docker-compose up -d --build
```

### Check Container Status

```bash
# List all containers
docker ps -a

# Check specific container
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f postgres
```

### Run Tests Manually

```bash
# If containers are running
docker-compose exec api pytest tests/ -v

# If containers are not running, start first
docker-compose up -d
docker-compose exec api pytest tests/ -v
```

## Best Practices

1. **Always use cleanup script before rebuild:**
   ```bash
   bash scripts/cleanup-docker.sh
   docker-compose up -d --build
   ```

2. **Check container status before running tests:**
   ```bash
   docker-compose ps
   ```

3. **Use WSL project folder for better performance:**
   ```bash
   # Copy from Windows to WSL
   cp -r /mnt/c/CursorPro/DomainHunterv3 ~/projects/dyn365hunterv3
   cd ~/projects/dyn365hunterv3
   ```

4. **Keep containers running during development:**
   ```bash
   # Start once
   docker-compose up -d
   
   # Then just run tests
   docker-compose exec api pytest tests/ -v
   ```

