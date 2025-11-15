# Production Engineering Guide v1

**Tarih**: 2025-01-28  
**Versiyon**: 1.0.0  
**Durum**: Active (Production Operations Guide)  
**İlgili Dokümanlar**: 
- [Production Readiness Critique v2](./PRODUCTION-READINESS-CRITIQUE-V2.md)
- [Development Environment Guide](./DEVELOPMENT-ENVIRONMENT.md)

---

## 📋 Genel Bakış

Bu doküman, **production ortamında** Dyn365Hunter'ın operasyonel yönetimi için SRE (Site Reliability Engineering) pratiklerini içerir:

- ✅ Health checks & probes (liveness/readiness/startup)
- ✅ Monitoring & alerting
- ✅ Logging & observability
- ✅ Deployment strategies
- ✅ Incident response
- ✅ Runbook (common operations)

---

## 🏥 Health Checks & Probes

### Endpoint'ler

| Endpoint | Amaç | Kubernetes Probe | HTTP Status |
|----------|------|------------------|-------------|
| `/healthz/live` | Liveness check | `livenessProbe` | 200 (always) |
| `/healthz/ready` | Readiness check | `readinessProbe` | 200 (ready) / 503 (not ready) |
| `/healthz/startup` | Startup check | `startupProbe` | 200 (ready) / 503 (not ready) |
| `/healthz` | Legacy (backward compat) | - | 200 (always) |

### Liveness Probe

**Amaç:** Uygulama çalışıyor mu?

**Davranış:**
- Kubernetes container'ı restart eder eğer fail olursa
- Deadlock veya infinite loop durumunda container yeniden başlatılır

**Endpoint:** `GET /healthz/live`

**Response:**
```json
{
  "status": "alive"
}
```

**Kubernetes Config:**
```yaml
livenessProbe:
  httpGet:
    path: /healthz/live
    port: 8000
  initialDelaySeconds: 30  # İlk 30 saniye bekle
  periodSeconds: 10        # Her 10 saniyede bir kontrol et
  timeoutSeconds: 5        # 5 saniye timeout
  failureThreshold: 3      # 3 kez fail olursa restart
```

---

### Readiness Probe

**Amaç:** Uygulama trafik alabilir mi?

**Davranış:**
- Kubernetes trafik göndermeyi durdurur eğer fail olursa
- DB veya Redis down olduğunda trafik alınmaz (graceful degradation)

**Endpoint:** `GET /healthz/ready`

**Checks:**
- ✅ Database connection (ping)
- ✅ Redis connection (ping)

**Response (Success):**
```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "redis": true
  },
  "environment": "production"
}
```

**Response (Failure):**
```json
HTTP 503 Service Unavailable
{
  "detail": "Database unavailable: connection refused"
}
```

**Kubernetes Config:**
```yaml
readinessProbe:
  httpGet:
    path: /healthz/ready
    port: 8000
  initialDelaySeconds: 10  # İlk 10 saniye bekle
  periodSeconds: 5         # Her 5 saniyede bir kontrol et
  timeoutSeconds: 3        # 3 saniye timeout
  failureThreshold: 3      # 3 kez fail olursa trafik kes
```

---

### Startup Probe

**Amaç:** İlk başlangıçta uygulama hazır mı?

**Davranış:**
- Kubernetes ilk başlangıçta daha uzun süre bekler
- Migration veya initialization süreçleri için zaman tanır

**Endpoint:** `GET /healthz/startup`

**Kubernetes Config:**
```yaml
startupProbe:
  httpGet:
    path: /healthz/startup
    port: 8000
  initialDelaySeconds: 0   # Hemen başla
  periodSeconds: 5         # Her 5 saniyede bir kontrol et
  timeoutSeconds: 3        # 3 saniye timeout
  failureThreshold: 30     # 30 kez fail olabilir (150 saniye max)
```

**Not:** Startup probe başarılı olduktan sonra liveness/readiness probe'lar devreye girer.

---

### Legacy Health Check

**Endpoint:** `GET /healthz`

**Amaç:** Backward compatibility (eski client'lar için)

**Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "redis": "connected",
  "environment": "production"
}
```

**Not:** Bu endpoint her zaman 200 döner (hata olsa bile). Production'da `/healthz/ready` kullanılmalı.

---

## 📊 Monitoring & Alerting

### Metrics to Track

#### Application Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `http_requests_total` | Counter | Total HTTP requests | - |
| `http_request_duration_seconds` | Histogram | Request latency | P95 > 1s |
| `http_requests_errors_total` | Counter | Error rate | Error rate > 5% |
| `db_connection_pool_size` | Gauge | Active DB connections | Pool size > 80% |
| `redis_connection_pool_size` | Gauge | Active Redis connections | Pool size > 80% |
| `celery_tasks_total` | Counter | Total Celery tasks | - |
| `celery_tasks_failed_total` | Counter | Failed Celery tasks | Failure rate > 10% |

#### Infrastructure Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `cpu_usage_percent` | Gauge | CPU usage | > 80% |
| `memory_usage_bytes` | Gauge | Memory usage | > 80% |
| `disk_usage_percent` | Gauge | Disk usage | > 85% |
| `db_connection_count` | Gauge | DB connections | > 80% of max |

#### Business Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `domains_scanned_total` | Counter | Total domains scanned | - |
| `domains_scanned_failed_total` | Counter | Failed scans | Failure rate > 5% |
| `leads_ingested_total` | Counter | Total leads ingested | - |
| `alerts_triggered_total` | Counter | Total alerts triggered | - |

---

### Prometheus Integration

**FastAPI Prometheus Middleware:**

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Database connection pool size'
)

# Middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

**Prometheus Scrape Config:**
```yaml
scrape_configs:
  - job_name: 'dyn365hunter-api'
    scrape_interval: 15s
    metrics_path: '/metrics'
    static_configs:
      - targets: ['api:8000']
```

---

### Alerting Rules (Prometheus)

```yaml
groups:
  - name: dyn365hunter_alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} (threshold: 0.05)"

      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s (threshold: 1s)"

      # DB connection pool exhaustion
      - alert: DBConnectionPoolExhausted
        expr: db_connection_pool_size / db_connection_pool_max > 0.8
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "DB connection pool nearly exhausted"
          description: "Pool usage is {{ $value }}%"

      # Celery task failure rate
      - alert: HighCeleryTaskFailureRate
        expr: rate(celery_tasks_failed_total[5m]) / rate(celery_tasks_total[5m]) > 0.1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High Celery task failure rate"
          description: "Failure rate is {{ $value }}%"
```

---

## 📝 Logging & Observability

### Structured Logging

**Format:** JSON (production), human-readable (development)

**Log Levels:**
- `DEBUG`: Development only (detailed tracing)
- `INFO`: Normal operations (requests, scans, etc.)
- `WARNING`: Recoverable errors (timeouts, retries)
- `ERROR`: Unrecoverable errors (exceptions, failures)
- `CRITICAL`: System failures (DB down, Redis down)

**PII Policy:**
- ✅ **Log'lanabilir**: domain, provider, segment, score, scan_status
- ❌ **Log'lanamaz**: email, company_name, contact_emails (hash veya id kullan)

**Example:**
```python
import structlog

logger = structlog.get_logger()

# ✅ Good
logger.info(
    "scan_completed",
    domain="example.com",
    score=85,
    segment="Migration",
    scan_status="success"
)

# ❌ Bad (PII)
logger.info(
    "scan_completed",
    email="user@example.com",  # ❌ YASAK
    company_name="Example Inc"  # ❌ YASAK
)
```

---

### Log Aggregation

**ELK Stack (Elasticsearch, Logstash, Kibana):**

```yaml
# docker-compose.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
  
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

**Logstash Config:**
```ruby
input {
  http {
    port => 5044
    codec => json
  }
}

filter {
  if [level] == "ERROR" {
    mutate {
      add_tag => [ "error" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "dyn365hunter-%{+YYYY.MM.dd}"
  }
}
```

---

## 🚀 Deployment Strategies

### Blue-Green Deployment

**Strateji:** İki production environment (blue/green), trafik switch edilir.

**Avantajlar:**
- Zero-downtime deployment
- Instant rollback
- Testing yeni versiyon production'da

**Kubernetes Config:**
```yaml
# Blue deployment (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dyn365hunter-api-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dyn365hunter-api
      version: blue
  template:
    metadata:
      labels:
        app: dyn365hunter-api
        version: blue
    spec:
      containers:
      - name: api
        image: dyn365hunter:v1.0.0

---
# Green deployment (new)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dyn365hunter-api-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dyn365hunter-api
      version: green
  template:
    metadata:
      labels:
        app: dyn365hunter-api
        version: green
    spec:
      containers:
      - name: api
        image: dyn365hunter:v1.1.0

---
# Service (switch between blue/green)
apiVersion: v1
kind: Service
metadata:
  name: dyn365hunter-api
spec:
  selector:
    app: dyn365hunter-api
    version: blue  # Switch to 'green' for new version
  ports:
  - port: 80
    targetPort: 8000
```

**Deployment Script:**
```bash
#!/bin/bash
# deploy_blue_green.sh

NEW_VERSION="v1.1.0"
CURRENT_VERSION=$(kubectl get svc dyn365hunter-api -o jsonpath='{.spec.selector.version}')

if [ "$CURRENT_VERSION" == "blue" ]; then
  NEW_COLOR="green"
  OLD_COLOR="blue"
else
  NEW_COLOR="blue"
  OLD_COLOR="green"
fi

# Deploy new version
kubectl set image deployment/dyn365hunter-api-$NEW_COLOR api=dyn365hunter:$NEW_VERSION

# Wait for rollout
kubectl rollout status deployment/dyn365hunter-api-$NEW_COLOR

# Switch traffic
kubectl patch svc dyn365hunter-api -p '{"spec":{"selector":{"version":"'$NEW_COLOR'"}}}'

# Verify
sleep 10
kubectl get pods -l version=$NEW_COLOR

echo "✅ Deployment complete. New version: $NEW_COLOR"
```

---

### Rolling Update (Default Kubernetes)

**Strateji:** Pod'lar tek tek güncellenir (zero-downtime).

**Kubernetes Config:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dyn365hunter-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max 1 extra pod during update
      maxUnavailable: 0  # Zero downtime
  template:
    spec:
      containers:
      - name: api
        image: dyn365hunter:v1.0.0
```

**Deployment:**
```bash
kubectl set image deployment/dyn365hunter-api api=dyn365hunter:v1.1.0
kubectl rollout status deployment/dyn365hunter-api
```

**Rollback:**
```bash
kubectl rollout undo deployment/dyn365hunter-api
```

---

## 🚨 Incident Response

### Runbook: Common Issues

#### 1. Database Connection Pool Exhausted

**Symptom:**
- `db_connection_pool_size` metric > 80%
- HTTP 503 errors
- Slow response times

**Diagnosis:**
```bash
# Check DB connections
kubectl exec -it <pod-name> -- psql -U dyn365hunter -c "SELECT count(*) FROM pg_stat_activity;"

# Check connection pool metrics
curl http://localhost:8000/metrics | grep db_connection_pool
```

**Resolution:**
1. Increase pool size (temporary):
   ```python
   # app/db/session.py
   pool_size=30,  # Increase from 20
   max_overflow=15  # Increase from 10
   ```

2. Check for connection leaks:
   ```bash
   # Find long-running queries
   psql -U dyn365hunter -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;"
   ```

3. Restart pods (if needed):
   ```bash
   kubectl rollout restart deployment/dyn365hunter-api
   ```

---

#### 2. Redis Connection Failure

**Symptom:**
- `/healthz/ready` returns 503
- Celery tasks not processing
- Bulk scan jobs stuck

**Diagnosis:**
```bash
# Check Redis
kubectl exec -it redis-pod -- redis-cli ping

# Check Redis metrics
curl http://localhost:8000/metrics | grep redis
```

**Resolution:**
1. Check Redis pod status:
   ```bash
   kubectl get pods -l app=redis
   kubectl logs redis-pod
   ```

2. Restart Redis (if needed):
   ```bash
   kubectl delete pod redis-pod
   ```

3. Check Redis memory:
   ```bash
   kubectl exec -it redis-pod -- redis-cli INFO memory
   ```

---

#### 3. High Error Rate

**Symptom:**
- `http_requests_errors_total` > 5%
- Alert triggered
- User complaints

**Diagnosis:**
```bash
# Check error logs
kubectl logs -l app=dyn365hunter-api --tail=100 | grep ERROR

# Check error metrics
curl http://localhost:8000/metrics | grep http_requests_errors_total
```

**Resolution:**
1. Identify error pattern:
   ```bash
   # Most common errors
   kubectl logs -l app=dyn365hunter-api --tail=1000 | grep ERROR | sort | uniq -c | sort -rn
   ```

2. Check Sentry (if configured):
   - Review error dashboard
   - Check stack traces

3. Rollback if recent deployment:
   ```bash
   kubectl rollout undo deployment/dyn365hunter-api
   ```

---

#### 4. Celery Worker Not Processing Tasks

**Symptom:**
- Bulk scan jobs stuck in "pending"
- Celery task queue growing
- No worker logs

**Diagnosis:**
```bash
# Check Celery worker status
kubectl get pods -l app=celery-worker
kubectl logs celery-worker-pod

# Check Redis queue
kubectl exec -it redis-pod -- redis-cli LLEN celery
```

**Resolution:**
1. Restart Celery worker:
   ```bash
   kubectl rollout restart deployment/celery-worker
   ```

2. Check worker logs:
   ```bash
   kubectl logs celery-worker-pod --tail=100
   ```

3. Clear stuck tasks (if needed):
   ```bash
   kubectl exec -it redis-pod -- redis-cli FLUSHDB
   ```

---

## 📋 Checklist: Production Deployment

### Pre-Deployment

- [ ] All P0 items from [Production Readiness Critique v2](./PRODUCTION-READINESS-CRITIQUE-V2.md) completed
- [ ] Health checks implemented (`/healthz/live`, `/healthz/ready`, `/healthz/startup`)
- [ ] Monitoring configured (Prometheus, Grafana)
- [ ] Logging configured (ELK or similar)
- [ ] Error tracking configured (Sentry)
- [ ] Database migrations tested (Alembic - P1-1: Database Migration System)
- [ ] Alembic migration system verified (`alembic upgrade head`, `alembic current`)
- [ ] Load testing completed
- [ ] Backup strategy in place

### Deployment

- [ ] Blue-green or rolling update strategy chosen
- [ ] Deployment script tested in staging
- [ ] Rollback plan ready
- [ ] Monitoring dashboards open
- [ ] On-call engineer available

### Post-Deployment

- [ ] Health checks passing
- [ ] Error rate normal (< 1%)
- [ ] Latency normal (P95 < 500ms)
- [ ] All metrics normal
- [ ] Smoke tests passing
- [ ] User acceptance testing (if applicable)
- [ ] API versioning verified (v1 endpoints: `/api/v1/...`, legacy endpoints: `/...`) - P1-5: API Versioning
- [ ] Redis health verified (distributed rate limiting, caching layer) - P1-2, P1-3

---

## 🔧 Common Operations

### Database Backup

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d)
kubectl exec -it postgres-pod -- pg_dump -U dyn365hunter dyn365hunter > $BACKUP_DIR/db_backup_$DATE.sql

# Restore
kubectl exec -i postgres-pod -- psql -U dyn365hunter dyn365hunter < $BACKUP_DIR/db_backup_20250128.sql
```

### Alembic Migration (P1-1: Database Migration System)

```bash
# Run migrations
kubectl exec -it api-pod -- alembic upgrade head

# Check current migration version
kubectl exec -it api-pod -- alembic current

# View migration history
kubectl exec -it api-pod -- alembic history

# Rollback (if needed)
kubectl exec -it api-pod -- alembic downgrade -1
```

### Log Rotation

```yaml
# Kubernetes log rotation (via fluentd)
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
    </source>
    
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      index_name dyn365hunter-%{+YYYY.MM.dd}
    </match>
```

### Scaling

```bash
# Scale API pods
kubectl scale deployment dyn365hunter-api --replicas=5

# Scale Celery workers
kubectl scale deployment celery-worker --replicas=3

# Auto-scaling (HPA)
kubectl autoscale deployment dyn365hunter-api --min=3 --max=10 --cpu-percent=70
```

---

## 📚 References

- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [SRE Book](https://sre.google/sre-book/table-of-contents/)
- [12-Factor App](https://12factor.net/)

---

**Son Güncelleme**: 2025-01-28  
**Versiyon**: 1.0.0  
**Durum**: Active (Production Operations Guide)

