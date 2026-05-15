# RELEASE_READINESS.md — pl-dashboard-v8.html

**Date:** 2026-05-15  
**App version:** 8.3.0  
**Auditor:** Independent principal engineer / security reviewer

---

## Current Status: NO-GO

---

## Blocking Issues (must fix before any external user)

| # | Issue | Why It Blocks |
|---|---|---|
| 1 | NEW-001: XSS in showUpdateBanner | Remote version.json can inject JS on page load |
| 2 | NEW-002: XSS in openChangelog | Remote version.json can inject JS via modal |
| 3 | NEW-003: XSS in showAuthSuccess | Supabase row data can inject JS on sign-in |
| 4 | NEW-004: XSS in showAccessDenied | OAuth email can inject HTML in error panel |
| 5 | NEW-005: XSS in auth-restore-details | Google Sheets name can inject JS on restore |
| 6 | NEW-006: Monthly table column mismatch | Every user sees wrong numbers in wrong columns |
| 7 | NEW-007: XLSX export formula injection | Exported Excel files can execute macros on open |

---

## Conditions for Safe Limited Use (developer / internal only)

The app is safe for a single developer with no external auth, no Google Sheets sync, and no version-check if:
- Google Auth is disabled or the user is the sole Supabase user
- Version check is disabled
- XLSX export is not used on data containing formula-prefix characters
- Data volume stays under 10,000 rows (snapshot quota risk above that)

---

## Pre-Release Checklist

### Security
- [ ] T1-1: escapeHtml wraps data.latest_version and notes in showUpdateBanner
- [ ] T1-2: All release_notes fields escaped in openChangelog  
- [ ] T1-3: user.name and user.plan escaped in showAuthSuccess
- [ ] T1-4: email variable escaped in showAccessDenied (all 4 occurrences)
- [ ] T1-5: sheetInfo.name and dateStr escaped in auth-restore-details
- [ ] T1-7: csvSanitize applied to Category and Description in exportXLSX
- [ ] T2-1: CATEGORIES escaped in all option-building innerHTML
- [ ] T2-2: name/savedFile escaped in sync-file-label renders
- [ ] T2-3: remoteVerData.latest_version escaped in settings-update-status

### Data Integrity
- [ ] T1-6: Monthly table column count fixed (6 headers matched to 6 data columns, OR headers reduced to 5)
- [ ] T4-2: Dead `cogs` variable either used or removed

### Accessibility
- [ ] T4-1: role="dialog" aria-modal aria-labelledby added to confirm-modal, changelog-modal, mapping-modal

### Config
- [ ] T4-3: service-worker.js CACHE_VERSION updated to match APP_VERSION (8.3.0)

---

## Post-Fix Verification Checklist

### Security smoke test
- [ ] Import CSV with `<script>alert(1)</script>` as description, category, date — verify no alert fires
- [ ] Create category named `"><img src=x onerror=alert(1)>` — verify it displays escaped
- [ ] Open changelog modal — verify release notes display as text, not executable HTML
- [ ] Trigger version update banner — verify version string displays escaped
- [ ] Sign in with Google — verify name/plan display as text

### Data integrity smoke test
- [ ] Open Monthly P&L — verify 6 data columns align with 6 header columns
- [ ] Export XLSX with a transaction whose description starts with `=` — open in Excel, verify no formula executes

### Accessibility smoke test
- [ ] Open confirm modal, check DevTools: role=dialog present?
- [ ] Trigger a toast, check aria-live announces it in VoiceOver/NVDA

### Performance smoke test
- [ ] Import 1,000 rows via CSV, navigate to Revenue tab — time the render
- [ ] Import 10,000 rows, navigate to Revenue tab — time the render (should stay < 2s)

---

## Estimated Time to GO

With all quick wins applied (Tier 1 + T2-2 + T2-3): **~80 minutes of engineering + 30 minutes testing = same-day fix possible.**

The remaining Medium/Low items can be tracked as follow-up work post-release.
