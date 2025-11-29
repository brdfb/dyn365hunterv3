# 🏗️ Environment Architecture - Hunter v1.0

**Tarih**: 2025-01-30  
**Durum**: ✅ **ACTIVE**

---

## 📊 Mevcut Ortam Yapısı

### Host System
- **OS**: Windows 10/11 (NT 10.0-26200)
- **Shell**: Git Bash (MINGW64)
- **Docker**: Docker Desktop (Windows)
- **Docker Context**: `desktop-linux` (WSL2 backend)

### Container Runtime
- **Platform**: WSL2 (Windows Subsystem for Linux 2)
- **Linux Kernel**: `6.6.87.2-microsoft-standard-WSL2`
- **Architecture**: x86_64

---

## 🐳 Docker Containers

### Container Names (dyn365hunter-* prefix)

1. **dyn365hunter-api**
   - Image: `domainhunterv3-api`
   - Command: `uvicorn app.main:ap…`
   - Ports: `0.0.0.0:8000->8000/tcp`
   - Status: ✅ Healthy
   - Hostname: `8875f0ae282a` (Linux container)

2. **dyn365hunter-postgres**
   - Image: `postgres:15-alpine`
   - Ports: `0.0.0.0:5432->5432/tcp`
   - Status: ✅ Healthy
   - Hostname: `bc15189e7a59` (Linux container)

3. **dyn365hunter-redis**
   - Image: `redis:7-alpine`
   - Ports: `0.0.0.0:6379->6379/tcp`
   - Status: ✅ Healthy

4. **dyn365hunter-worker**
   - Image: `domainhunterv3-worker`
   - Command: `celery -A app.core.…`
   - Status: ✅ Running

### Network
- **Network Name**: `dyn365hunter-network`
- **Type**: Docker bridge network
- **All containers connected**: ✅

---

## 🔄 Çalışma Ortamı Detayları

### Host → Container Flow

```
Windows PC (Local)
    ↓
Docker Desktop (Windows)
    ↓
WSL2 (Linux Kernel 6.6.87.2)
    ↓
Docker Containers (Linux)
    ├── dyn365hunter-api (Linux)
    ├── dyn365hunter-postgres (Linux)
    ├── dyn365hunter-redis (Linux)
    └── dyn365hunter-worker (Linux)
```

### Network Access

- **From Windows Host**: `localhost:8000` → `dyn365hunter-api:8000`
- **From Windows Host**: `localhost:5432` → `dyn365hunter-postgres:5432`
- **From Windows Host**: `localhost:6379` → `dyn365hunter-redis:6379`
- **Container-to-Container**: `dyn365hunter-network` (internal Docker network)

---

## 📍 Lokasyon

### Development Environment
- **Host**: Local Windows PC (`DESKTOP-F2SRPAF`)
- **Docker**: Docker Desktop (Windows)
- **Runtime**: WSL2 (Linux containers)
- **Network**: Local Docker network
- **Access**: `localhost:8000` (from Windows)

### Production Environment
- **Status**: ⚠️ **BELİRLENMEMİŞ**
- **Lokasyon**: Henüz karar verilmedi

---

## 🎯 Özet

**Soru**: "Bizim çalıştığımız ortam benim local PC mi yoksa benim PC'deki WSL mi?"

**Cevap**: 
- ✅ **Local Windows PC** üzerinde çalışıyoruz
- ✅ **Docker Desktop** (Windows) kullanıyoruz
- ✅ **WSL2** Docker'ın backend'i olarak kullanılıyor (container'lar WSL2 Linux kernel üzerinde çalışıyor)
- ✅ **Container'lar**: `dyn365hunter-*` prefix'i ile isimlendirilmiş (api, postgres, redis, worker)

**Yani**:
- Host: Windows PC (local)
- Container Runtime: WSL2 (Linux)
- Container'lar: Linux containers (WSL2 üzerinde)

---

## 🔍 Container Detayları

### API Container
```bash
# Container hostname
docker-compose exec api hostname
# Output: 8875f0ae282a

# Container OS
docker-compose exec api uname -a
# Output: Linux 8875f0ae282a 6.6.87.2-microsoft-standard-WSL2
```

### PostgreSQL Container
```bash
# Container hostname
docker-compose exec postgres hostname
# Output: bc15189e7a59

# Container OS
docker-compose exec postgres uname -a
# Output: Linux bc15189e7a59 6.6.87.2-microsoft-standard-WSL2
```

---

## 📝 Notlar

1. **WSL2**: Docker Desktop'ın backend'i olarak kullanılıyor
2. **Container'lar**: Linux containers (WSL2 üzerinde çalışıyor)
3. **Network**: Docker bridge network (`dyn365hunter-network`)
4. **Access**: Windows'tan `localhost:8000` ile erişilebilir
5. **Container Names**: `dyn365hunter-*` prefix'i ile isimlendirilmiş

---

**Last Updated**: 2025-01-30  
**Status**: ✅ **ACTIVE** - Development environment çalışıyor

