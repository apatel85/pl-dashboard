# P&L Dashboard v8 — Comprehensive Review & User Testing Plan

## Context

`pl-dashboard-v8.html` (4,190 lines) is a single-file, zero-backend P&L tracker. It uses vanilla JS + Chart.js + XLSX.js + IndexedDB + localStorage + File System Access API + Google Sheets API. Because it's a single file that holds all of a user's financial data client-side, a defect (XSS via category names, bad import mapping, broken backup restore, Sheets sync corruption) can silently destroy or leak data.

This plan is **AI-agnostic** — written so Claude, ChatGPT, or Gemini can execute it. Each step states (a) the action, (b) the expected result, (c) how to log a deviation as an issue, and (d) a resolution recipe. The plan is split into:
- **Part A: Static Code Review** (read-only, no browser)
- **Part B: Functional User Testing** (manual, in browser)
- **Part C: Issue Logging Format**
- **Part D: Resolution Playbook**
- **Part E: AI-Tool-Specific Execution Notes** (Claude / ChatGPT / Gemini)

The final review plan will be saved to both `/root/.claude/plans/` and `/home/user/pl-dashboard/REVIEW_PLAN.md` (the latter requires implementation phase — currently blocked by plan mode).

---

## Critical Files

| Path | Role |
|---|---|
| `/home/user/pl-dashboard/pl-dashboard-v8.html` | Target of review (single file, 4190 lines) |
| `/home/user/pl-dashboard/version.json` | Version metadata (currently v5.0.0; v8 is candidate build) |
| `/home/user/pl-dashboard/REVIEW_PLAN.md` | Where this plan will be saved on execution |
| `/home/user/pl-dashboard/ISSUES_LOG.md` | Created during review to log findings |

---

## Part A — Static Code Review (Phase 1)

Run before opening the file in a browser. Output: items appended to `ISSUES_LOG.md`.

### A1. Inventory Pass (~10 min)
1. Open `pl-dashboard-v8.html`. Note total lines, locate `<style>`, `<script>`, and major JS sections.
2. Build a function index: for each function, record name, line, ~LOC, and purpose. Flag any function > 80 LOC.
3. List all global variables/state (e.g., `txnSort`, `txnPage`, `parsedCSV`, `autoFileHandle`, `linkedFileHandle`).
4. List all storage keys: `CATEGORIES_KEY`, `GSHEETS_KEY`, `L2_META_KEY`, IndexedDB store names.

### A2. Security Review
Search the file for each pattern and verify safety:

| # | Pattern | Check |
|---|---|---|
| A2.1 | `innerHTML =` and template-string HTML concatenation | Confirm user-supplied data (category names, descriptions, filenames) is HTML-escaped. Flag every unescaped insertion. |
| A2.2 | `onclick="..."` inline handlers | Note count. Verify any dynamic `onclick` built from user data is escaped. |
| A2.3 | `eval`, `new Function`, `setTimeout("string")` | Must be zero. Flag any hit. |
| A2.4 | Google OAuth client_id | Confirm it's a public web client ID (not a secret). Confirm scopes are minimal (Sheets only). |
| A2.5 | `localStorage` for tokens | Verify OAuth access tokens have short TTL and are not long-lived refresh tokens. |
| A2.6 | CSV/XLSX import parsing | Confirm imported strings aren't injected into HTML without escape, and formula-injection (`=`, `+`, `-`, `@` leading chars) is neutralized on **export** to CSV. |

### A3. Data Integrity Review
| # | Check |
|---|---|
| A3.1 | IndexedDB schema: `onupgradeneeded` handles version bumps from prior v5–v7 without dropping the store. |
| A3.2 | `dbBulkPut` is wrapped in a single transaction and rolls back atomically on error. |
| A3.3 | Numeric parsing: `parseFloat`/`Number` calls strip currency symbols, thousands separators, and handle negative parentheses `(123.45)`. |
| A3.4 | Date parsing: handles `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY` ambiguously — confirm user is asked or the format is locked. |
| A3.5 | Floating-point money: amounts stored as cents (int) or as float? If float, flag `0.1 + 0.2` precision risk in totals. |
| A3.6 | Layer 1 snapshots: rolling buffer of 5 — confirm oldest evicted, not corrupted. |
| A3.7 | Google Sheets sync: pull replaces or merges? Confirm there's a confirmation prompt before destructive overwrite. |

### A4. Code Quality
| # | Check |
|---|---|
| A4.1 | Functions > 80 LOC flagged for refactor candidates. |
| A4.2 | Duplicate dropdown-refresh / table-render logic — note for DRY. |
| A4.3 | Magic strings — list and recommend moving to a `const` block at top. |
| A4.4 | Error handling: `FileReader.onerror`, `IDBRequest.onerror`, `fetch.catch` — every async op should surface a toast on failure. |
| A4.5 | Accessibility: tab navigation order, ARIA labels on icon buttons, color-contrast on dark theme, focus rings. |
| A4.6 | Performance: tables with 10k+ rows — confirm virtualization or pagination is enforced before render. |

### A5. Browser Compatibility
| # | Check |
|---|---|
| A5.1 | File System Access API — gated behind feature detection? Graceful fallback for Firefox/Safari? |
| A5.2 | IndexedDB — fallback message if unavailable (private mode)? |
| A5.3 | `?.` and `??` (ES2020) — confirm target browsers. |

Log every finding to `ISSUES_LOG.md` using the format in Part C.

---

## Part B — Functional User Testing (Phase 2)

Open `pl-dashboard-v8.html` in **Chrome (latest)**. Open DevTools → Console + Network + Application tabs. Watch console for errors during every step.

### B0. Pre-flight
1. Use a clean profile or clear site data (`Application → Storage → Clear site data`).
2. Reload. Expected: dashboard loads with zero transactions, no console errors, no red toasts.
3. **Issue log if:** any console error, missing chart canvas, broken icon font, layout overflow.

### B1. Quick-Add (Transactions)
1. Click **Add** tab.
2. Enter: Date=today, Type=Revenue, Category=existing default, Description="Test 1", Amount=1234.56. Submit with Enter key.
3. Expected: toast "Saved", form resets, Dashboard KPIs update.
4. Repeat for Type=Expense, Amount=200.
5. Edge cases:
   - Amount = `0` → expect rejection or clear warning
   - Amount = `-50` → confirm app convention (does sign indicate type?)
   - Amount = `1,234.56` (with comma) → confirm parsing
   - Amount = `(99.00)` (accounting negative) → confirm parsing
   - Description with `<script>alert(1)</script>` → **must render as text, not execute**. If alert fires → CRITICAL XSS issue.
   - Date in 1899 / 2099 → confirm accepted or bounded.

### B2. Transactions Table
1. Add 25 transactions via Quick-Add (mix revenue/expense across 3 months).
2. Verify pagination renders, page size selector works.
3. Sort by each column (Date, Amount, Type, Category, Description) asc/desc — verify stable sort.
4. Filter by Type, Month, Year, Category — each combination should narrow results correctly.
5. Search box: partial match on description; verify case-insensitive.
6. Inline edit a row: change amount, save, confirm Dashboard totals update.
7. Delete a row: confirm prompt, confirm KPI updates and snapshot creation.

### B3. Dashboard KPIs & Charts
1. With data from B2, verify: Total Revenue, Total Expenses, Net Profit, Margin% match a hand calculation.
2. Verify all 4 charts render: Revenue vs Expenses (monthly), Net Profit trend, Revenue by Category, Expense breakdown.
3. Hover tooltips show correct values.
4. Resize window — charts reflow without overlap.

### B4. Revenue / Expense / Monthly Summary tabs
1. Confirm Revenue tab shows only revenue rows; totals match Dashboard.
2. Confirm Expense tab shows only expenses; totals match.
3. Monthly Summary: each row = month; revenue/expense/net match sum of underlying rows.

### B5. Bulk Import (CSV)
1. Prepare CSV with 100 rows: headers `date,type,category,description,amount`.
2. Drag-drop into upload zone. Mapping modal opens.
3. Auto-detected mappings should be correct; manually adjust one and re-confirm.
4. Submit; expected: progress indicator, success toast with count, table updates.
5. Edge cases:
   - CSV with BOM
   - CSV with quoted fields containing commas
   - CSV with empty rows
   - CSV with formula injection (`=cmd|' /C calc'!A0`) — must be neutralized on later export
   - XLSX with multiple sheets — confirm correct sheet picked or prompted
   - 10,000-row file — confirm completes < 30s and UI doesn't freeze (look for `requestIdleCallback` / chunking)

### B6. Categories
1. Open Categories tab. Add a new category "Test-Cat".
2. Rename it to "Test-Cat-Renamed" — verify all existing transactions referencing it update.
3. Delete it — confirm prompt, confirm transactions are either reassigned or marked uncategorized per app rule.
4. Add a category named `<img src=x onerror=alert(1)>` — must not execute. If it does → CRITICAL XSS.

### B7. Export
1. Click Export CSV — open file in text editor: headers present, all rows, correct quoting, no formula injection in cells beginning with `=`/`+`/`-`/`@` (must be prefixed with `'`).
2. Click Export XLSX — open in Excel/LibreOffice: two sheets (Transactions + Monthly Summary), correct types, totals.

### B8. Backup Layer 1 — Snapshots
1. Open Backup tab. Confirm latest snapshot exists.
2. Make a destructive change (delete 5 rows).
3. Restore previous snapshot. Confirm rows return.
4. Verify rolling 5 limit: trigger 6 snapshots, confirm oldest is evicted.

### B9. Backup Layer 2 — Local File Auto-Save (Chrome only)
1. Click "Link file" — pick a local `.csv`. Grant permission.
2. Add a transaction; wait for auto-save tick (or trigger manual save).
3. Open the file externally — verify it reflects new data.
4. Reload page — confirm app remembers the link (`autoFileHandle` persisted via IndexedDB).
5. Edge: revoke permission in browser — app should surface a clear "permission lost" message.

### B10. Backup Layer 3 — Google Sheets Sync
1. Click Sign in with Google. Grant Sheets scope.
2. Create new sheet or link existing.
3. **Push to Sheets**: open sheet in Google Sheets, confirm rows match.
4. **Pull from Sheets**: edit a cell in Sheets, pull, confirm change reflected with destructive-overwrite confirmation.
5. Conflict test: edit locally + remotely → confirm conflict-resolution policy (last-write-wins, merge, or error).
6. Sign out — confirm token cleared from localStorage.

### B11. Settings & Storage Health
1. Verify Storage Health dashboard shows IndexedDB quota usage.
2. Click "Request Persistent Storage" — confirm browser prompts and state updates.
3. Click "Clear All Data" — must require typed confirmation, must wipe IndexedDB + localStorage + unlink file handles.

### B12. Cross-Cutting
| # | Test |
|---|---|
| B12.1 | Hard refresh after each major op — data persists. |
| B12.2 | Open in 2 tabs simultaneously — confirm no IndexedDB lock errors or split-brain writes. |
| B12.3 | Offline mode (DevTools → Network → Offline): all features except Sheets work; Sheets fails with clear error. |
| B12.4 | Print preview: layout is readable (1-page Dashboard summary if intended). |
| B12.5 | Keyboard-only nav: Tab through all controls; no traps; visible focus. |
| B12.6 | Mobile viewport (DevTools 375×812): tables scroll, no overflow, nav usable. |
| B12.7 | Lighthouse audit: Performance, Accessibility, Best Practices, SEO. Log scores. |

---

## Part C — Issue Logging Format

Append each finding to `ISSUES_LOG.md` using this template:

```markdown
## ISSUE-<NNN>: <Short title>
- **Section:** A2.1 / B5 / etc.
- **Severity:** Critical | High | Medium | Low | Info
- **Type:** Security | Data-loss | Functional | UX | Performance | Accessibility | Code-quality
- **Location:** pl-dashboard-v8.html:<line> (function `<name>`)
- **Steps to reproduce:** 1) … 2) … 3) …
- **Expected:** …
- **Actual:** …
- **Evidence:** console error text / screenshot path / sample data
- **Suggested fix:** see Resolution R-<id>
```

Severity guide:
- **Critical:** data loss, XSS, auth leak, app won't load
- **High:** feature broken, silent corruption, no error surfaced
- **Medium:** wrong calculation in edge case, missing validation
- **Low:** cosmetic, minor UX
- **Info:** code smell, refactor candidate

---

## Part D — Resolution Playbook

Each recipe = problem → diagnosis → patch → verification.

### R-1: XSS via unescaped user strings in innerHTML
- **Diagnose:** grep for `innerHTML\s*=` and template literals building HTML from user data (category names, descriptions, filenames).
- **Patch:** Add `function escapeHtml(s){return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}` and wrap every interpolated user value. Prefer `textContent` over `innerHTML` where possible.
- **Verify:** Repeat B1 / B6 with `<script>alert(1)</script>` payload — must render literally.

### R-2: CSV formula injection on export
- **Diagnose:** Open exported CSV; check cells starting with `=`, `+`, `-`, `@`.
- **Patch:** Before writing, prefix offending cells with `'` (or wrap in `"` and prefix tab character).
- **Verify:** Re-export, open in Excel — no formula execution prompt.

### R-3: Floating-point money drift
- **Diagnose:** Sum 0.1 + 0.2 across many rows; compare to expected.
- **Patch:** Store amounts as integer cents; format only at render time. Or use `(Math.round(x*100)/100)` for display and a `kahanSum` helper for totals.
- **Verify:** Import 10k rows of $0.01 — total reads exactly $100.00.

### R-4: Ambiguous date parsing
- **Patch:** Lock import to ISO `YYYY-MM-DD`; for other formats, prompt user in mapping modal with a "Date format" dropdown.
- **Verify:** Import a CSV with `03/04/2025` — modal asks `DD/MM` vs `MM/DD`.

### R-5: IndexedDB migration drops data
- **Patch:** In `onupgradeneeded`, branch on `oldVersion` and create indexes only if missing; never delete the store. Take a Layer-1 snapshot at the start of every upgrade.
- **Verify:** Load v7 data file in v8; confirm zero loss.

### R-6: Destructive Sheets pull without confirmation
- **Patch:** Before overwriting local data on pull, show modal with row counts (local vs remote) and require explicit "Replace local data" click. Auto-snapshot first.
- **Verify:** B10 step 4 — confirmation shown.

### R-7: Long functions / global state
- **Patch:** Extract by feature (`renderTxnTable`, `applyMapping`, `exportXLSX`) into IIFE modules or separate `<script type="module">` blocks. Replace globals with a single `state` object.
- **Verify:** Lint passes; all features still work end-to-end.

### R-8: Missing async error toasts
- **Patch:** Wrap every async op in try/catch and call `showToast(err.message, 'error')` in catch.
- **Verify:** Simulate IndexedDB quota exceeded (DevTools) — toast appears.

### R-9: Accessibility — missing ARIA / focus
- **Patch:** Add `aria-label` to icon-only buttons, `role="status"` to toast container, ensure `:focus-visible` outline ≥ 2px with sufficient contrast.
- **Verify:** Lighthouse Accessibility ≥ 95; keyboard-only walk-through completes.

### R-10: Two-tab IndexedDB conflicts
- **Patch:** Use `BroadcastChannel('pl-dashboard')` to notify other tabs of writes and refresh state. Or detect via `navigator.locks.request` for serialized writes.
- **Verify:** B12.2 passes.

### R-11: File System Access fallback
- **Patch:** Feature-detect `window.showOpenFilePicker`; if absent, hide Layer-2 UI and show "Auto-save to disk requires Chrome/Edge" notice.
- **Verify:** Open in Firefox — no broken button.

### R-12: Large import freezes UI
- **Patch:** Chunk import in batches of 500 with `await new Promise(r => setTimeout(r))` between chunks; show progress bar.
- **Verify:** Import 10k rows — UI remains responsive.

---

## Part E — AI-Tool-Specific Execution Notes

### E1. For Claude (Claude Code / claude.ai)
- Use the `Read` tool on `pl-dashboard-v8.html` in 500-line windows (Read with `offset`/`limit`).
- Use `Bash` with `grep -n` for pattern searches (A2 checks).
- Spawn an `Explore` subagent for any open-ended question to keep the main context lean.
- Manual UI testing requires a human operator since Claude cannot drive a browser in this environment — the human follows Part B and pastes findings back; Claude logs them via `Edit` into `ISSUES_LOG.md`.
- For resolution, switch out of plan mode then apply fixes with `Edit`; commit per Part F.

### E2. For ChatGPT (with Code Interpreter / Advanced Data Analysis)
- Upload `pl-dashboard-v8.html` to the chat.
- Ask: "Run the Part A static review against this file and output `ISSUES_LOG.md`."
- Code Interpreter can `grep`/`re.findall` patterns from A2 and produce a function inventory.
- ChatGPT cannot run the HTML; the human runs Part B locally and pastes console errors / screenshots back.
- For fixes, ask for unified diffs section-by-section (the file is too large for a single rewrite).

### E3. For Gemini (Gemini 2.x in AI Studio / Gemini app)
- Paste file contents (split into ~200KB chunks if needed) or upload via Files API.
- Use Gemini's long context to run Part A in one pass; explicitly request output **only** as `ISSUES_LOG.md` entries.
- Same human-in-the-loop constraint for Part B.
- For fixes, request diffs and apply manually.

### E4. Common Guardrails (all tools)
- Never commit or push automatically without user approval.
- Always create a Layer-1 snapshot (open the app, click "Snapshot now") **before** applying any fix to the live file.
- Apply one resolution at a time and re-run the relevant Part-B section before moving to the next.

---

## Part F — Verification & Sign-off

After all fixes are applied:
1. Re-run **all** of Part B from a clean profile.
2. Run Lighthouse — record Performance / Accessibility / Best Practices / SEO scores in `ISSUES_LOG.md` under a "Final scores" section.
3. Diff `pl-dashboard-v8.html` against the pre-review version; ensure every change traces to an `ISSUE-NNN`.
4. Bump `version.json` to v8.0.0 with release notes summarizing categories of fixes.
5. Commit on branch `claude/dashboard-review-testing-CcCGw` with message `chore(v8): apply review fixes (ISSUE-001..NNN)` and push.

---

## Deliverables Checklist (post-execution)

- [ ] `/home/user/pl-dashboard/REVIEW_PLAN.md` — this plan, committed
- [ ] `/home/user/pl-dashboard/ISSUES_LOG.md` — all findings logged
- [ ] Fixes applied per Part D, each traceable to an issue ID
- [ ] All Part B tests re-passed after fixes
- [ ] Lighthouse scores recorded
- [ ] `version.json` updated and changes committed/pushed to `claude/dashboard-review-testing-CcCGw`
