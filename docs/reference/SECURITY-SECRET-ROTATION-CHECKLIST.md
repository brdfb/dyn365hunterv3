# Security: Secret Rotation Checklist

**Date**: 2025-01-30  
**Status**: ⚠️ **ACTION REQUIRED**  
**Priority**: **P0 - CRITICAL**

---

## 🚨 Context

**What happened:**
- Azure AD Application Secret was committed to `docs/reference/PARTNER-CENTER-TEST-GUIDE.md`
- GitHub push protection detected the secret
- Secret removed from file and replaced with placeholder `YOUR_CLIENT_SECRET_HERE`
- Git history rewritten using `git filter-branch` to remove secret from all commits
- File re-added without secret, push successful

**Why rotation is required:**
> **If a secret was ever committed, it's theoretically compromised.**
> 
> Even though history was rewritten:
> - May have been pushed to remote before detection
> - May have been cloned by someone
> - May have appeared in CI logs
> 
> **Best practice**: Rotate the secret to close the security gap completely.

---

## ✅ Secret Rotation Checklist

### 1. Azure AD App Registration

- [ ] Go to **Entra ID → App registrations → [Partner Center App]**
- [ ] Create **new client secret**
  - [ ] Copy new secret value (shown only once!)
  - [ ] Set expiration date (recommended: 12-24 months)
- [ ] **Delete or expire old secret** (the one that was committed)
  - [ ] Mark old secret as expired
  - [ ] Or delete it completely

### 2. Update Configuration Files

- [ ] **`.env`** (local development)
  - [ ] Update `HUNTER_PARTNER_CENTER_CLIENT_SECRET` with new value
- [ ] **KeyVault** (if used)
  - [ ] Update secret in Azure Key Vault
- [ ] **Docker/Environment Variables** (production/staging)
  - [ ] Update `HUNTER_PARTNER_CENTER_CLIENT_SECRET` in:
    - [ ] `docker-compose.yml` (if secrets are in env vars)
    - [ ] Production environment variables
    - [ ] Staging environment variables
- [ ] **CI/CD Secrets** (if used)
  - [ ] Update secret in GitHub Actions secrets
  - [ ] Update secret in any CI/CD pipeline configs

### 3. Verify & Test

- [ ] **Restart services** to load new secret
  - [ ] `docker-compose restart api worker` (if using Docker)
  - [ ] Restart production services
- [ ] **Test Partner Center integration**
  - [ ] Verify authentication works with new secret
  - [ ] Test referral sync endpoint: `POST /api/referrals/sync`
  - [ ] Check logs for authentication success
- [ ] **Verify old secret is invalid**
  - [ ] Confirm old secret no longer works (optional verification)

### 4. Documentation

- [ ] **Update this checklist** - Mark as completed
- [ ] **Archive this file** - Move to `docs/archive/` after completion
- [ ] **Note in CHANGELOG** - Add entry about secret rotation (optional)

---

## ⚠️ Git History Rewrite Side Effects

**What was done:**
- `git filter-branch` was used to remove secret from all commits
- This rewrote commit history (commit hashes changed)

**Impact:**
- If others have cloned this branch, their `git pull` will fail
- They need to: `git fetch --all` + `git reset --hard origin/feature/partner-center-phase1`
- Or: Fresh clone of the branch

**Action required (if multi-dev environment):**
- [ ] Notify team about history rewrite
- [ ] Share instructions: "Branch history rewritten, please hard reset or fresh clone"

---

## 📋 Execution Window

- **Secret Rotation**: **S (15-20 minutes)**
- **Team Notification**: **XS (1-2 messages)**

---

## 🎯 Status

- [x] Secret removed from file
- [x] Git history cleaned
- [x] Push successful
- [ ] **Secret rotation** ← **ACTION REQUIRED**
- [ ] Team notification (if multi-dev)

---

**Last Updated**: 2025-01-30  
**Next Review**: After secret rotation completion

