# 🔥 Cursor ROAST Prompt — Hunter/D365 Edition (v1.0)

**Purpose:** Aggressive, expert-level codebase audit to identify flaws, hidden complexity, architectural debt, and refactor needs before D365 integration.

**Usage:** Copy-paste this entire prompt into Cursor for a comprehensive code roast.

---

## 🔥 "Hunter Codebase Roast & Hidden-Debt Audit"

**Mode:** aggressive, blunt, expert-level

**Goal:** identify flaws, hidden complexity, architectural debt, refactor needs

**Context:** Hunter v1.0 core, Partner Center integration, Dynamics 365 adapter %94 completed

**Scope:** `app/`, `integrations/`, `tasks/`, `api/`, `core/`, migrations, tests

### 💣 Deliver these 6 outputs:

1. **Brutal Roast (no sugar-coating):**
   - Dirty abstractions
   - Over-engineered parts
   - Under-engineered fragile spots
   - Anti-patterns
   - Things that will explode in production

2. **Hidden Complexity Scan:**
   - Implicit coupling
   - Secret state dependencies
   - Migration drift risks
   - Celery + DB interactions
   - API boundary leaks

3. **Adapter Layer Audit:**
   - Is D365 adapter isolated enough?
   - Mapping layer long-term risk
   - Client retry/backoff correctness
   - Feature flag safety
   - Where will it break under load?

4. **Partner Center Critique:**
   - Referral ingestion logic
   - Domain merge
   - Sync consistency
   - Error handling
   - DB schema correctness

5. **UI/Frontend Roast:**
   - Latent UX issues
   - Mini UI technical debt
   - Refactor priorities
   - "Things you will regret in 3 months"

6. **Actionable Fix List (top 10):**
   - Sorted by severity
   - With rationale
   - Short-term vs long-term split

### 🔧 Rules:

- No generic advice
- No "best practices" fluff
- No compliments
- Direct, harsh, specific
- Cite exact files + functions
- Expose weak points
- Suggest only *surgical* improvements

### 🧠 Tone:

Giga-chad senior engineer + production SRE + sarcastic code reviewer.

---

## 📝 Notes

- **Created:** 2025-01-30
- **Version:** 1.0
- **Status:** Active
- **Next:** Consider v1.1 PRO for deeper analysis (Celery reliability, rate-limit behavior, DB transaction isolation, mapping future-proofing, D365 error taxonomy, test suite brittleness)

