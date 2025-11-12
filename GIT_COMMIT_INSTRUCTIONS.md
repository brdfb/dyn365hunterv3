# Git Commit Instructions

## Problem
WSL'de "Unable to read current working directory" hatası alınıyor.

## Çözüm 1: Dizini Yeniden Belirle

```bash
# WSL'de dizini bul
cd /mnt/c/CursorPro/DomainHunterv3

# Eğer dizin yoksa, Windows path'ini kontrol et
cd /mnt/c
ls -la CursorPro/

# Git durumunu kontrol et
git status
```

## Çözüm 2: Windows'tan Commit Yap

Windows PowerShell veya CMD'de:

```powershell
cd C:\CursorPro\DomainHunterv3
git status
git add .
git commit -F commit_msg.txt
git push origin main
```

## Çözüm 3: Git Repo'yu Yeniden Başlat (Son Çare)

Eğer git repo bozulmuşsa:

```bash
# Git durumunu kontrol et
cd /mnt/c/CursorPro/DomainHunterv3
git status

# Eğer hala çalışmıyorsa, git config'i kontrol et
git config --list

# Veya Windows'tan yap
cd C:\CursorPro\DomainHunterv3
git status
```

## Hazır Commit Mesajı

`commit_msg.txt` dosyası hazır. İçeriği:

```
fix: DNS resolver and lead endpoint improvements

- Fix DNS resolver: Add public DNS servers for reliable resolution in containers
- Fix lead endpoint: Change from VIEW to direct JOIN query for better reliability
- Fix CHANGELOG: Add missing G3 phase documentation
- Clean up: Archive temporary test scripts and completed action items

Fixes:
- DNS MX record lookup failures in Docker containers
- Lead endpoint 404 errors for scanned domains

Tested with google.com domain - all working correctly.
```

## Commit Komutları

```bash
git add .
git commit -F commit_msg.txt
git push origin main
```

## CI/CD

Commit ve push sonrası otomatik olarak:
- ✅ CI Pipeline çalışacak (tests, coverage, Docker build)
- ✅ Code Quality checks çalışacak (Black, Flake8, MyPy)

