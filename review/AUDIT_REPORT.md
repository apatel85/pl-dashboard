# pl-dashboard-v8 — Full Audit Report

**Audit date:** 2026-05-15  
**Auditor:** Independent principal engineer / security reviewer  
**Method:** Static analysis (grep, manual inspection), Python logic simulation, stress tests  
**File audited:** pl-dashboard-v8.html (6,224 lines, 1.3 MB)  
**App version:** 8.3.0  
**Prior review date:** 2026-05-13 (Claude Opus 4.7 via ISSUES_LOG.md)

---

## Executive Summary

Since the May 13 review, **23 of the original 30 issues have been fully or partially resolved**, including all 7 formerly-Critical XSS vectors in transaction rendering. The app has improved from Grade F to roughly Grade C+.

However, **5 new High-severity XSS vulnerabilities** were discovered in code paths that didn't exist or weren't covered in the prior audit — specifically in the version-check banner, changelog modal, Google Auth response rendering, and cloud-restore UI. These new XSS vectors render external-controlled data (version.json, Google OAuth, Google Sheets) into innerHTML without escaping, and are just as dangerous as the issues that were fixed.

Additionally, the **Monthly P&L table has a column header/data misalignment bug** (6 headers, 5 data columns) that shows Net Profit under the "Gross Profit" header and leaves "Margin %" always blank — a data integrity defect affecting every user.

**Release recommendation: NO-GO.** The new XSS findings require the same remediation as the original Critical issues before any external user exposure.

---

## Comparison to Prior Review (ISSUE-001 through ISSUE-030)

| Issue ID | Title | Prior Severity | Status |
|---|---|---|---|
| ISSUE-001 | XSS: renderRecentEntries | Critical | **RESOLVED** — escapeHtml applied |
| ISSUE-002 | XSS: renderRevTable | Critical | **RESOLVED** — escapeHtml applied |
| ISSUE-003 | XSS: renderExpTable | Critical | **RESOLVED** — escapeHtml applied |
| ISSUE-004 | XSS: openMappingModal headers | Critical | **RESOLVED** — escapeHtml applied |
| ISSUE-005 | XSS: openMappingModal data cells | Critical | **RESOLVED** — escapeHtml applied |
| ISSUE-006 | XSS: catPillHTML name not safe | Critical | **RESOLVED** — uses `safe` variable |
| ISSUE-007 | No Content-Security-Policy | Critical | **RESOLVED** — CSP added at line 8 |
| ISSUE-008 | CSV formula injection on export | High | **PARTIALLY RESOLVED** — exportCSV uses csvSanitize; exportXLSX does NOT |
| ISSUE-009 | No SRI on CDN scripts | High | **RESOLVED** — both libraries inlined |
| ISSUE-010 | renderRevTable no pagination | High | **RESOLVED** — revPage/revPageSize present |
| ISSUE-011 | renderExpTable no pagination | High | **RESOLVED** — expPage/expPageSize present |
| ISSUE-012 | Snapshot localStorage overflow | High | **PARTIALLY RESOLVED** — QuotaExceededError caught; silent on background saves |
| ISSUE-013 | Accounting-negative not parsed | Medium | **RESOLVED** — `(99.00)` handled at line 4612 |
| ISSUE-014 | Ambiguous DD/MM/YYYY date | Medium | **RESOLVED** — date format selector added |
| ISSUE-015 | XSS: toast() innerHTML | High | **RESOLVED** — uses createTextNode |
| ISSUE-016 | Float arithmetic drift | Medium | **CONFIRMED** — 1.43×10⁻¹¹ drift on 10k×$0.01 |
| ISSUE-017 | RFC 4180 quoted CSV | Medium | **RESOLVED** — escaped `""` handled in parseCSV |
| ISSUE-018 | EU number format miscoercion | Medium | **RESOLVED** — EU detection at line 4613 |
| ISSUE-019 | Monthly table col mismatch | Medium | **REJECTED** (prior finding was imprecise) — new finding NEW-006 documents the actual current bug: 6-col header vs 5-col data |
| ISSUE-020 | inlineEdit no user toast | Medium | **RESOLVED** — toast on error at line 4106 |
| ISSUE-021 | Clear All single confirmation | Medium | **RESOLVED** — showDoubleConfirm pattern used |
| ISSUE-022 | IndexedDB DB_VERSION=1, no upgrade | Medium | **CONFIRMED** — still at version 1 with no migration |
| ISSUE-023 | No fallback if IndexedDB unavailable | Medium | **RESOLVED** — friendly error page at line 2908 |
| ISSUE-024 | 100k row memory footprint ~61.7 MB | Medium | **CONFIRMED** — simulation shows 58.8 MB |
| ISSUE-025 | Toast missing role/aria-live | Low | **RESOLVED** — `role="status" aria-live="polite"` at line 2727 |
| ISSUE-026 | Icon-only buttons missing aria-label | Low | **PARTIALLY RESOLVED** — some buttons now have aria-label |
| ISSUE-027 | Supabase anon key hardcoded | Info | **CONFIRMED** — still present at line 2780 |
| ISSUE-028 | Functions >80 LOC | Info | **CONFIRMED** — several 100+ LOC functions remain |
| ISSUE-029 | Magic strings repeated | Info | **CONFIRMED** |
| ISSUE-030 | Duplicate rendering patterns | Info | **PARTIALLY RESOLVED** |

---

## New Findings (Not in Prior Docs)

| ID | Title | Severity | Type |
|---|---|---|---|
| NEW-001 | XSS in showUpdateBanner via remote version.json | High | Security |
| NEW-002 | XSS in openChangelog via remote version.json | High | Security |
| NEW-003 | XSS in showAuthSuccess via Google OAuth/Supabase data | High | Security |
| NEW-004 | XSS in showAccessDenied via Google email | High | Security |
| NEW-005 | XSS in auth-restore-details via Google Sheets API | High | Security |
| NEW-006 | Monthly table: 6 header cols vs 5 data cols — misaligned display | High | Data Integrity |
| NEW-007 | XLSX export: no formula injection protection | Medium | Security |
| NEW-008 | Category `<option>` elements unescaped | Medium | Security |
| NEW-009 | renderRevTable/renderExpTable: full dbGetAll() on every render | Medium | Performance |
| NEW-010 | File name (sync-file-label, savedFile) rendered unescaped in innerHTML | Medium | Security |
| NEW-011 | No role="dialog" on any modal | Low | Accessibility |
| NEW-012 | `cogs` variable computed but never used in monthly table | Low | Code Quality |
| NEW-013 | settings-update-status: version string unescaped in innerHTML | Low | Security |
| NEW-014 | CSP has unsafe-inline for scripts — defeats XSS protection | Info | Security |
| NEW-015 | SW CACHE_VERSION (v8.5.0) mismatches APP_VERSION (8.3.0) | Info | Config |
| NEW-016 | index.html and pl-dashboard-v8.html are byte-for-byte identical | Info | Config |
| NEW-017 | GOOGLE_CLIENT_ID exposed in source | Info | Security |

---

## Incorrect / Overstated Prior Findings

| Issue | Problem with Prior Finding |
|---|---|
| ISSUE-008 | Stated "not sanitized on export" — exportCSV IS sanitized via csvSanitize; only exportXLSX is not |
| ISSUE-013 | Stated "not parsed" — accounting-negative format IS now handled in applyMapping at line 4612 |
| ISSUE-019 | Described "net vs gross mismatch" — actual current bug is column count mismatch (6 headers, 5 data), a different and worse defect |

---

## Category Assessment Table

| Category | Score | Change from Prior | Notes |
|---|---|---|---|
| Security | 55/100 | +23 | Prior XSS fixed; 5 new High XSS in auth/changelog paths |
| Data Integrity | 62/100 | +4 | Monthly table column mismatch is new; float drift remains |
| Reliability | 76/100 | +4 | Quota handled; IndexedDB fallback added |
| Performance | 72/100 | -6 | renderRevTable/Exp still call dbGetAll() on every render |
| Accessibility | 52/100 | +7 | Toast fixed; modals lack role=dialog |
| Code Quality | 58/100 | +3 | Minor improvements; dead code (cogs) |
| Browser Compatibility | 78/100 | +3 | No change; improved error messaging |
| **Weighted Overall** | **65/100** | **+6** | |

---

## Release Recommendation

**NO-GO**

Blocking reasons:
1. Five new High-severity XSS vectors in version-check, changelog, and auth UI
2. Monthly P&L table shows wrong numbers in wrong columns for every user
3. XLSX export is unprotected against formula injection
4. Category dropdown injection possible via crafted localStorage category names

Safe for personal use by the developer only, with no external data sources (no Google Auth, no version check).
