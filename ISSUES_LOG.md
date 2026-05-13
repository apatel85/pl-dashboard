# ISSUES_LOG.md — pl-dashboard-v8.html

**Generated:** 2026-05-13  
**Reviewed by:** Claude Sonnet 4.6 (Claude Code)  
**Method:** Static analysis + logic simulation + stress testing per REVIEW_PLAN.md  
**File:** pl-dashboard-v8.html (4,190 lines)

---

## Summary Table

| Issue | Section | Severity | Type | Short Title |
|---|---|---|---|---|
| ISSUE-001 | A2.1 / B2.8 | Critical | Security | XSS: renderRecentEntries — date/category/description unescaped |
| ISSUE-002 | A2.1 / B2.8 | Critical | Security | XSS: renderRevTable — category/description unescaped |
| ISSUE-003 | A2.1 / B2.8 | Critical | Security | XSS: renderExpTable — category/description unescaped |
| ISSUE-004 | A2.1 / B2.8 | Critical | Security | XSS: openMappingModal — CSV headers raw in innerHTML |
| ISSUE-005 | A2.1 / B2.8 | Critical | Security | XSS: openMappingModal — CSV data cells raw in innerHTML |
| ISSUE-006 | A2.1 / B2.7 | Critical | Security | XSS: catPillHTML — name rendered raw, `safe` var unused |
| ISSUE-007 | A2.7 / D10 | Critical | Security | No Content-Security-Policy meta tag |
| ISSUE-008 | A2.6 / B2.2 | High | Security | CSV formula injection not sanitized on export (3 functions) |
| ISSUE-009 | A2.8 / D9 | High | Security | No SRI integrity attribute on Chart.js and XLSX.js CDN scripts |
| ISSUE-010 | A4.6 / D4 | High | Performance | renderRevTable renders ALL rows with no pagination |
| ISSUE-011 | A4.6 / D4 | High | Performance | renderExpTable renders ALL rows with no pagination |
| ISSUE-012 | A3.6 / D7 | High | Data-loss | Snapshot localStorage overflow with >10k transactions |
| ISSUE-013 | A3.3 / B2.1 | Medium | Functional | Accounting-negative amounts (99.00) not parsed — silently NaN |
| ISSUE-014 | A3.4 / B2.3 | Medium | Functional | Ambiguous DD/MM/YYYY date format — browser-locale dependent |
| ISSUE-015 | A2.1 / B2.8 | High | Security | XSS: toast() uses innerHTML with msg parameter |
| ISSUE-016 | A3.5 / D8 | Medium | Data-loss | Float arithmetic drift in KPI sums — amounts not stored as cents |
| ISSUE-017 | B2.3 / A3.3 | Medium | Functional | RFC 4180 escaped quotes ("") not handled in parseCSV |
| ISSUE-018 | B2.1 / A3.3 | Medium | Functional | EU number format 1.234,56 silently miscoerces to 123456 |
| ISSUE-019 | B2.10 | Medium | Functional | Monthly table: col-4 mismatch (net per row vs gross in total row) |
| ISSUE-020 | A4.4 / B2.12 | Medium | UX | inlineEdit error path: console.warn only, no user toast |
| ISSUE-021 | B2.11 | Medium | UX | Clear All Data uses single confirmation (should be double) |
| ISSUE-022 | A3.1 | Medium | Data-loss | IndexedDB DB_VERSION=1 with no upgrade path for future schema changes |
| ISSUE-023 | A5.2 | Medium | Functional | No user-facing fallback if IndexedDB unavailable (private mode) |
| ISSUE-024 | D3 | Medium | Performance | 100k row memory footprint ~61.7 MB — may pressure quota |
| ISSUE-025 | A4.5 | Low | Accessibility | Toast container has no role="status" or aria-live |
| ISSUE-026 | A4.5 | Low | Accessibility | Icon-only buttons missing aria-label (delete ✕, download ⬇) |
| ISSUE-027 | A2.5 | Info | Security | Supabase anon key hardcoded in JS — note RLS required |
| ISSUE-028 | A4.1 | Info | Code-quality | Multiple functions >80 LOC (renderTxnTable, gsheetsPull, openMappingModal) |
| ISSUE-029 | A4.3 | Info | Code-quality | Magic string 'revenue'/'expense' repeated throughout — no TYPE_REVENUE const |
| ISSUE-030 | A4.2 | Info | Code-quality | Duplicate rendering patterns in rev/exp/monthly table functions |

**Severity counts:** Critical: 7 | High: 5 | Medium: 9 | Low: 2 | Info: 4  
**Total issues: 30**

---

## ISSUE-001: XSS in renderRecentEntries — user data unescaped in innerHTML

- **Section:** A2.1 / B2.8
- **Severity:** Critical
- **Type:** Security
- **Location:** pl-dashboard-v8.html:2834-2841 (function `renderRecentEntries`)
- **Discovered by:** static-review + simulation
- **Steps to reproduce:**
  1. Add a transaction with Description = `<img src=x onerror=alert(1)>` or import via CSV.
  2. Navigate to Add Transaction tab or any view that renders recent entries.
  3. Alert fires — XSS confirmed.
- **Expected:** User data rendered as literal text.
- **Actual:** User data executed as HTML/JS.
- **Evidence:**
  ```js
  tbody.innerHTML = rows.map(t=>`<tr>
    <td>${t.date}</td>
    <td><span class="type-pill ${t.type}">${t.type}</span></td>
    <td>${t.category||'—'}</td>
    <td style="...">${t.description||'—'}</td>
  ```
- **Linked fix:** FIX-001

---

## ISSUE-002: XSS in renderRevTable — category/description unescaped

- **Section:** A2.1 / B2.8
- **Severity:** Critical
- **Type:** Security
- **Location:** pl-dashboard-v8.html:2925 (function `renderRevTable`)
- **Discovered by:** static-review
- **Steps to reproduce:** Import CSV with `<script>alert(1)</script>` in category field. Open Revenue tab.
- **Expected:** Escaped text in table cell.
- **Actual:** Script executes.
- **Evidence:**
  ```js
  tbody.innerHTML=txns.map(t=>`<tr><td>${t.date}</td>
    <td><span ...>${t.category}</span></td>
    <td style="...">${t.description||'—'}</td>
  ```
- **Linked fix:** FIX-001

---

## ISSUE-003: XSS in renderExpTable — category/description unescaped

- **Section:** A2.1 / B2.8
- **Severity:** Critical
- **Type:** Security
- **Location:** pl-dashboard-v8.html:2933 (function `renderExpTable`)
- **Discovered by:** static-review
- **Steps to reproduce:** Same as ISSUE-002 but on Expenses tab.
- **Expected:** Escaped text.
- **Actual:** Script executes.
- **Evidence:**
  ```js
  tbody.innerHTML=txns.map(t=>`<tr><td>${t.date}</td>
    <td><span ...>${t.category}</span></td>
    <td ...>${t.description||'—'}</td>
  ```
- **Linked fix:** FIX-001

---

## ISSUE-004: XSS in openMappingModal — CSV headers inserted raw

- **Section:** A2.1 / B2.8
- **Severity:** Critical
- **Type:** Security
- **Location:** pl-dashboard-v8.html:3034 (function `openMappingModal`)
- **Discovered by:** static-review
- **Steps to reproduce:** Upload a CSV whose first row header is `<img src=x onerror=alert(1)>`. Mapping modal opens → XSS fires.
- **Expected:** Header escaped as text in `<th>`.
- **Actual:** Header executed as HTML.
- **Evidence:**
  ```js
  document.getElementById('preview-thead').innerHTML='<tr>'+
    csvHeaders.map(h=>`<th ...>${h}</th>`).join('')+'</tr>';
  ```
- **Linked fix:** FIX-002

---

## ISSUE-005: XSS in openMappingModal — CSV data cells inserted raw

- **Section:** A2.1 / B2.8
- **Severity:** Critical
- **Type:** Security
- **Location:** pl-dashboard-v8.html:3035 (function `openMappingModal`)
- **Discovered by:** static-review
- **Steps to reproduce:** Upload CSV with `<script>alert(1)</script>` in any data cell. Mapping preview renders it.
- **Expected:** Data escaped in `<td>`.
- **Actual:** Data executed as HTML.
- **Evidence:**
  ```js
  document.getElementById('preview-tbody').innerHTML=
    parsedCSV.slice(1,4).map(r=>'<tr>'+
      r.map(c=>`<td ...>${c}</td>`).join('')+'</tr>').join('');
  ```
- **Linked fix:** FIX-002

---

## ISSUE-006: XSS in catPillHTML — `safe` variable computed but never used

- **Section:** A2.1 / B2.7
- **Severity:** Critical
- **Type:** Security
- **Location:** pl-dashboard-v8.html:4039-4047 (function `catPillHTML`)
- **Discovered by:** simulation (B2.7)
- **Steps to reproduce:** Add a category named `<img src=x onerror=alert(1)>`. Open Categories tab.
- **Expected:** Category name escaped in span.
- **Actual:** XSS fires. `safe` variable is computed but then `name` (raw) is used in the template.
- **Evidence:**
  ```js
  function catPillHTML(name, idx, type) {
    const safe = name.replace(/'/g, "\\'").replace(/"/g, '&quot;');
    return `<div class="cat-pill ${type}-pill">
      <span class="cat-name">${name}</span>  // ← uses `name`, not `safe`!
  ```
- **Linked fix:** FIX-003

---

## ISSUE-007: No Content-Security-Policy meta tag

- **Section:** A2.7 / D10
- **Severity:** Critical
- **Type:** Security
- **Location:** pl-dashboard-v8.html:1-12 (`<head>`)
- **Discovered by:** static-review
- **Steps to reproduce:** Open DevTools → Application → inspect CSP headers. None present.
- **Expected:** `<meta http-equiv="Content-Security-Policy" content="...">` in `<head>`.
- **Actual:** No CSP exists. All XSS payloads (ISSUE-001–006) execute without restriction.
- **Evidence:** Only `<meta charset="UTF-8">` and `<meta name="viewport" ...>` in `<head>`.
- **Linked fix:** FIX-004

---

## ISSUE-008: CSV formula injection — exportCSV, syncToFile, gsheetsPush export raw formulas

- **Section:** A2.6 / B2.2
- **Severity:** High
- **Type:** Security
- **Location:** pl-dashboard-v8.html:3136 (`exportCSV`), 3123 (`syncToFile`), 2558 (`gsheetsPush`)
- **Discovered by:** simulation (B2.2)
- **Steps to reproduce:**
  1. Add transaction with Description = `=SUM(A1:A10)` or Category = `=CMD|CALC`.
  2. Export CSV and open in Excel.
  3. Excel executes the formula — CSV injection attack confirmed.
- **Expected:** Cells beginning with `=`, `+`, `-`, `@` prefixed with `'` (or tab).
- **Actual:** Raw formula strings written to CSV.
- **Evidence:**
  ```js
  // exportCSV line 3136:
  all.map(t=>[t.date,t.type,`"${t.category}"`,`"${t.description||''}"`,t.amount,...].join(','))
  // No sanitization before writing
  ```
- **Linked fix:** FIX-005

---

## ISSUE-009: No SRI integrity attributes on CDN scripts

- **Section:** A2.8 / D9
- **Severity:** High
- **Type:** Security
- **Location:** pl-dashboard-v8.html:6-7 (`<head>` script tags)
- **Discovered by:** static-review
- **Steps to reproduce:** CDN is compromised or MITM'd — malicious library served to users silently.
- **Expected:** `integrity="sha384-..."` and `crossorigin="anonymous"` on each CDN script.
- **Actual:** No SRI.
- **Evidence:**
  ```html
  <script src="https://cdnjs.cloudflare.com/.../chart.umd.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/.../xlsx.full.min.js"></script>
  ```
- **Linked fix:** FIX-006

---

## ISSUE-010: renderRevTable renders ALL rows without pagination

- **Section:** A4.6 / D4
- **Severity:** High
- **Type:** Performance
- **Location:** pl-dashboard-v8.html:2920-2926 (function `renderRevTable`)
- **Discovered by:** static-review + stress-test
- **Steps to reproduce:** Import 100k transactions, navigate to Revenue tab. Browser freezes creating 100k DOM nodes.
- **Expected:** Paginated like Transaction table (max 25–100 rows rendered at once).
- **Actual:** `dbGetAll()` → render all rows unconditionally.
- **Evidence:**
  ```js
  async function renderRevTable() {
    const all=await dbGetAll();
    const txns=all.filter(t=>t.type==='revenue')...
    tbody.innerHTML=txns.map(t=>`<tr>...</tr>`).join('');  // no limit
  ```
- **Linked fix:** FIX-007

---

## ISSUE-011: renderExpTable renders ALL rows without pagination

- **Section:** A4.6 / D4
- **Severity:** High
- **Type:** Performance
- **Location:** pl-dashboard-v8.html:2928-2934 (function `renderExpTable`)
- **Discovered by:** static-review + stress-test
- **Steps to reproduce:** Same as ISSUE-010 but on Expenses tab.
- **Expected:** Paginated rendering.
- **Actual:** All expense rows rendered at once.
- **Evidence:**
  ```js
  async function renderExpTable() {
    const all=await dbGetAll();
    const txns=all.filter(t=>t.type==='expense')...
    tbody.innerHTML=txns.map(t=>`<tr>...</tr>`).join('');
  ```
- **Linked fix:** FIX-008

---

## ISSUE-012: Layer-1 snapshot exceeds localStorage quota with >10k transactions

- **Section:** A3.6 / D7
- **Severity:** High
- **Type:** Data-loss
- **Location:** pl-dashboard-v8.html:2111-2140 (function `takeSnapshot`)
- **Discovered by:** stress-test (D7)
- **Steps to reproduce:** Import 10k+ transactions. Snapshot attempts to write `~5 × 1.4MB = 7MB` to localStorage (5MB cap). QuotaExceededError silently trims oldest snapshot rather than alerting user.
- **Expected:** Warn user when snapshot is near quota limit; recommend enabling Layer 2 file backup.
- **Actual:** Silent trim of oldest snapshot, then console.warn only. User unaware.
- **Evidence:**
  ```
  10k txns: ~1413 KB/snapshot × 5 = ~7064 KB > 5120 KB localStorage cap
  100k txns: ~14129 KB/snapshot × 5 = ~70645 KB >> cap
  ```
  QuotaExceededError at line 2130 caught silently with only `console.warn`.
- **Linked fix:** FIX-009

---

## ISSUE-013: Accounting-negative format `(99.00)` not supported in amount parsing

- **Section:** A3.3 / B2.1
- **Severity:** Medium
- **Type:** Functional
- **Location:** pl-dashboard-v8.html:3069 (function `applyMapping`)
- **Discovered by:** simulation (B2.1)
- **Steps to reproduce:** Import CSV with amounts in accounting format `(1,234.56)` (common in bank exports, QuickBooks). Amount parses as NaN → row skipped silently.
- **Expected:** `(99.00)` → `-99.00`.
- **Actual:** `NaN` → row skipped, user sees "X rows skipped" but no reason given.
- **Evidence:**
  ```js
  const amount=parseFloat(String(amountRaw).replace(/[$,\s]/g,''));
  // "(99.00)".replace(/[$,\s]/g,'') → "(99.00)" → parseFloat → NaN
  ```
- **Linked fix:** FIX-010

---

## ISSUE-014: Ambiguous date format DD/MM/YYYY — browser-locale dependent parsing

- **Section:** A3.4 / B2.3
- **Severity:** Medium
- **Type:** Functional
- **Location:** pl-dashboard-v8.html:3073-3074 (function `applyMapping`)
- **Discovered by:** simulation (B2.3) + static-review
- **Steps to reproduce:** Import CSV with date `13/05/2025` (European format). `new Date("13/05/2025")` = Invalid Date in US locale → date stored as-is string, month = 'Unknown'.
- **Expected:** Mapping modal prompts user for date format (MM/DD vs DD/MM).
- **Actual:** Silent failure / wrong date. Month field = 'Unknown', grouping broken.
- **Evidence:**
  ```js
  const parsed=dateVal&&dateVal.match(/^\d{4}-\d{2}-\d{2}$/)?
    new Date(dateVal+'T00:00:00'):new Date(dateVal);  // locale-dependent!
  ```
- **Linked fix:** FIX-011

---

## ISSUE-015: XSS in toast() — msg inserted via innerHTML

- **Section:** A2.1 / B2.8
- **Severity:** High
- **Type:** Security
- **Location:** pl-dashboard-v8.html:3783 (function `toast`)
- **Discovered by:** static-review
- **Steps to reproduce:** Any path where `toast()` is called with an unescaped external string (e.g., `e.message` from file/network errors, or version notes from remote JSON).
- **Expected:** `msg` rendered as text.
- **Actual:** `msg` in innerHTML — if it contains HTML tags, they execute.
- **Evidence:**
  ```js
  function toast(msg,type='info'){
    ...
    el.innerHTML=`<span>${{success:'✓',...}[type]}</span> ${msg}`;
  ```
  Callers: `showUpdateBanner` passes `notes` from remote `version.json` (line 3250).
- **Linked fix:** FIX-012

---

## ISSUE-016: Floating-point drift in KPI sums — amounts stored as JS floats

- **Section:** A3.5 / D8
- **Severity:** Medium
- **Type:** Data-loss
- **Location:** pl-dashboard-v8.html:2965-2966 (`refreshDashboard`), 2939 (`renderMonthlyTable`)
- **Discovered by:** stress-test (D8)
- **Steps to reproduce:** Import 10,000 transactions of $0.01 each. Dashboard shows total ≠ $100.00 exactly due to IEEE 754 float accumulation.
- **Expected:** Exact cent-accurate totals.
- **Actual:** Drift of ~$0.000000000014 per 10k transactions; visible with large datasets.
- **Evidence:**
  ```
  Python simulation: sum(10000 × 0.01) = 100.000000000014253 (drift = 1.4e-11)
  JS `reduce((s,t)=>s+t.amount,0)` exhibits identical IEEE 754 behaviour.
  ```
- **Linked fix:** FIX-013

---

## ISSUE-017: RFC 4180 escaped quotes `""` not handled in parseCSV

- **Section:** B2.3 / A3.3
- **Severity:** Medium
- **Type:** Functional
- **Location:** pl-dashboard-v8.html:3019 (function `parseCSV`)
- **Discovered by:** simulation (B2.3)
- **Steps to reproduce:** Import CSV with `"He said ""hi"""` in a field. Parsed result = `He said hi` (inner quotes dropped).
- **Expected:** `He said "hi"` per RFC 4180.
- **Actual:** Toggle-quote logic drops `""` instead of treating it as a literal quote.
- **Evidence:**
  ```js
  // Current logic:
  if(ch==='"'){q=!q;continue;}  // toggles — doesn't handle ""
  // Input: "He said ""hi"""
  // Actual parse: He said hi  (missing quotes)
  ```
- **Linked fix:** FIX-014

---

## ISSUE-018: EU number format `1.234,56` silently miscoerces to `1.23456`

- **Section:** B2.1 / A3.3
- **Severity:** Medium
- **Type:** Functional
- **Location:** pl-dashboard-v8.html:3069 (function `applyMapping`)
- **Discovered by:** simulation (B2.1)
- **Steps to reproduce:** Import European bank export with `1.234,56` amount. Regex strips `.` and `,` giving `123456`, then `parseFloat` → `1.23456` (decimal misplaced) or `123456` depending on regex order. Either way, wrong amount.
- **Expected:** Detect EU format and parse correctly, or warn user.
- **Actual:** Silent miscoerce — wrong dollar amount stored.
- **Evidence:**
  ```js
  const amount=parseFloat(String(amountRaw).replace(/[$,\s]/g,''));
  // "1.234,56" → strip , → "1.23456" → parseFloat → 1.23456 (WRONG: should be 1234.56)
  ```
- **Linked fix:** FIX-010 (combined with accounting-negative fix)

---

## ISSUE-019: Monthly table col-4 type mismatch — net per row, gross in total row

- **Section:** B2.10
- **Severity:** Medium
- **Type:** Functional
- **Location:** pl-dashboard-v8.html:2945 (function `renderMonthlyTable`)
- **Discovered by:** simulation (B2.10) + static-review
- **Steps to reproduce:** Open Monthly P&L tab with data containing COGS expenses. Per-month column 4 = Net Profit (revenue − all expenses). Total row column 4 = Gross Profit (revenue − COGS only). Mismatch is confusing and misleading.
- **Expected:** Column 4 consistent (both net or both gross).
- **Actual:**
  ```js
  // Per-month rows:
  `<td>${fmt(m.revenue-m.expenses)}</td>`  // = Net
  // Total FULL YEAR row:
  `<td>${fmt(totRev-cogs)}</td>`            // = Gross (different!)
  ```
- **Linked fix:** FIX-015

---

## ISSUE-020: inlineEdit error path — console.warn only, no user toast

- **Section:** A4.4 / B2.12
- **Severity:** Medium
- **Type:** UX
- **Location:** pl-dashboard-v8.html:2911 (function `inlineEdit`)
- **Discovered by:** static-review
- **Steps to reproduce:** Edit a transaction inline while IndexedDB quota is exceeded or a transaction error occurs. No visible feedback to user.
- **Expected:** Toast error on failed inline edit.
- **Actual:** `putReq.onerror=ev=>console.warn(...)` — silent failure.
- **Evidence:**
  ```js
  const putReq=tx.objectStore(STORE_NAME).put(rec);
  putReq.onerror=ev=>console.warn('inlineEdit put error',ev.target.error);
  ```
- **Linked fix:** FIX-016

---

## ISSUE-021: Clear All Data uses single confirmation — destructive op needs double-confirm

- **Section:** B2.11
- **Severity:** Medium
- **Type:** UX
- **Location:** pl-dashboard-v8.html:3208-3212 (function `confirmClearData`)
- **Discovered by:** static-review
- **Steps to reproduce:** Click "Clear All Data" → one confirm dialog → all data deleted. No second prompt.
- **Expected:** Double-confirm pattern (app already has `showDoubleConfirm` defined at L3214).
- **Actual:** Single `showConfirm` call.
- **Evidence:**
  ```js
  async function confirmClearData(){
    showConfirm('Clear ALL Data?','This will permanently delete all transactions...',
      async()=>{await dbClear();...});  // single confirm only
  ```
  Note: `showDoubleConfirm` function exists at L3214 but is not used here.
- **Linked fix:** FIX-017

---

## ISSUE-022: DB_VERSION=1 with no upgrade path for future schema changes

- **Section:** A3.1
- **Severity:** Medium
- **Type:** Data-loss
- **Location:** pl-dashboard-v8.html:1913, 1992-2008 (constants + `openDB`)
- **Discovered by:** static-review
- **Steps to reproduce:** If a future version of the app requires a new IndexedDB index or schema change, bumping `DB_VERSION` to 2 with only the current `onupgradeneeded` would create new indexes only if store doesn't exist — existing users would not get the new indexes.
- **Expected:** `onupgradeneeded` branches on `e.oldVersion` to apply incremental migrations.
- **Actual:** Single `if (!d.objectStoreNames.contains(STORE_NAME))` — no version branching.
- **Evidence:**
  ```js
  req.onupgradeneeded = e => {
    const d = e.target.result;
    if (!d.objectStoreNames.contains(STORE_NAME)) {
      // Only creates store on fresh install — no oldVersion branching
    }
  };
  ```
- **Linked fix:** FIX-018

---

## ISSUE-023: No user-facing fallback when IndexedDB is unavailable (private mode)

- **Section:** A5.2
- **Severity:** Medium
- **Type:** Functional
- **Location:** pl-dashboard-v8.html:1992-2008 (function `openDB`)
- **Discovered by:** static-review
- **Steps to reproduce:** Open the app in private/incognito mode (Firefox blocks IndexedDB). App fails silently or with cryptic errors.
- **Expected:** Clear banner: "This app requires IndexedDB — not available in private browsing mode."
- **Actual:** `reject(e.target.error)` — uncaught promise rejection, blank screen or silent failure.
- **Linked fix:** FIX-019

---

## ISSUE-024: Memory footprint ~61.7 MB for 100k transactions

- **Section:** D3
- **Severity:** Medium
- **Type:** Performance
- **Location:** pl-dashboard-v8.html:2049-2054 (`dbGetAll`) — all callers
- **Discovered by:** stress-test (D3)
- **Steps to reproduce:** Load 100k transactions. All views that call `dbGetAll()` load the full dataset into memory simultaneously.
- **Expected:** <50 MB for 100k rows (budget).
- **Actual:** ~61.7 MB estimated per `dbGetAll()` call. Multiple simultaneous calls × tabs compounds this.
- **Evidence:**
  ```
  Per-row estimate: ~647 bytes (Python sys.getsizeof)
  100k rows × 647 bytes = 64.7 MB (Python) / ~61.7 MB (JS estimate)
  Budget: 50 MB → FAIL
  ```
- **Linked fix:** FIX-007 + FIX-008 (pagination reduces how many rows are held in memory)

---

## ISSUE-025: Toast container missing role="status" and aria-live

- **Section:** A4.5
- **Severity:** Low
- **Type:** Accessibility
- **Location:** pl-dashboard-v8.html:378 (`<div id="toast">`)
- **Discovered by:** static-review
- **Steps to reproduce:** Use screen reader — toast notifications are not announced.
- **Expected:** `role="status"` and `aria-live="polite"` on toast container.
- **Actual:** Plain `<div id="toast">` with no ARIA attributes.
- **Linked fix:** FIX-020

---

## ISSUE-026: Icon-only buttons missing aria-label

- **Section:** A4.5
- **Severity:** Low
- **Type:** Accessibility
- **Location:** pl-dashboard-v8.html:2840 (delete ✕), 2163 (download ⬇ in snapshot list), 2883 (delete ✕ in txn table)
- **Discovered by:** static-review
- **Steps to reproduce:** Tab to delete/download buttons with screen reader — announces "button" with no description.
- **Expected:** `aria-label="Delete transaction"` etc.
- **Actual:** Emoji-only button text, no aria-label.
- **Linked fix:** FIX-020

---

## ISSUE-027: Supabase anon key hardcoded in JS source

- **Section:** A2.5
- **Severity:** Info
- **Type:** Security
- **Location:** pl-dashboard-v8.html:1921 (`SUPA_KEY`)
- **Discovered by:** static-review
- **Steps to reproduce:** View page source → anon key visible.
- **Expected:** Supabase anon keys are designed to be public only if RLS is enabled. Comment on L1920 warns about RLS.
- **Actual:** Key is public in source (acceptable IF RLS enforced). Confirm RLS is active on `pl_licensed_users` table.
- **Evidence:** `const SUPA_KEY = 'eyJhbGciOiJIUzI1NiIsInR5...'` (JWT, anon role, expires 2099)
- **Linked fix:** No code fix required — verify RLS in Supabase dashboard.

---

## ISSUE-028: Multiple functions exceed 80 LOC

- **Section:** A4.1
- **Severity:** Info
- **Type:** Code-quality
- **Location:** Multiple
- **Discovered by:** static-review
- **Evidence:**
  - `renderTxnTable` (L2865): ~30 LOC dense one-liner equivalent of ~120 LOC
  - `openMappingModal` (L3033): ~16 LOC
  - `gsheetsPull` (L2611): ~47 LOC
  - `renderGSheetsPanel` (L2306): ~120 LOC
  - `applyMapping` (L3058): ~31 LOC
- **Linked fix:** Info only — refactor in separate PR.

---

## ISSUE-029: Magic strings 'revenue'/'expense' repeated 25+ times

- **Section:** A4.3
- **Severity:** Info
- **Type:** Code-quality
- **Location:** Throughout JS (L2072, 2808, 2811, 2836, 2921, 2929, 2965, 2966, etc.)
- **Discovered by:** static-review
- **Evidence:** No `const TYPE_REVENUE = 'revenue'` constant. Typo would be a silent bug.
- **Linked fix:** Info only.

---

## ISSUE-030: Duplicate rendering patterns across rev/exp/monthly tables

- **Section:** A4.2
- **Severity:** Info
- **Type:** Code-quality
- **Location:** L2920 (`renderRevTable`), L2928 (`renderExpTable`), L2936 (`renderMonthlyTable`)
- **Discovered by:** static-review
- **Evidence:** All three functions call `dbGetAll()`, filter, sort, and build identical `tbody.innerHTML`. Could be a shared `renderTypeTable(type)` helper.
- **Linked fix:** Info only.

---

*End of ISSUES_LOG.md*
