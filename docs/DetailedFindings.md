> 📁 This file has moved to `docs/DetailedFindings.md`

See [DetailedFindings.md](../docs/DetailedFindings.md) — or you are already in the right place!

# PL Dashboard — Detailed Findings Report

**Review Date:** May 14, 2026  
**Reviewed By:** Independent AI Review (Perplexity / Claude)  
**App URL:** https://apatel85.github.io/pl-dashboard/  
**Version Reviewed:** v8 (pl-dashboard-v8.html, 4,190 lines)  
**Overall Grade:** F (audit baseline) → **B+ (current, 2026-05-19)**
**Overall Health Score:** 59 / 100 → **82 / 100 (current)**

> **Status (2026-05-19):** Every Critical and High finding below has been resolved. See `CHANGELOG.md` and `review/SCORECARD.md` for details. Status markers (✅ / ⚠️) appear next to each finding.

---

## Quick Summary

The PL Dashboard is a well-intentioned, zero-backend Profit & Loss tracker. It works offline, syncs to Google Sheets, and supports CSV/Excel import. However, it has **7 critical security vulnerabilities**, several **usability problems that would confuse non-technical users**, and **performance issues** that cause browser freezes with large data sets. It should NOT be shared with real users until the Critical issues below are fixed.

---

## Score by Category

| Category | Score | What It Means |
|---|---|---|
| Security | 32 / 100 | 6 XSS attack points, no browser safety policy, formula injection in exports |
| Data Integrity | 58 / 100 | Numbers can drift slightly, dates parse incorrectly, backups fail silently |
| Reliability | 72 / 100 | Strong 3-layer backup system; some edge cases not handled |
| Performance | 78 / 100 | Fast for normal use; crashes browser with 100k+ rows |
| Accessibility | 45 / 100 | Screen readers can't read notifications or icon buttons |
| Code Quality | 55 / 100 | Large messy functions, repeated code, developer shortcuts |
| Browser Compatibility | 75 / 100 | Works best in Chrome/Edge; Firefox/Safari have gaps |

---

## Section 1 — Usability Findings

- ✅ **FIND-U1:** No welcome screen or onboarding — *Resolved: landing page + sample-data + industry templates (v8.1.0–v8.3.0).*
- ✅ **FIND-U2:** Confusing URL structure (versioned filenames) — *Resolved: clean `/` URL serves the dashboard directly (v8.0.3).* 
- ✅ **FIND-U3:** "Layer 1/2/3" backup terminology confuses users — *Resolved: relabeled Quick Save / Save to My Computer / Sync to Google Drive (v8.1.0).*
- ✅ **FIND-U4:** No in-app help or tooltips — *Resolved: help drawer with Quick Start + FAQ (v8.1.0).*
- ✅ **FIND-U5:** No visual feedback on failed inline edits — *Resolved (FIX-016).*
- ✅ **FIND-U6:** "Clear All Data" only asks once (should be double-confirm) — *Resolved (FIX-017).*
- ✅ **FIND-U7:** No install prompt inside the app — *Resolved: smart PWA install banner after 3+ transactions (v8.1.0).*

---

## Section 2 — Security Findings (Critical)

> ⚠️ These must be fixed before sharing this app with anyone.

- ✅ **FIND-S1:** XSS in transaction display (renderRecentEntries) — Line ~2834 — *Resolved (FIX-001).*
- ✅ **FIND-S2:** XSS in Revenue Table (renderRevTable) — Line ~2925 — *Resolved (FIX-001).*
- ✅ **FIND-S3:** XSS in Expense Table (renderExpTable) — Line ~2933 — *Resolved (FIX-001).*
- ✅ **FIND-S4:** XSS in CSV Import Preview (openMappingModal) — Lines ~3034-3035 — *Resolved (FIX-002).*
- ✅ **FIND-S5:** XSS in Category Pills (catPillHTML) — Lines ~4039-4047 — *Resolved (FIX-003).*
- ✅ **FIND-S6:** XSS in Notification Toasts (toast function) — Line ~3783 — *Resolved (FIX-012).*
- ✅ **FIND-S7:** No Content Security Policy (CSP) — *Resolved (FIX-004).*
- ✅ **FIND-S8:** CSV Export Formula Injection — *Resolved (FIX-005).*
- ✅ **FIND-S9:** No integrity check on external libraries (CDN) — *Resolved by inlining Chart.js + XLSX.js; no external scripts are loaded.*

---

## Section 3 — Data & Functional Findings

- ✅ **FIND-D1:** Silent backup failure for large datasets — *Resolved (FIX-009).*
- ✅ **FIND-D2:** Accounting number format not supported `(500.00)` — *Resolved (FIX-010).*
- ✅ **FIND-D3:** European number format causes wrong amounts — *Resolved (FIX-010 + v8.1.0 number-format selector).*
- ✅ **FIND-D4:** Date format confusion (DD/MM vs MM/DD) — *Resolved (FIX-011 + v8.1.0 date-format selector).*
- ✅ **FIND-D5:** Monthly table shows inconsistent profit numbers — *Resolved (FIX-015).*
- ✅ **FIND-D6:** Small rounding errors in totals — *Resolved (FIX-013).*
- ✅ **FIND-D7:** CSV quotes not handled correctly (RFC 4180) — *Resolved (FIX-014).*

---

## Section 4 — Performance Findings

- ✅ **FIND-P1:** Revenue and expense tables freeze browser with large data — *Resolved (FIX-007/008 pagination + v8.2.0 Web Worker import).*
- ⚠️ **FIND-P2:** Memory usage too high for large datasets — *Partially resolved. ~62 MB at 100k transactions; acceptable for target scale, revisit if 1M-row use cases emerge.*

---

## Section 5 — Accessibility Findings

- ✅ **FIND-A1:** Notifications not read aloud by screen readers — *Resolved (FIX-019, ARIA live region on toast).*
- ✅ **FIND-A2:** Icon buttons have no labels — *Resolved (FIX-020).*

---

## Section 6 — Comparison to Leading Apps

| Feature | PL Dashboard | Wave | QuickBooks | Zoho Books |
|---|---|---|---|---|
| Onboarding Wizard | ❌ None | ✅ Yes | ✅ Yes | ✅ Yes |
| Offline Support | ✅ Full | ❌ Online only | ❌ Online only | ❌ Online only |
| Data Privacy | ✅ Best-in-class | ❌ Server-stored | ❌ Server-stored | ❌ Server-stored |
| Security (XSS) | ❌ Not applied yet | ✅ Enterprise-grade | ✅ Enterprise-grade | ✅ Enterprise-grade |
| Price | Free | Free | $30–$200/mo | $15–$240/mo |

---

## Issue Count Summary

| Severity | Count |
|---|---|
| 🔴 Critical | 7 |
| 🟠 High | 5 |
| 🟡 Medium | 9 |
| 🔵 Low | 2 |
| ℹ️ Info | 4 |
| **Total** | **27** |

*See `review/ISSUES_LOG.md` for the full technical issue log. See `docs/SuggestedFix.md` for the step-by-step remediation plan.*
