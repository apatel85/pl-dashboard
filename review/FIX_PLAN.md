# FIX_PLAN.md — pl-dashboard-v8.html

**Date:** 2026-05-15  
**Scope:** All active issues from FINDINGS_LOG.md

---

## Tier 1 — Release Blockers (fix before any external user)

| Fix | Issue | Effort | Risk |
|---|---|---|---|
| T1-1: Escape version.json data in showUpdateBanner | NEW-001 | 5 min | None |
| T1-2: Escape all fields in openChangelog | NEW-002 | 15 min | None |
| T1-3: Escape user.name and user.plan in showAuthSuccess | NEW-003 | 5 min | None |
| T1-4: Escape email in showAccessDenied | NEW-004 | 5 min | None |
| T1-5: Escape sheetInfo.name and dateStr in auth-restore-details | NEW-005 | 5 min | None |
| T1-6: Fix monthly table column mismatch (add Gross Profit column or fix headers) | NEW-006 | 30 min | Low |
| T1-7: Add csvSanitize to exportXLSX | NEW-007 | 5 min | None |

**Tier 1 total: ~70 minutes**

---

## Tier 2 — High Priority

| Fix | Issue | Effort | Risk |
|---|---|---|---|
| T2-1: Escape CATEGORIES in option elements | NEW-008 | 10 min | Low |
| T2-2: Escape name/savedFile in sync-file-label innerHTML | NEW-010 | 5 min | None |
| T2-3: Escape latest_version in settings-update-status | NEW-013 | 5 min | None |
| T2-4: Convert renderRevTable/renderExpTable to use dbQuery (paginated) | NEW-009 | 2–4 hours | Medium |

---

## Tier 3 — Medium Priority (correctness & data accuracy)

| Fix | Issue | Effort | Risk |
|---|---|---|---|
| T3-1: Replace float summation with integer cents accumulation | ISSUE-016 | 2–4 hours | High — touch all amount fields |
| T3-2: Add IndexedDB schema migration handler for future upgrades | ISSUE-022 | 1 hour | Low |
| T3-3: Add Gross Profit data to monthly table using stored cogs variable | NEW-006/012 | 30 min | Low |

---

## Tier 4 — Polish

| Fix | Issue | Effort | Risk |
|---|---|---|---|
| T4-1: Add role="dialog" aria-modal aria-labelledby to all modals | NEW-011 | 20 min | None |
| T4-2: Remove dead `cogs` variable or use it | NEW-012 | 5 min | None |
| T4-3: Align SW CACHE_VERSION with APP_VERSION | NEW-015 | 2 min | None |

---

## Quick Wins (< 15 minutes each)

These are surgical, zero-risk, immediate gains:

1. **T1-1** — Escape showUpdateBanner (2 field wraps, 5 min)
2. **T1-3** — Escape showAuthSuccess (2 field wraps, 5 min)
3. **T1-4** — Escape showAccessDenied (1 variable, 3 places, 5 min)
4. **T1-5** — Escape auth-restore-details (2 fields, 5 min)
5. **T1-7** — Add csvSanitize to exportXLSX (2 fields, 5 min)
6. **T2-2** — Escape file name in sync-file-label (2 lines, 5 min)
7. **T2-3** — Escape latest_version in settings-update-status (1 wrap, 3 min)
8. **T4-2** — Remove dead cogs variable (1 line delete, 2 min)
9. **T4-3** — Fix SW CACHE_VERSION (1 string change, 2 min)

**Combined: ~37 minutes, zero regression risk**

---

## Architectural Fixes Needing Separate Planning

1. **Integer cent arithmetic** (T3-1): All amount storage, aggregation, and display must move from `float` to `integer cents`. Requires a data migration for existing IndexedDB records, changes to CSV import/export parsing, and changes to KPI display formatting. High blast radius — plan as a separate PR.

2. **Paginated Revenue/Expense queries** (T2-4): `renderRevTable` and `renderExpTable` need `dbQuery({type:'revenue', ...})` support. Requires extending the IndexedDB query engine to filter by type natively, then removing the `dbGetAll()` call. Medium effort, medium risk.

3. **Schema migration system** (T3-2): DB_VERSION should be bumped and `onupgradeneeded` should handle the transition from version N to N+1 without data loss. Plan as schema evolution documentation plus tested migration handler.
