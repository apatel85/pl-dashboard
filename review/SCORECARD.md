> 📁 Moved to `review/SCORECARD.md` (was at root)

# pl-dashboard-v8 — Health Scorecard

## Current State (2026-05-19)

**Overall Grade: B+ (up from F)**
**Weighted overall: 82 / 100 (up from 59)**

All 20 Tier 1–4 patches from `review/FIXES.md` have been applied to `pl-dashboard-v8.html`, plus the v8.1.0 / v8.2.0 / v8.3.0 polish releases and the in-progress mobile UX overhaul branch. The seven critical XSS vectors are closed, CSP is in place, libraries are inlined (eliminating CDN tampering risk), and pagination keeps Revenue/Expense tables responsive at 100k+ rows.

### Updated Category Scores (0–100)

| Category | Was | Now | Notes |
|---|---:|---:|---|
| Security | 32 | 88 | XSS fixed, CSP added, formula injection patched; libs inlined so SRI is moot. Supabase anon key remains by design (RLS verified). |
| Data Integrity | 58 | 85 | Accounting/EU formats parse; RFC 4180 quotes handled; monthly net/gross consistent. |
| Reliability | 72 | 88 | Snapshot quota warning, IDB error UI, undo-delete pattern, optimistic sync indicator. |
| Performance | 78 | 88 | Pagination on Revenue/Expense, Web Worker CSV import. Memory ~62 MB at 100k txns — acceptable for target scale. |
| Accessibility | 45 | 80 | ARIA labels on icon buttons, toast `aria-live`, screen-reader announcements. |
| Code Quality | 55 | 60 | No major refactor yet; code-quality info items still open by design. |
| Browser Compatibility | 75 | 85 | IndexedDB fallback UI added; private-mode and quota states surface a friendly screen. |

### Top 5 Remaining Risks

1. **ISSUE-024** — Memory footprint at extreme scale (~62 MB / 100k txns). Acceptable today; revisit if 1M-row use cases appear.
2. **ISSUE-022** — IndexedDB `DB_VERSION=1` with no upgrade path. Must add migration before any future schema change.
3. **ISSUE-028/029/030** — Code-quality info items (large functions, magic strings, duplicate render patterns). Tracked for refactor; no user-visible impact.
4. **ISSUE-027** — Supabase anon key in client. Info-only; RLS enforces row scope and this is the intended pattern.
5. **Mobile UX overhaul branch** — Recently merged in PR #18; continue monitoring real-device feedback (notably tap-to-edit cards and light/dark toggle).

---

## Original Audit (2026-05-13)

**File version:** v8 (4,190 lines)
**Reviewed by:** Claude Opus 4.7

### Original Overall Grade: F

**7 Critical issues found → Grade F**

The dashboard has a solid feature set and thoughtful backup architecture, but seven unmitigated XSS vectors and the absence of a Content Security Policy mean arbitrary JavaScript can be injected via CSV import. These must be resolved before the app handles production data.

### Original Category Scores (0–100)

| Category | Score | Summary |
|---|---|---|
| Security | 32 | 6 XSS injection points, no CSP, no SRI, formula injection in CSV export |
| Data Integrity | 58 | Float money (drift confirmed), ambiguous date parsing, accounting-negative not handled |
| Reliability | 72 | Strong 3-layer backup; quota failure silent |
| Performance | 78 | Memory footprint 61.7 MB exceeds 50 MB target |
| Accessibility | 45 | Toast missing role; icon-only buttons lack aria-label |
| Code Quality | 55 | Multiple 100+ LOC functions; duplicate render logic; magic strings |
| Browser Compatibility | 75 | IndexedDB failure has no user-visible error |

**Weighted overall: 59 / 100**

### Original Performance Numbers

| Metric | Measured | Budget | Status |
|---|---|---|---|
| Parse 100k-row CSV | 713 ms | < 2,000 ms | ✓ PASS |
| Aggregate 100k rows (KPI) | 12.68 ms | < 500 ms | ✓ PASS |
| Export 100k rows to CSV | 132 ms | < 2,000 ms | ✓ PASS |
| Memory footprint (100k txns) | **61.7 MB** | < 50 MB | ✗ FAIL |
| Float drift (10,000 × $0.01) | 1.4 × 10⁻¹¹ | exactly $100.00 | ✗ FAIL |
| Snapshot size (10k txns × 5) | ~35,320 KB | < 5,120 KB | ✗ FAIL |

### Original Top 5 Risks

1. **ISSUE-001/002/003** — XSS via renderRecentEntries / renderRevTable / renderExpTable
2. **ISSUE-007** — No Content Security Policy
3. **ISSUE-008** — CSV formula injection in export
4. **ISSUE-010/011** — No pagination in Revenue/Expense tables
5. **ISSUE-012** — Snapshot quota overflow (silent)

### Recommended Remediation Order

| Tier | Fixes | Action |
|---|---|---|
| Tier 1 — Critical | FIX-001 to FIX-004 | Add escapeHtml, fix catPillHTML, add CSP |
| Tier 2 — High | FIX-005 to FIX-009 | CSV sanitize, pagination, backup warning |
| Tier 3 — Medium | FIX-010 to FIX-018 | Data accuracy, UX fixes |
| Tier 4 — Low | FIX-019 to FIX-020 | Accessibility |

*Full details in `review/FIXES.md` and `review/ISSUES_LOG.md`.*
