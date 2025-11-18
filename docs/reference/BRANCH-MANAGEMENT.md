# Branch Management Guide

**Last Updated**: 2025-01-30  
**Purpose**: Branch naming conventions, lifecycle, and deprecated branch tracking

---

## 🎯 Active Branches

### Main Branches
- `main` - Production-ready code (stable releases)
- `feature/*` - Feature development branches

### Current Active Feature Branches
- `feature/partner-center-phase1` - **ACTIVE** - Partner Center Phase 2 integration (opened 2025-01-29)
  - Status: 🅿️ Parked (MVP-safe mode, 50% completed)
  - Progress: Tasks 2.1, 2.2, 2.3 completed
  - Remaining: Tasks 2.4, 2.5, 2.6 (post-MVP)

---

## 📋 Deprecated/Archived Branches

### Partner Center Branches

**⚠️ DEPRECATED**: `feature/partner-center-referrals`
- **Status**: ❌ **DEPRECATED** - Do not use
- **Reason**: Replaced by `feature/partner-center-phase1` (2025-01-29)
- **Action**: Use `feature/partner-center-phase1` instead
- **Note**: Branch kept for historical reference only
- **Last Commit**: Tagged as `v1.0.0` (2025-01-28)

**✅ ACTIVE**: `feature/partner-center-phase1`
- **Status**: ✅ **ACTIVE** - Current development branch
- **Opened**: 2025-01-29
- **Purpose**: Partner Center Phase 2 integration
- **Use this branch** for Partner Center related work

---

## 🔄 Branch Lifecycle

### Creating a New Branch
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/feature-name

# Push and set upstream
git push -u origin feature/feature-name
```

### Deprecating a Branch
1. Create new branch with updated name/approach
2. Update all documentation references
3. Add branch to this document (Deprecated section)
4. Add commit message to old branch: `git commit --allow-empty -m "DEPRECATED: Use feature/new-branch-name instead"`
5. **Do NOT delete** - Keep for historical reference

### Merging a Branch
1. Ensure all tests pass
2. Update documentation
3. Create pull request
4. After merge, mark branch as merged in this document
5. Delete local branch: `git branch -d feature/branch-name`
6. Delete remote branch: `git push origin --delete feature/branch-name`

---

## 📝 Branch Naming Conventions

### Feature Branches
- Format: `feature/feature-name`
- Examples:
  - `feature/partner-center-phase1`
  - `feature/ui-stabilization-v1.1`
  - `feature/dynamics-integration`

### Hotfix Branches
- Format: `hotfix/issue-description`
- Examples:
  - `hotfix/dns-timeout-fix`
  - `hotfix/cache-invalidation`

### Archive Branches (Optional)
- Format: `archive/feature-name` (if needed for long-term reference)
- Use sparingly - prefer documentation over archive branches

---

## ⚠️ Important Notes

1. **Always check this document** before creating a new branch for existing features
2. **Update documentation** when deprecating or creating branches
3. **Do not delete deprecated branches** - Keep for historical reference
4. **Use descriptive names** - Avoid abbreviations unless widely understood
5. **One feature per branch** - Keep branches focused and small

---

## 🔍 Quick Reference

**"Which branch should I use for Partner Center?"**
→ Use `feature/partner-center-phase1` (active branch)

**"Is feature/partner-center-referrals still active?"**
→ No, it's deprecated. Use `feature/partner-center-phase1` instead.

**"How do I know if a branch is deprecated?"**
→ Check this document's "Deprecated/Archived Branches" section.

---

**Last Updated**: 2025-01-30  
**Maintained By**: Documentation Manager Agent

