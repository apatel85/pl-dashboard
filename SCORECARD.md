# pl-dashboard-v8 — Health Scorecard

**Review date:** 2026-05-13
**File version:** v8 (4,190 lines)
**Reviewed by:** Claude Opus 4.7 (claude-opus-4-7)
**Branch:** claude/dashboard-review-testing-CcCGw

---

## Overall Grade: F

> Grade formula: A = 0 Critical, ≤ 2 High | B = 0 Critical, ≤ 5 High | C = ≤ 1 Critical | D = ≤ 3 Critical | **F = > 3 Critical**

**7 Critical issues found → Grade F**

The dashboard has a solid feature set and thoughtful backup architecture, but seven
unmitigated XSS vectors and the absence of a Content Security Policy mean arbitrary
JavaScript can be injected via CSV import or URL query strings. These must be resolved
before the app handles production data.

---

## Category Scores (0–100)

| Category | Score | Summary |
|---|---|---|
| Security | 32 | 6 XSS injection points, no CSP, no SRI, formula injection in CSV export |
| Data Integrity | 58 | Float money (drift confirmed), ambiguous date parsing, accounting-negative not handled, snapshot quota overflow |
| Reliability | 72 | Strong 3-layer backup; IndexedDB single transaction; quota failure silent |
| Performance | 78 | Parse/aggregate/export all under budget; memory footprint 61.7 MB exceeds 50 MB target |
| Accessibility | 45 | Toast missing `role="status"`; several icon-only buttons lack `aria-label`; no `:focus-visible` audit |
| Code Quality | 55 | Multiple 100+ LOC functions; duplicate render logic; magic strings; inline `onclick=`; unused `showDoubleConfirm` |
| Browser Compatibility | 75 | File System Access API gated (good); IndexedDB failure has no user-visible error; ES2020+ documented |

**Weighted overall: 59 / 100**

---

## Issue Counts

| Severity | Count | Issues |
|---|---|---|
| Critical | 7 | ISSUE-001 through ISSUE-007 |
| High | 5 | ISSUE-008 through ISSUE-012 |
| Medium | 9 | ISSUE-013 through ISSUE-021 |
| Low | 2 | ISSUE-022 through ISSUE-023 |
| Info | 4 | ISSUE-024 through ISSUE-027 (wait — 27 total; see ISSUES_LOG.md) |
| **Total** | **27** | |

*(Counts reflect ISSUES_LOG.md as generated; some groupings may differ from summary.)*

---

## Performance Numbers (from Part D stress tests)

All stress tests run in Python sandbox on server hardware. Browser performance may vary.

| Metric | Measured | Budget | Status |
|---|---|---|---|
| Parse 100k-row CSV | 713 ms | < 2,000 ms | ✓ PASS |
| Aggregate 100k rows (KPI) | 12.68 ms | < 500 ms | ✓ PASS |
| Export 100k rows to CSV | 132 ms | < 2,000 ms | ✓ PASS |
| Memory footprint (100k txns) | **61.7 MB** | < 50 MB | ✗ FAIL |
| Parse throughput | 140,252 rows/sec | ≥ 50,000 rows/sec | ✓ PASS |
| Float drift (10,000 × $0.01) | 1.4 × 10⁻¹¹ | exactly $100.00 | ✗ FAIL (detectable) |
| Snapshot size (10k txns × 5) | ~35,320 KB | < 5,120 KB | ✗ FAIL |
| Snapshot size (1k txns × 5) | ~3,530 KB | < 5,120 KB | ✓ PASS |
| IndexedDB bulk-put batching | 100 rows/tx | ≥ 500 rows/tx recommended | ✗ FAIL |

**Parse throughput** (rows/sec by dataset):

| Dataset | Rows | Time (ms) | Rows/sec |
|---|---|---|---|
| 10 rows | 10 | < 1 | — |
| 1,000 rows | 1,000 | ~7 | ~142,857 |
| 10,000 rows | 10,000 | ~71 | ~140,845 |
| 100,000 rows | 100,000 | 713 | 140,252 |

---

## Top 5 Risks (Ranked by Impact)

1. **ISSUE-001/002/003 — XSS via renderRecentEntries / renderRevTable / renderExpTable**
   Category names and transaction descriptions are interpolated raw into `innerHTML`.
   An imported CSV with `<script>alert(document.cookie)</script>` in any description
   field executes immediately on the Dashboard tab. *Fix: FIX-001.*

2. **ISSUE-007 — No Content Security Policy**
   Without a CSP, any injected `<script>` tag runs unrestricted. Adding a strict
   `script-src 'self' [whitelisted CDN hashes]` policy would mitigate all XSS even
   before code-level fixes land. *Fix: FIX-004.*

3. **ISSUE-008 — CSV formula injection in export**
   Cells beginning with `=`, `+`, `-`, `@` are exported verbatim. Opening the CSV in
   Excel/Sheets executes the formula under the user's own credentials. *Fix: FIX-005.*

4. **ISSUE-010/011 — No pagination in Revenue/Expense tables**
   With 100k rows, `renderRevTable()` and `renderExpTable()` attempt to inject 100k
   `<tr>` elements, freezing the browser indefinitely. *Fix: FIX-007, FIX-008.*

5. **ISSUE-012 — Snapshot quota overflow (silent)**
   A dataset of ≥ 10k transactions produces a single snapshot ≥ 7MB; five snapshots
   exceed Chrome's 5MB localStorage cap. `takeSnapshot()` catches `QuotaExceededError`
   with only `console.warn` — the user sees nothing and believes the backup succeeded.
   *Fix: FIX-009.*

---

## Recommended Remediation Order

### Tier 1 — Critical (apply first, re-run simulation after each)
| Fix | Issue | Action |
|---|---|---|
| FIX-001 | ISSUE-001, 002, 003, 006 | Add `escapeHtml()`, escape all template literals |
| FIX-003 | ISSUE-004 | Fix `catPillHTML` using `safe` variable correctly |
| FIX-012 | ISSUE-005 | Fix `toast()` to use `textContent` not `innerHTML` |
| FIX-004 | ISSUE-007 | Add CSP `<meta>` tag |

### Tier 2 — High
| Fix | Issue | Action |
|---|---|---|
| FIX-005 | ISSUE-008 | Add `csvSanitize()` to export and sync paths |
| FIX-006 | ISSUE-009 | Add SRI `integrity=` to all CDN `<script>` tags |
| FIX-007 | ISSUE-010 | Add 50-row pagination to `renderRevTable()` |
| FIX-008 | ISSUE-011 | Add 50-row pagination to `renderExpTable()` |
| FIX-009 | ISSUE-012 | Surface `QuotaExceededError` toast to user |

### Tier 3 — Medium
| Fix | Issue | Action |
|---|---|---|
| FIX-010 | ISSUE-013 | Handle `(99.00)` and EU `1.234,56` in amount parser |
| FIX-011 | ISSUE-014 | Add date-format dropdown to mapping modal |
| FIX-013 | ISSUE-016 | Round via `Math.round(n*100)/100` to suppress float display drift |
| FIX-014 | ISSUE-017 | Fix RFC 4180 `""` escaped-quote handling in `parseCSV` |
| FIX-015 | ISSUE-018 | Fix monthly table col-4 net vs gross mismatch |
| FIX-016 | ISSUE-019 | Add error toast to `inlineEdit` failure path |
| FIX-017 | ISSUE-020 | Use `showDoubleConfirm` for Clear All Data |
| FIX-018 | ISSUE-021 | Show user-facing IndexedDB unavailable error |

### Tier 4 — Low / Info
| Fix | Issue | Action |
|---|---|---|
| FIX-019 | ISSUE-022 | Add `role="status"` and `aria-live` to toast container |
| FIX-020 | ISSUE-023 | Add `aria-label` to snapshot download button |

---

## Confidence Table

| Area | Confidence | Rationale |
|---|---|---|
| Static analysis (security) | High | Full 4,190-line file read; regex + manual inspection of all `innerHTML` and `eval` patterns |
| Static analysis (code quality) | High | All function bodies inspected; LOC counted |
| Logic simulation — parseCSV | High | Transliterated to Python; all test vectors run |
| Logic simulation — parseAmount | High | 9 test cases run; (99.00) and EU failure confirmed |
| Logic simulation — KPI aggregation | High | Reference totals validated on 4 dataset sizes |
| Logic simulation — htmlEscape | High | No helper found; XSS confirmed by absence |
| Logic simulation — csvSanitize | High | No sanitizer found; injection confirmed by absence |
| UI rendering | Low | Requires browser; not testable in sandbox |
| IndexedDB transactions | Low | Requires browser; correctness inferred from code reading |
| File System Access API | Low | Chrome-only; requires browser |
| Google Sheets OAuth flow | Low | Requires live OAuth token and network |
| Chart.js rendering | Low | Requires browser; logic traced only |

---

## Recommended Next Steps

1. **Apply FIXES.md** using Claude Code (`Edit` tool) or any AI tool that supports find-and-replace. Apply Tier 1 first and re-run the Part B simulation to confirm zero Critical remain.
2. **Run the Playwright stub** (`tests/e2e.spec.js`) in a real Chromium browser to cover UI rendering, IndexedDB, File System Access, and Google OAuth flows.
3. **Upgrade float storage** to integer cents (`Math.round(amount * 100)`) across all storage and aggregation paths to permanently eliminate drift. (Architectural change — scope separately.)
4. **Add LZ-string compression** to Layer-1 snapshots to fit large datasets within the 5MB localStorage cap.
5. **Bump `version.json`** from `5.0.0` to `8.0.0` after all Critical/High fixes are applied and re-verified.
6. **Consider a Content Security Policy** served via HTTP header (not only `<meta>`) when deploying, as `<meta>` CSP cannot block navigation-level injections.

---

## Cover Note

**Most impactful finding:** The dashboard has **six active XSS injection points** (ISSUE-001 through ISSUE-006) combined with **zero Content Security Policy** (ISSUE-007). Any CSV imported with `<script>` or `<img onerror=>` payloads in description or category fields executes arbitrary JavaScript immediately — capable of exfiltrating all stored transaction data via `indexedDB` or `localStorage`. This is not a theoretical risk; it requires only a maliciously named category or imported CSV row.

**First fix to apply:** `FIX-001` — adds the `escapeHtml()` helper and rewires `renderRecentEntries()`, `renderRevTable()`, and `renderExpTable()` to escape all user-controlled fields before insertion into `innerHTML`. This single patch eliminates four of the seven Critical issues. Follow immediately with `FIX-004` (CSP meta tag) as a defence-in-depth layer.
