# RELEASE_READINESS.md — pl-dashboard-v8.html

**Date:** 2026-05-15  
**App version:** 8.3.0  
**Auditor:** Independent principal engineer / security reviewer  
**Prior status (2026-05-13):** NO-GO — 7 Critical XSS

---

## Current Status: NO-GO

**Reason:** 5 new High-severity XSS vectors discovered in code paths added or not covered in the prior audit (version banner, changelog modal, auth UI, cloud restore). The monthly P&L table shows wrong numbers in wrong columns for every user.

---

## Blocking Issues

| # | Issue ID | Description | Why It Blocks |
|---|---|---|---|
| 1 | NEW-001 | XSS in showUpdateBanner (version.json) | Executes on every page load for outdated users |
| 2 | NEW-002 | XSS in openChangelog (version.json) | Executes whenever "What's New" is opened |
| 3 | NEW-003 | XSS in showAuthSuccess (Supabase name/plan) | Executes on every sign-in |
| 4 | NEW-004 | XSS in showAccessDenied (OAuth email) | Executes for every auth failure |
| 5 | NEW-005 | XSS in auth-restore-details (Sheets name) | Executes during cross-device restore flow |
| 6 | NEW-006 | Monthly table: 6 headers / 5 data columns | Every user sees Net Profit under "Gross Profit", Margin% under "Net Profit", "Margin %" always blank |
| 7 | NEW-007 | XLSX export: no formula injection guard | Exported .xlsx opens with executable formulas in Excel |

---

## Progress vs Prior Review

| Metric | 2026-05-13 | 2026-05-15 | Change |
|---|---|---|---|
| Critical / High security issues | 7 | 5 (new) + 2 (carry-over) | Tier shifted |
| Total active issues | 30 | 17 | −13 resolved |
| Overall score | 59/100 | 65/100 | +6 |
| Release status | NO-GO | NO-GO | Unchanged |

---

## Conditions for Safe Personal / Developer Use Only

The app is safe for a single developer with full awareness of the above issues if:
- Google Auth / Supabase auth is disabled or the developer is the only Supabase user
- The version check URL is the developer's own controlled endpoint
- XLSX export is avoided for data containing formula-prefix characters (`=`, `+`, `-`, `@`)
- Data stays under 10,000 rows (snapshot quota risk above that)
- Monthly P&L figures are not relied on for actual business decisions until NEW-006 is fixed

---

## Pre-Release Checklist

### Security — Tier 1 blockers (all must be ✅ before release)
- [ ] T1-1: `escapeHtml` wraps `data.latest_version` and `notes` in `showUpdateBanner` (line 4843)
- [ ] T1-2: All 6 release-notes fields escaped in `openChangelog` (line 4880)
- [ ] T1-3: `user.name` and `user.plan` escaped in `showAuthSuccess` (line 5207)
- [ ] T1-4: `email` variable escaped in `showAccessDenied` — all 4 occurrences (lines 5190–5201)
- [ ] T1-5: `sheetInfo.name` and `dateStr` escaped in `auth-restore-details` (line 5360)
- [ ] T1-7: `csvSanitize` applied to Category and Description in `exportXLSX` (line 4720)

### Data integrity — Tier 1 blocker
- [ ] T1-6: Monthly table column count fixed (6 headers matched to 6 data cols OR headers reduced to 5)

### Security — Tier 2 (fix before broad distribution)
- [ ] T2-1: `CATEGORIES` escaped in all `<option>` innerHTML (lines 6040, 6049)
- [ ] T2-2: `name` / `savedFile` escaped in `sync-file-label` renders (lines 4688, 5743)
- [ ] T2-3: `remoteVerData.latest_version` escaped in `settings-update-status` (line 4825)

### Config
- [ ] T4-3: `service-worker.js` `CACHE_VERSION` updated to `pl-dashboard-v8.3.0` (currently `v8.5.0`)

---

## Post-Fix Verification Checklist

### Security smoke tests
- [ ] Import CSV with `<img src=x onerror=alert(1)>` as description → no alert fires in any view
- [ ] Create category named `"><img src=x onerror=alert(2)>` → displays escaped in all dropdowns
- [ ] Open changelog modal → all text is plain text, no HTML executes
- [ ] Trigger version-check banner → version string is plain text
- [ ] Sign in successfully → welcome message is plain text
- [ ] Trigger auth failure → error message is plain text
- [ ] Export XLSX with `=HYPERLINK(...)` description → open in Excel, verify no formula executes

### Data integrity smoke tests
- [ ] Navigate to Monthly P&L with data → verify 6 data columns all show correct values under correct headers
- [ ] Verify "Gross Profit" column shows Revenue − COGS (not Net Profit)
- [ ] Verify "Margin %" column is not blank

### Service worker test
- [ ] DevTools → Application → Service Workers → confirm CACHE_VERSION matches APP_VERSION

### Accessibility smoke test
- [ ] Open confirm modal → DevTools verify `role="dialog"` is present
- [ ] Tab from outside the modal → confirm focus is trapped inside
- [ ] Trigger toast → VoiceOver/NVDA announces it

---

## Time-to-GO Estimate

| Path | Time | What's included |
|---|---|---|
| Minimum viable (Tier 1 only) | ~80 min engineering + 30 min testing | 7 blockers fixed |
| Recommended (Tier 1 + Tier 2) | ~2 hours engineering + 1 hour testing | All XSS + data issues |
| Full production-ready | 1–2 days | All tiers including pagination refactor |

The app can reach GO status **same-day** if Tier 1 and Tier 2 quick wins are applied together.
