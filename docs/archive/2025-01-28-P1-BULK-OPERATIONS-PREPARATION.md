# P1 Bulk Operations Hazırlığı

**Tarih**: 2025-01-28  
**Durum**: Hazırlık Tamamlandı  
**Amaç**: Bulk operations optimization için zemin hazırlamak (read-only analiz)

---

## 📋 Mevcut Bulk Scan Analizi

### ✅ Mevcut Bulk Scan Yapısı

#### 1. bulk_scan_task (Celery Task)
- **Lokasyon**: `app/core/tasks.py` (satır 194-306)
- **Tip**: Celery task (`@celery_app.task(bind=True)`)
- **Akış**: Sequential processing (her domain için ayrı transaction)
- **Rate Limiting**: DNS (10 req/s), WHOIS (5 req/s) - her domain için ayrı ayrı

**Kod Örneği:**
```python
@celery_app.task(bind=True)
def bulk_scan_task(self, job_id: str, is_rescan: bool = False):
    tracker = get_progress_tracker()
    db = SessionLocal()
    
    try:
        domain_list = tracker.get_domain_list(job_id)
        tracker.set_status(job_id, "running")
        
        processed = 0
        succeeded = 0
        failed = 0
        
        for domain in domain_list:  # Sequential processing
            try:
                if is_rescan:
                    result = rescan_domain(domain, db)
                else:
                    result = scan_single_domain(domain, db)  # Her domain için ayrı transaction
                
                processed += 1
                if result["success"]:
                    succeeded += 1
                else:
                    failed += 1
                
                tracker.update_progress(job_id, processed, succeeded, failed, error)
            except Exception as e:
                processed += 1
                failed += 1
                tracker.update_progress(job_id, processed, succeeded, failed, error)
        
        tracker.set_status(job_id, "completed")
    finally:
        db.close()
```

---

### ❌ Eksik Optimizasyonlar

#### 1. Batch Insert Yok
- **Sorun**: Her domain için ayrı `db.add()` ve `db.commit()`
- **Etki**: Yüksek - 100 domain → 100 transaction
- **Çözüm**: Batch insert (bulk insert - `bulk_insert_mappings()` veya `bulk_save_objects()`)

**Mevcut Kod:**
```python
# Her domain için ayrı transaction
for domain in domain_list:
    result = scan_single_domain(domain, db)  # İçinde db.commit() var
    # Her domain için ayrı DB write
```

**Optimize Edilmiş Kod:**
```python
# Batch processing
batch_size = 100
for i in range(0, len(domain_list), batch_size):
    batch = domain_list[i:i+batch_size]
    batch_results = []
    
    for domain in batch:
        result = scan_single_domain(domain, db, commit=False)  # commit=False
        batch_results.append(result)
    
    # Batch commit
    db.commit()  # Tek transaction
```

#### 2. Database Transaction Optimization Yok
- **Sorun**: Her domain için ayrı transaction
- **Etki**: Yüksek - Transaction overhead
- **Çözüm**: Batch'ler halinde commit (100 domain/batch)

#### 3. Memory Usage Optimization Yok
- **Sorun**: Tüm domain listesi memory'de
- **Etki**: Orta - Büyük listeler için memory sorunu
- **Çözüm**: Streaming - generator kullan

#### 4. Deadlock Prevention Strategy Yok
- **Sorun**: 2 worker aynı domain'leri scan ederse deadlock riski
- **Etki**: 🔴 **YÜKSEK** - Production'da sorun çıkarabilir
- **Çözüm**: Transaction timeout, retry logic, batch isolation

#### 5. Batch Failure Recovery Yok
- **Sorun**: Batch ortasında hata olursa tüm batch fail olur
- **Etki**: Yüksek - Partial commit yok
- **Çözüm**: Partial commit log, failed batch'leri retry

#### 6. Partial Commit Log Yok
- **Sorun**: Hangi domain'ler commit edildi, hangileri edilmedi bilinmiyor
- **Etki**: Yüksek - Recovery zor
- **Çözüm**: Partial commit log formatı

#### 7. Batch Size Adaptasyonu Yok
- **Sorun**: Sabit batch size (yok, her domain için ayrı)
- **Etki**: Orta - Rate limit'e göre optimize edilebilir
- **Çözüm**: Rate-limit aware batch size calculation

---

## 📊 Batch Size Hesaplama (Rate-Limit Aware)

### DNS Rate Limit: 10 req/s
- **Batch Size Formülü**: `batch_size = min(100, rate_limit * batch_duration)`
- **Örnek**: 10 req/s × 10 saniye = 100 domain/batch (max)

### WHOIS Rate Limit: 5 req/s
- **Batch Size Formülü**: `batch_size = min(100, rate_limit * batch_duration)`
- **Örnek**: 5 req/s × 10 saniye = 50 domain/batch (max)

### Optimal Batch Size Hesaplama

**Formül:**
```python
def calculate_optimal_batch_size(
    dns_rate_limit: float = 10.0,  # req/s
    whois_rate_limit: float = 5.0,  # req/s
    batch_duration: float = 10.0,  # seconds
    max_batch_size: int = 100
) -> int:
    """
    Calculate optimal batch size based on rate limits.
    
    Args:
        dns_rate_limit: DNS rate limit (req/s)
        whois_rate_limit: WHOIS rate limit (req/s)
        batch_duration: Target batch duration (seconds)
        max_batch_size: Maximum batch size (safety limit)
    
    Returns:
        Optimal batch size
    """
    # Her domain için 1 DNS + 1 WHOIS query
    # DNS bottleneck: 10 req/s → 100 domain/10s
    # WHOIS bottleneck: 5 req/s → 50 domain/10s
    # Optimal: min(DNS capacity, WHOIS capacity, max_batch_size)
    
    dns_capacity = int(dns_rate_limit * batch_duration)
    whois_capacity = int(whois_rate_limit * batch_duration)
    
    optimal_batch_size = min(dns_capacity, whois_capacity, max_batch_size)
    
    return optimal_batch_size

# Örnek: 10 req/s DNS, 5 req/s WHOIS, 10 saniye batch
# DNS: 10 × 10 = 100 domain
# WHOIS: 5 × 10 = 50 domain
# Optimal: min(100, 50, 100) = 50 domain/batch
```

**Rate-Limit Aware Batch Processing:**
```python
def process_batch_with_rate_limiting(domain_list: List[str], db: Session):
    optimal_batch_size = calculate_optimal_batch_size()
    
    for i in range(0, len(domain_list), optimal_batch_size):
        batch = domain_list[i:i+optimal_batch_size]
        
        # Process batch with rate limiting
        for domain in batch:
            wait_for_dns_rate_limit()
            dns_result = analyze_dns(domain)
            
            wait_for_whois_rate_limit()
            whois_result = get_whois_info(domain)
            
            # ... scan logic ...
        
        # Batch commit
        db.commit()
```

---

## 🛡️ Deadlock Prevention Stratejisi

### Transaction Timeout
- **Değer**: 30 saniye (configurable)
- **Amaç**: Deadlock durumunda transaction timeout olsun

**Kod Örneği:**
```python
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    # PostgreSQL için transaction timeout
    dbapi_conn.execute("SET statement_timeout = 30000")  # 30 seconds
```

### Retry Logic
- **Max Retries**: 3
- **Backoff**: Exponential (1s, 2s, 4s)
- **Amaç**: Transient deadlock'ları handle et

**Kod Örneği:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4)
)
def process_batch_with_retry(batch: List[str], db: Session):
    try:
        # Batch processing
        for domain in batch:
            scan_single_domain(domain, db, commit=False)
        db.commit()
    except Exception as e:
        db.rollback()
        if "deadlock" in str(e).lower() or "lock" in str(e).lower():
            raise  # Retry
        else:
            raise  # Don't retry
```

### Batch Isolation
- **Strateji**: Her batch ayrı transaction
- **Amaç**: Bir batch fail olursa diğer batch'ler etkilenmesin

**Kod Örneği:**
```python
def process_bulk_scan_with_isolation(domain_list: List[str], db: Session):
    batch_size = 100
    
    for i in range(0, len(domain_list), batch_size):
        batch = domain_list[i:i+batch_size]
        
        try:
            # Isolated batch transaction
            with db.begin():  # Auto-commit on success, auto-rollback on error
                for domain in batch:
                    scan_single_domain(domain, db, commit=False)
        except Exception as e:
            # Batch failed, log and continue
            logger.error("batch_failed", batch_no=i//batch_size, error=str(e))
            continue
```

---

## 📝 Partial Commit Log Tasarımı

### Log Format

```python
{
    "bulk_id": "job_12345",
    "batch_no": 1,
    "total_batches": 10,
    "committed": [
        {"domain": "example.com", "status": "success", "timestamp": "2025-01-28T10:00:00Z"},
        {"domain": "google.com", "status": "success", "timestamp": "2025-01-28T10:00:01Z"}
    ],
    "failed": [
        {"domain": "invalid.com", "status": "error", "error": "Invalid domain", "timestamp": "2025-01-28T10:00:02Z"}
    ],
    "batch_start_time": "2025-01-28T10:00:00Z",
    "batch_end_time": "2025-01-28T10:00:10Z",
    "batch_duration_seconds": 10.0
}
```

### Recovery Mekanizması

**Kod Örneği:**
```python
def get_partial_commit_log(bulk_id: str) -> Dict:
    """Get partial commit log for a bulk scan job."""
    log_key = f"bulk_log:{bulk_id}"
    log_data = redis_client.get(log_key)
    if log_data:
        return json.loads(log_data)
    return {"committed": [], "failed": []}

def store_partial_commit_log(bulk_id: str, batch_no: int, committed: List, failed: List):
    """Store partial commit log for recovery."""
    log_key = f"bulk_log:{bulk_id}"
    log_data = {
        "bulk_id": bulk_id,
        "batch_no": batch_no,
        "committed": committed,
        "failed": failed,
        "timestamp": datetime.utcnow().isoformat()
    }
    redis_client.setex(log_key, 86400, json.dumps(log_data))  # TTL: 24 hours
```

---

## 🔄 Bulk Log Context

### Log Context Format

```python
{
    "bulk_id": "job_12345",
    "batch_no": 1,
    "total_batches": 10,
    "batch_size": 100,
    "processed": 50,
    "succeeded": 45,
    "failed": 5
}
```

### Structured Logging Integration

**Kod Örneği:**
```python
def process_batch_with_logging(batch: List[str], bulk_id: str, batch_no: int, total_batches: int):
    logger.info(
        "bulk_scan_batch_started",
        bulk_id=bulk_id,
        batch_no=batch_no,
        total_batches=total_batches,
        batch_size=len(batch)
    )
    
    # Process batch
    for domain in batch:
        logger.debug(
            "bulk_scan_domain_processing",
            bulk_id=bulk_id,
            batch_no=batch_no,
            domain=domain
        )
        # ... scan logic ...
    
    logger.info(
        "bulk_scan_batch_completed",
        bulk_id=bulk_id,
        batch_no=batch_no,
        succeeded=succeeded,
        failed=failed
    )
```

---

## ⚠️ Dikkat Edilmesi Gerekenler

### 1. Transaction Timeout
- PostgreSQL `statement_timeout` kullanılmalı
- Deadlock durumunda transaction timeout olsun
- Default: 30 saniye (configurable)

### 2. Batch Size Limit
- Maximum batch size: 100 domain (safety limit)
- Rate-limit aware calculation
- Memory usage kontrolü

### 3. Partial Commit Recovery
- Failed domain'leri retry mekanizması
- Partial commit log Redis'te tutulmalı
- Recovery script'i hazır olmalı

### 4. Deadlock Detection
- PostgreSQL deadlock error'ları handle edilmeli
- Retry logic ile transient deadlock'lar çözülmeli
- Log'da deadlock bilgisi olmalı

### 5. Memory Usage
- Büyük domain listeleri için streaming kullan
- Generator pattern ile memory efficient processing

---

## ✅ Hazırlık Checklist

- [x] Mevcut bulk scan analizi yapıldı (sequential processing, her domain için ayrı transaction)
- [x] Batch size hesaplama formülü hazırlandı (rate-limit aware)
- [x] Deadlock prevention stratejisi dokümante edildi (transaction timeout, retry logic, batch isolation)
- [x] Partial commit log formatı tasarlandı
- [x] Bulk log context formatı hazırlandı
- [x] Recovery mekanizması planlandı

---

## 🚀 Sonraki Adımlar

1. **Batch Insert Optimization**
   - `bulk_insert_mappings()` veya `bulk_save_objects()` kullan
   - Her domain için ayrı transaction yerine batch commit

2. **Transaction Optimization**
   - Batch'ler halinde commit (100 domain/batch)
   - Transaction timeout ekle (30 saniye)

3. **Deadlock Prevention**
   - Retry logic implementasyonu
   - Batch isolation stratejisi

4. **Partial Commit Log**
   - Redis'te partial commit log tutma
   - Recovery mekanizması

5. **Batch Size Adaptasyonu**
   - Rate-limit aware batch size calculation
   - Dynamic batch size adjustment

6. **Memory Optimization**
   - Streaming - generator pattern
   - Büyük listeler için memory efficient processing

---

**Referans**: `docs/active/P1-IMPLEMENTATION-PLAYBOOK.md` - Bulk Operations bölümü

