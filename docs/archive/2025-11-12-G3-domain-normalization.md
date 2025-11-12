# TODO: G3 - Domain Normalization & Data Files

**Date Created**: 2025-11-12
**Date Completed**: 2025-11-12
**Status**: Completed
**Phase**: G3

## Tasks

- [x] Create `app/core/__init__.py`
- [x] Create `app/core/normalizer.py` (`normalize_domain()`, `extract_domain_from_email()`, `extract_domain_from_website()`)
- [x] Create `app/data/providers.json` (10+ provider: M365, Google, Yandex, Hosting, Local, Unknown + örnek MX roots)
- [x] Create `app/data/rules.json` (base_score, provider_points, signal_points, segment_rules)
- [x] Create `app/core/provider_map.py` (`load_providers()`, `classify_provider()`)
- [x] Create `app/core/scorer.py` (`load_rules()`, `calculate_score()`, `determine_segment()`, `score_domain()`)

## Test/Acceptance

- [x] `normalize_domain("WWW.EXAMPLE.COM")` → `"example.com"` ✅
- [x] `normalize_domain("xn--example.com")` → punycode decode ✅
- [x] `extract_domain_from_email("user@example.com")` → `"example.com"` ✅
- [x] `classify_provider("outlook-com.olc.protection.outlook.com")` → `"M365"` ✅
- [x] `classify_provider("mail.example.com")` → `"Local"` ✅
- [x] `load_providers()` → 10+ provider yükleniyor ✅ (10 providers)
- [x] `load_rules()` → rules yükleniyor ✅

## Notes

- ✅ Tüm kabul kriterleri test edildi ve geçti
- ✅ WSL path mapping sorunu çözüldü (Windows'tan WSL'e core ve data dizinleri kopyalandı)
- ✅ Container'da volume mount çalışıyor
- ✅ Python path sorunu çözüldü (PYTHONPATH=/app kullanılıyor)

## Next Phase

G4: Ingest Endpoints (CSV + Domain)

