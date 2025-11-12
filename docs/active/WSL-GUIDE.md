# WSL Kullanım Rehberi

## Hızlı Başlangıç

```bash
# WSL'de
cd /mnt/c/CursorPro/DomainHunterv3
bash setup_venv.sh
source .venv/bin/activate
bash setup_dev.sh
```

## Path Mapping

| Windows | WSL |
|---------|-----|
| `C:\CursorPro\DomainHunterv3` | `/mnt/c/CursorPro/DomainHunterv3` |

## Venv Aktivasyonu

```bash
# Kontrol
echo $VIRTUAL_ENV  # Boşsa → aktif değil

# Aktif et
source .venv/bin/activate

# Kontrol et
which python  # .venv/bin/python görünmeli
```

## Sorun Giderme

### python3-venv Eksik

```bash
sudo apt update
sudo apt install python3-venv
bash setup_venv.sh
```

### Windows Venv Hatası

```bash
# Windows venv'i sil
rm -rf .venv

# Linux venv oluştur
bash setup_venv.sh
source .venv/bin/activate
```

### Docker Sorunları

```bash
# Container conflict
docker stop dyn365hunter-postgres dyn365hunter-api
docker rm dyn365hunter-postgres dyn365hunter-api

# Docker servis kontrolü
sudo service docker status
```

## Performans Notları

- ⚠️ Windows file system (`/mnt/c/`) yavaş olabilir
- ✅ Linux file system (`~/projects/`) önerilir

