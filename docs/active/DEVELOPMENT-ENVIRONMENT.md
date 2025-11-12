# Development Environment Recommendations

## 🎯 Önerilen Ortam: WSL2 + Docker Desktop

### Neden WSL2?

1. **Docker Compose Performansı**
   - WSL2'de Docker container'ları native Linux performansında çalışır
   - File system mount'ları daha hızlı
   - Volume performansı daha iyi

2. **Production'a Yakınlık**
   - Production ortamı Linux (container'lar)
   - CI/CD pipeline Linux'ta çalışıyor (GitHub Actions: `ubuntu-latest`)
   - Aynı ortamda test etmek = daha az sorun

3. **Python Venv Uyumluluğu**
   - Linux venv standart (`.venv/bin/activate`)
   - Windows venv karmaşası yok
   - Cross-platform uyumluluk sorunları yok

4. **Terminal Deneyimi**
   - Native Linux shell (bash)
   - Git komutları daha hızlı
   - Script'ler daha güvenilir çalışır

## 📋 Kurulum Adımları (WSL2)

### 1. WSL2 Kurulumu
```bash
# Windows PowerShell (Admin)
wsl --install -d Ubuntu-22.04
# veya mevcut WSL'i güncelle
wsl --update
```

### 2. Docker Desktop WSL2 Entegrasyonu
- Docker Desktop → Settings → General → "Use the WSL 2 based engine" ✅
- Docker Desktop → Settings → Resources → WSL Integration → Ubuntu-22.04 ✅

### 3. Proje Kurulumu
```bash
# WSL terminalinde
cd ~/projects  # veya istediğiniz klasör
git clone https://github.com/brdfb/dyn365hunterv3.git
cd dyn365hunterv3

# Venv oluştur (Linux venv)
bash setup_venv.sh
source .venv/bin/activate

# Docker setup
bash setup_dev.sh
```

## 🔄 Alternatif Ortamlar

### Git Bash (Windows) - ⚠️ Önerilmez

**Avantajlar:**
- Hızlı başlangıç (WSL kurulumu gerekmez)
- Windows dosya sistemine direkt erişim

**Dezavantajlar:**
- Windows venv kullanır (`.venv/Scripts/activate`)
- Docker performansı daha düşük
- Production ortamından farklı
- File system mount sorunları olabilir

**Kullanım:**
```bash
# Git Bash'te
bash setup_venv.sh
source .venv/Scripts/activate  # Windows venv
bash setup_dev.sh
```

### Windows Native (PowerShell/CMD) - ❌ Önerilmez

**Sorunlar:**
- Docker Compose performans sorunları
- Path separator farklılıkları (`\` vs `/`)
- Script uyumluluk sorunları
- Production ortamından çok farklı

## 🎯 Önerilen Workflow

### Günlük Geliştirme (WSL2)

```bash
# 1. WSL terminalini aç
wsl

# 2. Proje klasörüne git
cd ~/projects/dyn365hunterv3

# 3. Venv'i aktive et
source .venv/bin/activate

# 4. Docker servisleri çalışıyor mu kontrol et
docker-compose ps

# 5. Kod yaz, test et
pytest tests/ -v
curl http://localhost:8000/healthz

# 6. Değişiklikleri commit et
git add .
git commit -m "feat: new feature"
```

### Test Çalıştırma

```bash
# WSL'de
source .venv/bin/activate
pytest tests/ -v --cov=app
```

### Docker İşlemleri

```bash
# WSL'de
docker-compose up -d        # Servisleri başlat
docker-compose logs -f api  # Logları izle
docker-compose down         # Servisleri durdur
```

## 🚫 Neden Git Bash Önerilmiyor?

1. **Venv Uyumsuzluğu**
   - Windows venv WSL'de çalışmaz
   - Linux venv Windows'ta çalışmaz
   - İki ortam arasında geçiş sorunlu

2. **Docker Performansı**
   - WSL2 backend kullanılsa bile Git Bash'ten erişim daha yavaş
   - File system mount'ları sorunlu olabilir

3. **Path Sorunları**
   - Windows path'leri (`C:\...`) WSL'de farklı (`/mnt/c/...`)
   - Script'lerde path handling karmaşık

## ✅ Sonuç

**En İyi Seçenek:** WSL2 + Docker Desktop + Linux venv

**Kabul Edilebilir:** Git Bash + Docker Desktop + Windows venv (sadece hızlı test için)

**Önerilmez:** Windows Native (PowerShell/CMD)

## 📝 Notlar

- WSL2'de proje klasörünü Linux file system'inde tutun (`~/projects/`)
- Windows file system'inde (`/mnt/c/...`) çalışmak performans sorunlarına yol açabilir
- Docker Desktop WSL2 backend'i kullanmalı
- Venv'i her ortamda ayrı oluşturun (Windows ve WSL farklı venv'ler)

