# Gereksiz Dosyalar Listesi

## ✅ Temizlendi (Silindi)

Aşağıdaki dosyalar silindi:

### 1. Tekrar Eden Commit Mesaj Dosyaları
- ❌ `COMMIT_MESSAGE.md` - Eski commit mesajı (COMMIT_CHECKLIST.md ile değiştirildi)
- ❌ `commit_msg.txt` - Eski commit mesajı (COMMIT_CHECKLIST.md ile değiştirildi)
- ❌ `GIT_COMMIT_INSTRUCTIONS.md` - Eski talimatlar (artık gereksiz)

**Tutulacak:** `COMMIT_CHECKLIST.md` (güncel ve kullanışlı)

### 2. Gereksiz Script'ler (Tekrar Eden İşlevler)
- ❌ `scripts/fix-containers.sh` - `cleanup-docker.sh` ile aynı işi yapıyor
- ❌ `scripts/fix-docker-deps.sh` - `rebuild-docker.sh` ile aynı işi yapıyor
- ❌ `scripts/auto-doc-manager.sh` - `manage_docs.sh` ile aynı işi yapıyor
- ❌ `scripts/auto-update-docs.sh` - Otomatik güncelleme, gereksiz karmaşıklık

**Tutulacak Script'ler:**
- ✅ `scripts/cleanup-docker.sh` - Container temizleme
- ✅ `scripts/rebuild-docker.sh` - Container rebuild
- ✅ `scripts/run-tests-docker.sh` - Test çalıştırma
- ✅ `scripts/manage_docs.sh` - Dokümantasyon yönetimi
- ✅ `scripts/sales-demo.sh` - Demo script

### 3. Boş/Geçici Klasörler
- ❌ `htmlcov/` - Coverage raporları (boş, .gitignore'da olmalı)

## ✅ Silinen Dosyalar

1. ✅ `COMMIT_MESSAGE.md` - Silindi
2. ✅ `commit_msg.txt` - Silindi
3. ✅ `GIT_COMMIT_INSTRUCTIONS.md` - Silindi
4. ✅ `scripts/fix-containers.sh` - Silindi
5. ✅ `scripts/fix-docker-deps.sh` - Silindi
6. ✅ `scripts/auto-doc-manager.sh` - Silindi
7. ✅ `scripts/auto-update-docs.sh` - Silindi
8. ✅ `htmlcov/` - Klasör kontrol edildi (zaten ignore ediliyor)

## ✅ Tutulacak Dosyalar

- ✅ `COMMIT_CHECKLIST.md` - Güncel commit checklist
- ✅ `CHANGELOG.md` - Versiyon geçmişi
- ✅ `README.md` - Ana dokümantasyon
- ✅ Tüm aktif script'ler (cleanup, rebuild, run-tests, manage_docs, sales-demo)
- ✅ Tüm dokümantasyon dosyaları

## 📝 Not

Bu dosyalar silindikten sonra `.gitignore` dosyasına şunları eklemek iyi olur:
```
htmlcov/
.coverage
*.pyc
__pycache__/
```

