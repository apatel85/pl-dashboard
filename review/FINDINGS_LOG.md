# FINDINGS_LOG.md — pl-dashboard-v8.html

**Generated:** 2026-05-15  
**Auditor:** Independent principal engineer / security reviewer  
**Method:** Static analysis, Python simulation, stress tests  
**File:** pl-dashboard-v8.html (6,224 lines, v8.3.0)  
**Extends:** review/ISSUES_LOG.md (2026-05-13)

---

## Issues Resolved Since Prior Review

ISSUE-001 through ISSUE-007, ISSUE-009 through ISSUE-011, ISSUE-013 through ISSUE-015, ISSUE-017 through ISSUE-018, ISSUE-020 through ISSUE-021, ISSUE-023, ISSUE-025 — all resolved. See AUDIT_REPORT.md for confirmation status.

---

## Active Issues

### NEW-001 — XSS in showUpdateBanner via remote version.json

| Field | Value |
|---|---|
| **Severity** | High |
| **Type** | Security / DOM XSS |
| **File + line** | pl-dashboard-v8.html:4843 |
| **Discovery** | Manual inspection of innerHTML sites without escapeHtml |
| **Previously documented** | No |

**Code:**
```js
document.getElementById('update-banner-text').innerHTML =
  `<strong>v${data.latest_version}</strong> is available &nbsp;·&nbsp; ${notes}`;
```
`data` comes from `fetch(VERSION_CHECK_URL)` — the remote `version.json`. `data.latest_version` and `notes` (the first `summary` field) are injected without escaping.

**Reproduction:** Modify `version.json` to include `"summary": "<img src=x onerror=alert(1)>"`. On next version check the banner fires the payload.

**Expected:** Fields escaped with escapeHtml before injection.  
**Actual:** Raw strings from remote JSON rendered as HTML.

**Why it matters:** Same-repo attack vector — anyone who can push to the repo can inject JS into every user's browser via the version check. The banner auto-shows on load.

**Recommended fix:**
```js
document.getElementById('update-banner-text').innerHTML =
  `<strong>v${escapeHtml(data.latest_version)}</strong> is available &nbsp;·&nbsp; ${escapeHtml(notes)}`;
```

**Confidence:** High

---

### NEW-002 — XSS in openChangelog via remote version.json

| Field | Value |
|---|---|
| **Severity** | High |
| **Type** | Security / DOM XSS |
| **File + line** | pl-dashboard-v8.html:4880 |
| **Discovery** | Manual inspection |
| **Previously documented** | No |

**Code (excerpt):**
```js
document.getElementById('changelog-body').innerHTML = releases.map((rel,i) =>
  `...<span class="ver-tag">${rel.version}</span>
   <span class="ver-date">${rel.date||''}</span>
   <div class="ver-title">${rel.title||''}</div>
   ...<span>${c.text}</span>...`
).join('');
```
`releases` comes from `remoteVerData?.release_notes` — the fetched `version.json`. All six fields (`rel.version`, `rel.date`, `rel.title`, `c.type`, `c.text`, `latest`) are rendered without escaping.

**Why it matters:** `c.text` is long-form prose injected directly — an attacker who controls `version.json` can deliver arbitrary HTML/JS to every user who opens the "What's New" modal.

**Recommended fix:** Wrap each field in `escapeHtml()`.

**Confidence:** High

---

### NEW-003 — XSS in showAuthSuccess via Google OAuth / Supabase

| Field | Value |
|---|---|
| **Severity** | High |
| **Type** | Security / DOM XSS |
| **File + line** | pl-dashboard-v8.html:5207–5209 |
| **Discovery** | Manual inspection |
| **Previously documented** | No |

**Code:**
```js
document.getElementById('auth-success-msg').innerHTML =
  `Welcome back, <strong>${user.name.split(' ')[0]}</strong>! &nbsp;·&nbsp; ` +
  `<span style="color:#0ecfbe">${user.plan.charAt(0).toUpperCase()+user.plan.slice(1)} license</span>`;
```
`user.name` and `user.plan` come from the Supabase `pl_licensed_users` table. A row with `name = '<img src=x onerror=alert(1)>'` would execute on every auth success.

**Recommended fix:**
```js
document.getElementById('auth-success-msg').innerHTML =
  `Welcome back, <strong>${escapeHtml(user.name.split(' ')[0])}</strong>! &nbsp;·&nbsp; ` +
  `<span style="color:#0ecfbe">${escapeHtml(user.plan.charAt(0).toUpperCase()+user.plan.slice(1))} license</span>`;
```

**Confidence:** High

---

### NEW-004 — XSS in showAccessDenied via Google OAuth email

| Field | Value |
|---|---|
| **Severity** | High |
| **Type** | Security / DOM XSS |
| **File + line** | pl-dashboard-v8.html:5188–5201 |
| **Discovery** | Manual inspection |
| **Previously documented** | No |

**Code (excerpt):**
```js
const msgs = {
  not_found: `No license was found for <strong>${email}</strong>.<br><br>...`,
  suspended: `Your license for <strong>${email}</strong> has been suspended.`,
  expired:   `Your license for <strong>${email}</strong> has expired.`
};
document.getElementById('auth-denied-msg').innerHTML = msgs[reason] || `Access denied for ${email}.`;
```
`email` from Google OAuth is embedded directly in the template literals that go into `innerHTML`. Google validates email format strictly so exploitation requires a non-standard email, but the pattern is unsafe by principle.

**Recommended fix:** Use `escapeHtml(email)` inside the template literals.

**Confidence:** Medium-High

---

### NEW-005 — XSS in auth-restore-details via Google Sheets API

| Field | Value |
|---|---|
| **Severity** | High |
| **Type** | Security / DOM XSS |
| **File + line** | pl-dashboard-v8.html:5360–5373 |
| **Discovery** | Manual inspection |
| **Previously documented** | No |

**Code (excerpt):**
```js
document.getElementById('auth-restore-details').innerHTML = `
  ...
  <div style="font-size:20px;...">${sheetInfo.rowCount.toLocaleString()}</div>
  <div style="font-size:12px;...">${dateStr}</div>
  ...
  📄 ${sheetInfo.name}
  ...`;
```
`sheetInfo.name` is the Google Sheets spreadsheet name — fully user-controlled. A spreadsheet named `<img src=x onerror=alert(document.cookie)>` would execute on any device that auto-restores.

**Recommended fix:** `escapeHtml(sheetInfo.name)`, `escapeHtml(dateStr)`.

**Confidence:** High

---

### NEW-006 — Monthly table: 6-column header, 5-column data rows

| Field | Value |
|---|---|
| **Severity** | High |
| **Type** | Data Integrity |
| **File + line** | pl-dashboard-v8.html: HTML ~line 2176, JS line 4236 |
| **Discovery** | Column count comparison |
| **Previously documented** | No (prior ISSUE-019 described a different defect) |

**Header (6 columns):**
```
Month | Revenue | Expenses | Gross Profit | Net Profit | Margin %
```

**Data row template (5 columns):**
```js
`<tr>
  <td>${m.month}</td>
  <td>${fmt(m.revenue)}</td>
  <td>${fmt(m.expenses)}</td>
  <td>${fmt(m.net)}</td>       ← shows under "Gross Profit"
  <td>${mg}%</td>              ← shows under "Net Profit"
</tr>`
```

**Result:** Net Profit value displays under "Gross Profit" header. Margin% value displays under "Net Profit" header. "Margin %" column is always empty. Total row has the same mismatch.

**Additionally:** `const cogs = ...` is computed at line 4235 but never used — dead code.

**Recommended fix:** Either add a 6th data column (actual Gross Profit = Revenue − COGS) or rename headers to match the 5-column data layout. The `cogs` variable is already available.

**Confidence:** High (verified by header/template comparison)

---

### NEW-007 — XLSX export: no formula injection protection

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Type** | Security / CSV Injection |
| **File + line** | pl-dashboard-v8.html:4720 |
| **Discovery** | Grep for csvSanitize in exportXLSX |
| **Previously documented** | No (ISSUE-008 only confirmed exportCSV fix) |

**Code:**
```js
const txData = all.map(t => ({
  Date: t.date, Type: t.type,
  Category: t.category || '',        // ← no csvSanitize
  Description: t.description || '',  // ← no csvSanitize
  Amount: t.amount, ...
}));
```
XLSX.js writes strings directly to cells. Excel and LibreOffice will execute cell values beginning with `=`, `+`, `-`, `@` as formulas.

**Recommended fix:** Apply `csvSanitize()` to Category and Description in the XLSX data map.

**Confidence:** High

---

### NEW-008 — Category `<option>` elements rendered without escaping

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Type** | Security / HTML Injection |
| **File + line** | pl-dashboard-v8.html:6040–6049 |
| **Discovery** | Python script scanning unescaped innerHTML |
| **Previously documented** | No |

**Code:**
```js
sel.innerHTML = '<option value="">— Select —</option>' +
  CATEGORIES.map(c => `<option value="${c}"...>${c}</option>`).join('');
```
`CATEGORIES` comes from localStorage. A category named `</option><option onclick="alert(1)">` would break out of the `<option>` context.

**Attack path:** User imports a CSV with a crafted category name → localStorage is poisoned → next render injects HTML.

**Recommended fix:** `escapeHtml(c)` on both the value attribute and the text content.

**Confidence:** Medium (requires localStorage manipulation — moderately difficult)

---

### NEW-009 — renderRevTable / renderExpTable: full dbGetAll() on every render

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Type** | Performance |
| **File + line** | pl-dashboard-v8.html:4180, 4205 |
| **Discovery** | Code inspection |
| **Previously documented** | No (ISSUE-010/011 covered pagination fix; this is a separate issue) |

Both `renderRevTable()` and `renderExpTable()` call `dbGetAll()` to retrieve every transaction, then filter and paginate in JavaScript. With 100k rows, each render call loads ~58 MB into memory and scans all records — even when only 50 rows are displayed.

`renderTxnTable()` correctly uses `dbQuery()` which paginates inside IndexedDB. Revenue and Expense tables do not.

**Recommended fix:** Extend `dbQuery()` to accept a `type` filter and use it in these two render functions.

**Confidence:** High

---

### NEW-010 — File name rendered unescaped in innerHTML

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Type** | Security / HTML Injection |
| **File + line** | pl-dashboard-v8.html:4688, 5743 |
| **Discovery** | unescaped innerHTML scan |
| **Previously documented** | No |

```js
// Line 4688
document.getElementById('sync-file-label').innerHTML =
  name ? `Linked file: <strong>${name}</strong>` : 'No file linked';

// Line 5743
el.innerHTML = `Previously linked: <strong>${savedFile}</strong> — click "Link File" to reconnect`;
```
`name` is a file system file name from the File System Access API. `savedFile` is a file name stored in localStorage. Both are attacker-controllable via a specially named file.

**Recommended fix:** `escapeHtml(name)` and `escapeHtml(savedFile)`.

**Confidence:** Medium

---

### NEW-011 — No role="dialog" on modals

| Field | Value |
|---|---|
| **Severity** | Low |
| **Type** | Accessibility |
| **File + line** | pl-dashboard-v8.html:2601, 2613, 2630 |
| **Discovery** | grep for role="dialog" |
| **Previously documented** | No |

Three modals (`#confirm-modal`, `#changelog-modal`, `#mapping-modal`) and the help drawer have no `role="dialog"`, no `aria-modal="true"`, and no `aria-labelledby`. Screen readers cannot identify them as dialog regions or trap focus correctly.

**Recommended fix:** Add `role="dialog" aria-modal="true" aria-labelledby="<title-id>"` to each modal container.

**Confidence:** High

---

### NEW-012 — Dead code: `cogs` variable computed but unused

| Field | Value |
|---|---|
| **Severity** | Low |
| **Type** | Code Quality |
| **File + line** | pl-dashboard-v8.html:4235 |
| **Discovery** | Code inspection |
| **Previously documented** | No |

```js
const cogs = all.filter(t=>t.type==='expense'&&(t.category||'').toLowerCase().includes('cog'))
               .reduce((s,t)=>s+t.amount,0);
```
`cogs` is computed from all transactions on every `renderMonthlyTable()` call but is never read. Likely a remnant of the planned Gross Profit column.

**Recommended fix:** Either use `cogs` to populate the missing Gross Profit column (fixing NEW-006) or remove it.

---

### CONFIRMED: ISSUE-016 — Float arithmetic drift

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Type** | Data Integrity |
| **File + line** | pl-dashboard-v8.html: KPI aggregation |
| **Previously documented** | Yes (ISSUE-016) |

Python simulation confirms: 10,000 × $0.01 = $100.00000000001425 (drift 1.43×10⁻¹¹). For real financial data this rounds away at display time (`toFixed(2)`), so it's cosmetically safe but technically incorrect. At scale (millions of transactions) drift could exceed one cent.

**Recommended fix:** Use integer arithmetic (store amounts in cents as integers) or accumulate with a compensated summation (Kahan algorithm).

---

### CONFIRMED: ISSUE-022 — DB_VERSION=1, no schema migration

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Type** | Data Safety |
| **File + line** | pl-dashboard-v8.html:2772 |
| **Previously documented** | Yes (ISSUE-022) |

`onupgradeneeded` only creates the store if it does not exist (`if (!d.objectStoreNames.contains(STORE_NAME))`). Any future schema change (new index, new field constraint) would require bumping DB_VERSION, which currently has no migration handler beyond store creation. An incomplete migration could silently lose data.

---

### CONFIRMED: ISSUE-024 — Memory footprint 58.8 MB at 100k rows

| Field | Value |
|---|---|
| **Severity** | Medium |
| **Type** | Performance |
| **Previously documented** | Yes (ISSUE-024, previously estimated 61.7 MB) |

Re-confirmed by Python simulation at 58.8 MB. Exceeds the 50 MB budget. Worsened by NEW-009: Revenue and Expense tabs each trigger a full `dbGetAll()` load on every render.

---

### CONFIRMED: ISSUE-027 — Supabase anon key hardcoded

| Field | Value |
|---|---|
| **Severity** | Info |
| **Type** | Security |
| **File + line** | pl-dashboard-v8.html:2780 |
| **Previously documented** | Yes (ISSUE-027) |

The Supabase anon key is a public JWT by design. The comment at line 2779 correctly notes RLS must be enabled. No action required beyond confirming RLS is active.

---

## Summary Table

| ID | Title | Severity | Type | New? |
|---|---|---|---|---|
| NEW-001 | XSS: showUpdateBanner (version.json) | High | Security | Yes |
| NEW-002 | XSS: openChangelog (version.json) | High | Security | Yes |
| NEW-003 | XSS: showAuthSuccess (OAuth/Supabase) | High | Security | Yes |
| NEW-004 | XSS: showAccessDenied (email) | High | Security | Yes |
| NEW-005 | XSS: auth-restore-details (Sheets) | High | Security | Yes |
| NEW-006 | Monthly table column mismatch | High | Data Integrity | Yes |
| NEW-007 | XLSX export formula injection | Medium | Security | Yes |
| NEW-008 | Category option unescaped | Medium | Security | Yes |
| NEW-009 | renderRevTable/Exp full dbGetAll | Medium | Performance | Yes |
| NEW-010 | File name unescaped in innerHTML | Medium | Security | Yes |
| NEW-011 | No role=dialog on modals | Low | Accessibility | Yes |
| NEW-012 | Dead code: cogs variable | Low | Code Quality | Yes |
| NEW-013 | settings-update-status unescaped | Low | Security | Yes |
| ISSUE-016 | Float arithmetic drift | Medium | Data Integrity | No |
| ISSUE-022 | DB_VERSION=1, no migration | Medium | Reliability | No |
| ISSUE-024 | Memory 58.8 MB @ 100k rows | Medium | Performance | No |
| ISSUE-027 | Supabase anon key hardcoded | Info | Security | No |

**Active issue count:** 17  
**New (not in prior docs):** 13  
**Carried over confirmed:** 4
