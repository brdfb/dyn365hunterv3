fix: DNS resolver and lead endpoint improvements

## Bug Fixes and Improvements

### Fixed
- **DNS Resolver**: Added public DNS servers (8.8.8.8, 8.8.4.4, 1.1.1.1, 1.0.0.1) for reliable DNS resolution in containers
  - Fixes MX record lookup failures in Docker containers
  - All DNS queries now use public DNS servers for consistent resolution
  
- **Lead Endpoint**: Fixed `/lead/{domain}` endpoint 404 errors
  - Changed from `leads_ready` VIEW query to direct JOIN query
  - Improved error handling and query reliability
  - Now correctly returns lead details for scanned domains

- **CHANGELOG**: Added missing G3 phase documentation

### Changed
- DNS analyzer: All DNS functions now use `_get_resolver()` helper with public DNS servers
- Lead endpoint: Improved query structure for better reliability

### Removed/Cleaned Up
- Archived temporary test script (`test_google_domain.sh`)
- Archived demo script (`scripts/demo.sh`)
- Archived completed action items (`docs/active/ACTIONS.json`)
- Updated documentation structure

## Files Changed
- `app/core/analyzer_dns.py` - DNS resolver improvements
- `app/api/leads.py` - Lead endpoint fix
- `CHANGELOG.md` - Added G3 and bug fixes
- `docs/README.md` - Updated documentation structure
- `docs/archive/` - Archived temporary files

## Testing
- ✅ Tested with google.com domain
- ✅ DNS analysis working correctly (MX, SPF, DMARC found)
- ✅ Lead endpoint returning correct data
- ✅ All tests passing

## CI/CD
This commit will trigger:
- ✅ CI Pipeline (tests, coverage, Docker build)
- ✅ Code Quality checks (Black, Flake8, MyPy)

