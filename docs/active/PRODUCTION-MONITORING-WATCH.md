# Production Monitoring Watch - Hunter v1.0.0

**Deployment Tarihi**: 2025-11-17  
**Watch Süresi**: İlk 1-2 gün (critical monitoring period)  
**Durum**: Active

---

## Monitoring Komutları

### Real-time Log Monitoring

```bash
# API ve Worker log'larını birlikte izle
docker compose logs -f api worker

# Sadece API log'ları
docker compose logs -f api

# Sadece Worker log'ları
docker compose logs -f worker

# Son 100 satır + follow
docker compose logs --tail=100 -f api worker
```

### Health Check Monitoring

```bash
# Health check'leri periyodik kontrol et
watch -n 5 'curl -s http://localhost:8000/healthz/ready | jq'

# Veya basit script
while true; do
  echo "=== $(date) ==="
  curl -s http://localhost:8000/healthz/ready | jq '.'
  sleep 10
done
```

---

## İzlenecek Kritik Sinyaller

### 1. DNS/WHOIS Timeout'ları

**Ne aramalı:**
```bash
docker compose logs api | grep -iE "(timeout|dns.*fail|whois.*fail)"
```

**Beklenen:** Minimal timeout (graceful degradation çalışmalı)  
**Kritik:** Sürekli timeout'lar, DNS çözümleme başarısızlıkları

### 2. Redis/DB Reconnect Denemeleri

**Ne aramalı:**
```bash
docker compose logs api worker | grep -iE "(connection.*refused|reconnect|redis.*fail|database.*fail)"
```

**Beklenen:** İlk başlangıçta bağlantı, sonra stabil  
**Kritik:** Sürekli reconnect denemeleri, connection pool exhaustion

### 3. Sentry'de Beklenmedik Spike

**Kontrol:**
- Sentry dashboard'u kontrol et
- Error rate'de ani artış var mı?
- Yeni error pattern'ler var mı?

**Beklenen:** Minimal errors (opsiyonel dependency warnings OK)  
**Kritik:** Yeni error pattern'ler, error rate > 1%

### 4. Worker Task Failures

**Ne aramalı:**
```bash
docker compose logs worker | grep -iE "(error|failed|traceback|exception)"
```

**Beklenen:** Task'lar başarıyla tamamlanıyor  
**Kritik:** Sürekli task failure'lar, dead letter queue birikmesi

### 5. API Response Time Degradation

**Kontrol:**
```bash
# Response time'ları izle
curl -w "\nTime: %{time_total}s\n" -o /dev/null -s http://localhost:8000/api/v1/leads
```

**Beklenen:** < 1s (leads endpoint)  
**Kritik:** Sürekli > 2s response time'lar

---

## Alerting Kriterleri

### Immediate Action Required (P0)

- ❌ Health check'ler fail oluyor (`/healthz/ready` → 503)
- ❌ Database connection kayboldu
- ❌ Redis connection kayboldu
- ❌ Worker sürekli crash oluyor
- ❌ API endpoint'ler 500 döndürüyor
- ❌ Sentry'de critical error spike (> 10 errors/min)

### Watch & Investigate (P1)

- ⚠️ DNS/WHOIS timeout rate > 10%
- ⚠️ Response time > 2s (sürekli)
- ⚠️ Worker task failure rate > 5%
- ⚠️ Redis/DB reconnect attempts (sürekli)
- ⚠️ Memory/CPU usage > 80% (sürekli)

### Normal (P2 - Log Only)

- ℹ️ Opsiyonel dependency warnings (ip2location, ip2proxy)
- ℹ️ Cache serialization warnings (date objects)
- ℹ️ Graceful degradation messages

---

## Daily Check Checklist (İlk 2 Gün)

### Gün 1 (2025-11-17)

- [ ] Health check'ler çalışıyor mu? (her 2 saatte bir)
- [ ] Log'larda kritik error var mı? (sabah/öğle/akşam)
- [ ] Sentry dashboard kontrol (sabah/akşam)
- [ ] Worker task'lar çalışıyor mu? (gün sonu)
- [ ] Response time'lar normal mi? (spot check)

### Gün 2 (2025-11-18)

- [ ] Health check'ler stabil mi?
- [ ] Error rate trend'i nasıl? (artıyor mu, azalıyor mu?)
- [ ] Worker task success rate?
- [ ] Database connection pool healthy mi?
- [ ] Redis cache hit rate?

---

## Troubleshooting Quick Reference

### Health Check Fail

```bash
# Container'ları kontrol et
docker compose ps

# Log'lara bak
docker compose logs api --tail=50

# Database bağlantısını test et
docker compose exec api python -c "from app.db.session import SessionLocal; db = SessionLocal(); db.execute('SELECT 1')"
```

### Worker Not Processing Tasks

```bash
# Worker durumunu kontrol et
docker compose exec worker celery -A app.core.celery_app.celery_app inspect ping

# Active task'ları kontrol et
docker compose exec worker celery -A app.core.celery_app.celery_app inspect active

# Worker log'larına bak
docker compose logs worker --tail=50
```

### High Error Rate

```bash
# Son 100 satırda error'ları say
docker compose logs api --tail=100 | grep -i error | wc -l

# Error pattern'lerini analiz et
docker compose logs api --tail=200 | grep -i error | sort | uniq -c | sort -rn
```

---

## Monitoring Dashboard (Opsiyonel)

Eğer monitoring dashboard kurulursa, şu metrikleri izle:

- **API**: Request rate, response time (P50, P95, P99), error rate
- **Database**: Connection pool usage, query time, deadlock count
- **Redis**: Connection count, cache hit rate, memory usage
- **Worker**: Task success rate, task duration, queue length

---

**Last Updated**: 2025-11-17  
**Status**: Active monitoring period

