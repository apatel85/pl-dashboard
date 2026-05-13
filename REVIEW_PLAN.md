# P&L Dashboard v8 — AI-Driven Review, Testing & Auto-Fix Plan (v2)

## Context

`pl-dashboard-v8.html` (4,190 lines) is a single-file, zero-backend P&L tracker built with vanilla JS + Chart.js + XLSX.js + IndexedDB + localStorage + File System Access API + Google Sheets API. Because it stores a user's financial data client-side, defects in any layer (XSS via category names, CSV formula injection, IndexedDB upgrade dropping data, floating-point money drift, Sheets sync overwrites) can silently destroy or leak data.

This revision (v2) shifts the testing model from "human-in-browser" to **AI-driven**: the AI tool (ChatGPT with Code Interpreter, Gemini in AI Studio, or Claude Code) performs **all** review, functional simulation, and stress testing by:
1. Statically analyzing the HTML/JS for defects.
2. Extracting the JavaScript and **simulating** its core logic (parsing, math, formatting, validation) in a sandbox (Python / Node) using AI-generated mock datasets.
3. Generating and replaying stress datasets (100 → 100,000 rows) to measure throughput, memory pressure, and correctness.
4. Producing two machine-readable outputs (`ISSUES_LOG.md` + `FIXES.md`) so a downstream AI can be handed the file + `FIXES.md` and apply patches autonomously.
5. Producing a human-readable **scorecard** summarizing app health.

The plan is AI-agnostic (Claude / ChatGPT / Gemini) and is itself uploaded alongside the dashboard so the AI knows exactly what to do.

---

## Critical Files

| Path | Role |
|---|---|
| `/home/user/pl-dashboard/pl-dashboard-v8.html` | Target of review (4,190 lines, single file) |
| `/home/user/pl-dashboard/version.json` | Version metadata (currently 5.0.0) |
| `/home/user/pl-dashboard/REVIEW_PLAN.md` | This plan (committed to repo) |
| `/home/user/pl-dashboard/AI_REVIEW_PROMPT.md` | Standalone prompt to paste into any AI tool |
| `/home/user/pl-dashboard/ISSUES_LOG.md` | Output: every defect found |
| `/home/user/pl-dashboard/FIXES.md` | Output: fix patches in AI-applyable format |
| `/home/user/pl-dashboard/SCORECARD.md` | Output: overall health + performance summary |
| `/home/user/pl-dashboard/mock-data/` | Output: generated mock datasets used in tests |

---

## Plan Structure

- **Part A** — Static Code Review (no execution)
- **Part B** — Logic Simulation Testing (AI runs JS-equivalent code on mock data)
- **Part C** — Mock Dataset Specifications (with generators)
- **Part D** — Stress & Performance Testing
- **Part E** — Issue Logging Format (`ISSUES_LOG.md`)
- **Part F** — Fix-Ready Output Format (`FIXES.md` — designed for auto-apply)
- **Part G** — Scorecard & Performance Report (`SCORECARD.md`)
- **Part H** — AI-Tool Execution Notes

---

## Part A — Static Code Review

### A1. Inventory
1. Report total lines, locations of `<style>` and `<script>` blocks.
2. Function index: name, line, LOC, purpose. Flag any > 80 LOC.
3. Global state list (`txnSort`, `txnPage`, `parsedCSV`, `autoFileHandle`, `linkedFileHandle`, etc.).
4. Storage key list (`CATEGORIES_KEY`, `GSHEETS_KEY`, `L2_META_KEY`, IndexedDB store names).
5. External dependencies (CDN URLs, versions).

### A2. Security Review
| ID | Check |
|---|---|
| A2.1 | Every `innerHTML =` / template-literal HTML must escape user data (categories, descriptions, filenames). |
| A2.2 | Count inline `onclick=` handlers; flag any built from user data. |
| A2.3 | Zero `eval`, `new Function`, `setTimeout("string")`. |
| A2.4 | Google OAuth `client_id` is public web client; scopes minimal (Sheets only). |
| A2.5 | Tokens in `localStorage` have TTL; no long-lived refresh tokens. |
| A2.6 | CSV export sanitizes cells starting with `=`, `+`, `-`, `@` (formula injection). |
| A2.7 | CSP meta tag present? If missing, flag. |
| A2.8 | External CDN scripts use SRI (`integrity=` attribute)? If missing, flag. |

### A3. Data Integrity
| ID | Check |
|---|---|
| A3.1 | `onupgradeneeded` branches on `oldVersion`; never drops store. |
| A3.2 | `dbBulkPut` wrapped in single transaction with rollback. |
| A3.3 | Numeric parsing strips `$`, `,`, handles `(99.00)` accounting-negative. |
| A3.4 | Date parsing unambiguous (locked to ISO, or user-prompted on import). |
| A3.5 | Amounts as integer cents or float; if float, flag drift risk. |
| A3.6 | Layer 1 snapshot rolling buffer correctly capped at 5. |
| A3.7 | Sheets pull shows destructive-overwrite confirmation. |

### A4. Code Quality
| ID | Check |
|---|---|
| A4.1 | Functions > 80 LOC. |
| A4.2 | Duplicate render logic (dropdowns, tables). |
| A4.3 | Magic strings; should be top-level constants. |
| A4.4 | Every async op has error path → toast. |
| A4.5 | ARIA: icon-only buttons have `aria-label`; toast has `role="status"`; `:focus-visible` ≥ 2px. |
| A4.6 | Tables paginate/virtualize before render. |

### A5. Browser Compatibility
| ID | Check |
|---|---|
| A5.1 | File System Access API feature-detected; graceful fallback on Firefox/Safari. |
| A5.2 | IndexedDB fallback message in private mode. |
| A5.3 | ES2020+ syntax usage documented. |

---

## Part B — Logic Simulation Testing (AI-Executed)

**Goal:** The AI extracts pure-logic JavaScript functions from the file and re-executes them in a sandbox (Python via Code Interpreter, or Node) against generated mock data. This is **not** UI testing — it's **logic correctness testing**. Any function that does not require the DOM, IndexedDB, or network is in scope.

### B1. Function Extraction
1. Identify pure-logic functions (no DOM/IndexedDB/fetch). Candidates:
   - Date parser (`parseDate` / equivalent)
   - Amount parser (handles `$`, `,`, `()`)
   - Currency formatter
   - CSV parser (handles BOM, quoted commas, escapes)
   - CSV escaper / formula-injection sanitizer
   - Mapping auto-detector (heuristics for `date`, `amount`, `type`, `category` headers)
   - Total/KPI calculators (revenue, expenses, net profit, margin %)
   - Monthly summary aggregator
   - Snapshot diff/restore
   - HTML escaper (if present)
2. For each, copy the function body verbatim into a sandbox file (`tests/extracted.js` for Node, or paste into a Python `js2py`/`PyMiniRacer` cell).

### B2. Unit Test Matrix

Generate and run the following test matrix against each extracted function. Record pass/fail in `ISSUES_LOG.md`.

**parseAmount tests:**
| Input | Expected | Notes |
|---|---|---|
| `"1234.56"` | `1234.56` | basic |
| `"$1,234.56"` | `1234.56` | currency + thousands |
| `"(99.00)"` | `-99.00` | accounting negative |
| `"-50"` | `-50` | signed |
| `"1.234,56"` | `1234.56` or error | EU format — flag if silent miscoerce |
| `""` | `null`/error | empty |
| `"abc"` | `NaN`/error | non-numeric |
| `"1e6"` | `1000000` | scientific |
| `"  42  "` | `42` | whitespace |

**parseDate tests:**
| Input | Expected | Notes |
|---|---|---|
| `"2025-05-13"` | `Date(2025,4,13)` | ISO |
| `"05/13/2025"` | ambiguous | MM/DD vs DD/MM |
| `"13/05/2025"` | ambiguous | DD/MM |
| `"May 13, 2025"` | `Date(2025,4,13)` | long |
| `"2025/05/13"` | parse or error | slash ISO |
| `"1899-01-01"` | accepted or warning | range |
| `"2099-12-31"` | accepted or warning | range |
| `""` / `null` | error | empty |

**csvSanitize tests:**
| Input | Expected output |
|---|---|
| `"=SUM(A1:A10)"` | `"'=SUM(A1:A10)"` (prefixed) |
| `"+CMD"` | `"'+CMD"` |
| `"-1234"` | passthrough (negative number, not formula) — confirm app's choice |
| `"@import"` | `"'@import"` |
| `"normal text"` | passthrough |

**KPI calculator tests:**
- Feed 1,000 mock txns (see C2), confirm `totalRevenue`, `totalExpenses`, `netProfit`, `margin%` match Python-computed reference within $0.005.
- Feed 10,000 mock txns of `$0.01` each → revenue should be exactly `$100.00` (flag float drift if not).

**csvParse tests:**
- BOM prefix file → strips BOM
- Quoted field containing `,` → preserved
- Quoted field containing `"` (escaped as `""`) → preserved
- CRLF vs LF line endings → both work
- Empty trailing rows → skipped
- Mapping auto-detector recognizes headers: `Date`, `date`, `Transaction Date`, `txn_date` → all map to date

**htmlEscape tests:**
- `<script>alert(1)</script>` → `&lt;script&gt;alert(1)&lt;/script&gt;`
- `"><img src=x onerror=alert(1)>` → fully escaped
- `O'Brien` → `O&#39;Brien`

### B3. Integration Simulation
1. Build a Python/Node harness that mimics the app's data flow:
   - Generate mock CSV (Part C2) → parse → map → "store" in dict → aggregate KPIs → "export" CSV.
2. Run end-to-end on 100 / 1,000 / 10,000 / 100,000 row datasets.
3. Compare AI-computed totals to a known reference total embedded in each mock dataset's filename. Any deviation → ISSUE.

### B4. Browser-Only Features
For features the AI **cannot** simulate (UI rendering, Chart.js, IndexedDB transactions, File System Access, Google OAuth), the AI must:
1. Read the relevant function code carefully.
2. Trace control flow and log every reachable error path.
3. List what would need a human or headless browser (Playwright/Puppeteer) to test.
4. Generate a Playwright test script stub (`tests/e2e.spec.js`) that the human can run later if desired.

---

## Part C — Mock Dataset Specifications

The AI generates these and writes them to `/home/user/pl-dashboard/mock-data/`. Each file's name encodes the expected total so simulations can self-verify.

### C1. Tiny smoke dataset — `mock-10-rev2500-exp1000.csv`
- 10 rows, mixed types, single month.
- Headers: `date,type,category,description,amount`
- Total revenue: $2,500.00 | Total expenses: $1,000.00 | Net: $1,500.00

### C2. Standard dataset — `mock-1000-rev500000-exp300000.csv`
- 1,000 rows across 12 months, 6 categories.
- Total revenue: $500,000.00 | Total expenses: $300,000.00 | Net: $200,000.00

### C3. Stress datasets
- `mock-10000-rev1000000-exp500000.csv`
- `mock-100000-rev10000000-exp5000000.csv`

### C4. Edge-case dataset — `mock-edge-cases.csv`
20 rows covering:
- Amounts with `$` and thousands separators
- Negative parentheses `(123.45)`
- Empty description
- Description with HTML payload: `<script>alert(1)</script>`
- Description with quoted comma: `"Smith, John LLC"`
- Description with embedded quote: `"He said ""hi"""`
- Date in `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY-MM-DD` formats
- Future date `2099-12-31`
- Past date `1899-01-01`
- Zero amount `$0.00`
- Tiny amount `$0.001`
- Huge amount `$999,999,999.99`
- Unicode category: `Café`, `日本円`
- Formula injection payloads: `=SUM(A1:A10)`, `+cmd|calc`, `@SUM`, `-99 -SUM`
- BOM-prefixed first row

### C5. Floating-point torture — `mock-10000-pennies.csv`
10,000 rows of exactly `$0.01` each. Expected total: **$100.00 exactly**.

### C6. Boundary stress — `mock-100k-mixed.csv`
100,000 rows, 24 months, 20 categories. Tests pagination, table render budget, IndexedDB bulk-put estimated throughput.

### C7. Generator pseudocode (AI implements this in Python)
```python
import csv, random, datetime
def gen(filename, n, target_rev, target_exp, categories, start_date, months):
    rows = []
    rev_pool = [target_rev * w for w in dirichlet(n_rev)]   # split target across rev rows
    exp_pool = [target_exp * w for w in dirichlet(n_exp)]
    for i in range(n):
        d = start_date + timedelta(days=random.randint(0, months*30))
        is_rev = (i < len(rev_pool))
        amt = round(rev_pool[i] if is_rev else exp_pool[i - len(rev_pool)], 2)
        rows.append([d.isoformat(), "revenue" if is_rev else "expense",
                     random.choice(categories), f"txn-{i}", amt])
    # final residual goes to last row to make total exact
    ...
    with open(filename,'w',newline='') as f:
        w = csv.writer(f); w.writerow(["date","type","category","description","amount"])
        w.writerows(rows)
```

---

## Part D — Stress & Performance Testing

### D1. Parse throughput
For each stress dataset (1k, 10k, 100k):
1. Time the extracted CSV parser in the sandbox: `time.perf_counter()` before/after.
2. Record rows/sec.
3. Compare to budget: parser should sustain ≥ 50,000 rows/sec on modern hardware; flag if < 10,000.

### D2. Aggregation throughput
1. Time the KPI calculator on 100k rows.
2. Budget: < 100ms in JS, < 500ms in Python sandbox.

### D3. Memory estimate
1. Compute per-row footprint (Python `sys.getsizeof`) × 100k.
2. Flag if estimated > 50MB (will pressure IndexedDB quota and Chart.js).

### D4. UI render budget (static estimate)
1. Read transaction-table render function.
2. Confirm it paginates (does NOT render all 100k rows at once).
3. If full render is unconditional → CRITICAL performance issue.

### D5. Export throughput
1. Time CSV export of 100k rows.
2. Budget: < 2 seconds. Flag if > 5 seconds (UI will hang).

### D6. IndexedDB bulk-put estimate
1. Inspect `dbBulkPut`. Confirm batching (≥ 500 per transaction).
2. Estimate time for 100k inserts: should be < 10 seconds. Flag missing batching.

### D7. Layer 1 snapshot size
1. Compute size of one snapshot (= full data array stringified).
2. localStorage cap is ~5MB. With 5 snapshots × full data → flag if any single dataset > 1MB stringified.
3. Recommend compression (LZ-string) if oversized.

---

## Part E — Issue Logging Format (`ISSUES_LOG.md`)

Each finding (static, simulated, or stress) is logged in `ISSUES_LOG.md` using this exact format:

```markdown
## ISSUE-<NNN>: <Short title>
- **Section:** A2.1 | B2.parseAmount | D1 | etc.
- **Severity:** Critical | High | Medium | Low | Info
- **Type:** Security | Data-loss | Functional | UX | Performance | Accessibility | Code-quality
- **Location:** pl-dashboard-v8.html:<line-start>-<line-end> (function `<name>`)
- **Discovered by:** static-review | simulation | stress-test
- **Steps to reproduce:** 1) … 2) … 3) …
- **Expected:** …
- **Actual:** …
- **Evidence:**
  ```js
  // ≤ 10 lines of offending code
  ```
- **Linked fix:** FIX-<NNN> (in FIXES.md)
```

Severity guide:
- **Critical** — data loss, XSS, auth leak, app won't load
- **High** — feature broken, silent corruption, no error surfaced
- **Medium** — wrong calc in edge case, missing validation
- **Low** — cosmetic, minor UX
- **Info** — code smell, refactor candidate

Numbering is sequential and stable; never reused.

---

## Part F — Fix-Ready Output Format (`FIXES.md`)

`FIXES.md` is the deliverable that, when uploaded alongside `pl-dashboard-v8.html`, lets a downstream AI apply all fixes autonomously. Format **strictly**:

```markdown
# FIXES.md — Auto-applyable patches for pl-dashboard-v8.html

## Apply Instructions for AI tools

Upload `pl-dashboard-v8.html` and this file. Then prompt:
> "Apply every FIX-NNN block below to pl-dashboard-v8.html in order.
>  Each block specifies a unique OLD_STRING to find and a NEW_STRING to replace it with.
>  If OLD_STRING is not found, skip the fix and report it.
>  After all fixes, output the patched file."

---

## FIX-001: <Short title — mirrors ISSUE-NNN>
**Resolves:** ISSUE-001
**Severity:** Critical
**Type:** Security
**File:** pl-dashboard-v8.html
**Strategy:** find-and-replace (exact string)

### OLD_STRING
```
<exact code block from file, including surrounding context for uniqueness>
```

### NEW_STRING
```
<exact replacement code, preserving indentation>
```

### Rationale
1–3 sentences: why this fix is correct and complete.

### Verification
- Re-run Part B simulation for: <function name>
- Expected: <specific test now passes>

---

## FIX-002: …
(repeat per issue)
```

**Rules for the AI generating `FIXES.md`:**
1. Every `OLD_STRING` must appear **exactly once** in the file (include enough surrounding lines for uniqueness).
2. Indentation, quotes, and whitespace in `OLD_STRING`/`NEW_STRING` must match byte-for-byte.
3. Fixes are ordered so earlier fixes don't invalidate later `OLD_STRING`s (group by file region, top-to-bottom).
4. For new-helper-function fixes (e.g., adding `escapeHtml`), insert immediately after the last top-level `const` declaration; use that declaration line as anchor.
5. No fix may rewrite the entire file or large sections — keep patches surgical (≤ 50 lines each). For large refactors, split into multiple FIX-NNN entries.
6. Every fix links back to its `ISSUE-NNN`.

This format mirrors what Claude Code's `Edit` tool expects (`old_string` / `new_string`), so the same file works with Claude Code directly **and** with any AI tool that supports find-and-replace.

---

## Part G — Scorecard & Performance Report (`SCORECARD.md`)

The AI writes a one-page scorecard. Format:

```markdown
# pl-dashboard-v8 — Health Scorecard

**Review date:** YYYY-MM-DD
**File version:** v8 (commit/hash if known)
**Reviewed by:** ChatGPT 4o | Gemini 2.x | Claude 4.7 (state which)

## Overall Grade: A | B | C | D | F

(Grade formula:
 A = 0 Critical, ≤ 2 High
 B = 0 Critical, ≤ 5 High
 C = ≤ 1 Critical, ≤ 10 High
 D = ≤ 3 Critical
 F = > 3 Critical)

## Category scores (0–100)
| Category | Score | Notes |
|---|---|---|
| Security | 85 | 1 XSS risk, no SRI on CDN |
| Data integrity | 70 | float-based money, ambiguous dates |
| Reliability | 90 | strong backup layers |
| Performance | 75 | 100k import OK; export untested in browser |
| Accessibility | 60 | missing ARIA on icon buttons |
| Code quality | 65 | long functions, inline handlers |
| Browser compat | 80 | FSA gated; Safari fallback unclear |

## Issue counts
| Severity | Count |
|---|---|
| Critical | N |
| High | N |
| Medium | N |
| Low | N |
| Info | N |

## Performance numbers (from Part D)
| Metric | Value | Budget | Pass/Fail |
|---|---|---|---|
| Parse 100k CSV | X ms | < 2000 ms | ✓/✗ |
| Aggregate 100k rows | X ms | < 500 ms | ✓/✗ |
| Export 100k CSV | X ms | < 2000 ms | ✓/✗ |
| Memory footprint 100k | X MB | < 50 MB | ✓/✗ |
| Snapshot size full data | X KB | < 1024 KB | ✓/✗ |
| Float drift (10k × $0.01) | $X | exactly $100.00 | ✓/✗ |

## Top 5 risks (ranked)
1. ISSUE-NNN — short description
2. …

## Recommended remediation order
1. All Critical issues → apply FIX-001..FIX-N first.
2. High-severity data-integrity issues next.
3. Performance + accessibility.
4. Code-quality refactors last.

## Confidence
| Area | Confidence | Why |
|---|---|---|
| Static analysis | High | Full file analyzed |
| Logic simulation | High/Med | Extracted N of M pure functions |
| UI rendering | Low | Not testable without browser |
| IndexedDB transactions | Low | Not testable without browser |
| Google Sheets sync | Low | Not testable without OAuth flow |

## Recommended next steps
- Human runs supplied Playwright test stub (`tests/e2e.spec.js`) for UI-only features.
- Apply FIXES.md via Claude Code or equivalent.
- Re-run Part B simulation; confirm zero Critical/High issues remain.
```

---

## Part H — AI-Tool Execution Notes

### H1. ChatGPT (4o / o1 with Code Interpreter / Advanced Data Analysis)
- Upload `pl-dashboard-v8.html`, `REVIEW_PLAN.md` (this file), and (optionally) `AI_REVIEW_PROMPT.md`.
- Use **Code Interpreter** for: regex searches, mock-data generation (Python `csv`, `random`), function extraction, sandboxed execution of pure-JS via `PyMiniRacer` or by manually transliterating to Python.
- For 100k-row stress tests, generate the file in chunks and run in-memory only.
- Output four artifacts: `ISSUES_LOG.md`, `FIXES.md`, `SCORECARD.md`, plus the `mock-data/` files.

### H2. Gemini (2.x in AI Studio)
- Use AI Studio for full 1M-context single-pass analysis.
- Gemini can output all four artifacts in one response if asked.
- For sandboxed execution, ask for Python code blocks the user can run locally, or use Gemini's built-in code execution if available.

### H3. Claude (claude.ai or Claude Code)
- In Claude Code: file already on disk, use `Read` with offsets, `Bash` for grep, generate mocks via `Bash` (`python3 -c '...'`), and execute simulations via `node` if available, otherwise transliterate to Python.
- `FIXES.md` format is designed to feed Claude Code's `Edit` tool directly (its `old_string`/`new_string` shape matches one-to-one).
- After producing `FIXES.md`, Claude Code can apply every fix automatically without human intervention.

### H4. Common guardrails
- Always generate Layer-1 snapshot guidance in the final report ("Before applying fixes, open the running app and click Snapshot Now").
- Never push, commit, or modify the source without explicit user approval.
- Apply fixes one severity tier at a time (Critical → High → Medium → …), re-running simulations between tiers.
- If a function cannot be extracted cleanly (mixes DOM + logic), report it as an `ISSUE` (Code-quality, Info) recommending refactor for testability.

---

## Final Deliverables (after AI completes the plan)

The AI must produce and hand back:
1. `ISSUES_LOG.md` — every defect, formatted per Part E.
2. `FIXES.md` — every fix, formatted per Part F (find/replace, AI-applyable).
3. `SCORECARD.md` — health scorecard + performance table per Part G.
4. `mock-data/*.csv` — every generated dataset (so user can re-run).
5. `tests/e2e.spec.js` — Playwright stub for the browser-only checks the AI couldn't run.
6. A short cover note (≤ 200 words) summarizing the highest-impact finding and the one fix to apply first.

---

## Verification (post-fix)

After fixes from `FIXES.md` are applied to `pl-dashboard-v8.html`:
1. Re-run Part B simulations on every mock dataset → all assertions must pass.
2. Re-run Part D stress tests → all budgets met or improved.
3. Re-generate `SCORECARD.md` → confirm 0 Critical / 0 High remaining.
4. Diff old vs new file → every change must trace back to a `FIX-NNN`.
5. Bump `version.json` to 8.0.0 with a release-notes summary.
6. Commit on `claude/dashboard-review-testing-CcCGw` and push.

---

## Deliverables Checklist

- [ ] `REVIEW_PLAN.md` (this file) — committed
- [ ] `AI_REVIEW_PROMPT.md` — committed (one-paste prompt for any AI)
- [ ] `ISSUES_LOG.md` — produced by AI
- [ ] `FIXES.md` — produced by AI (auto-applyable)
- [ ] `SCORECARD.md` — produced by AI
- [ ] `mock-data/` — produced by AI
- [ ] `tests/e2e.spec.js` — produced by AI (Playwright stub)
- [ ] Fixes applied; simulations re-pass
- [ ] `version.json` bumped, committed, pushed
