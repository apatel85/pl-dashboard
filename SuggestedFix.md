# PL Dashboard — Suggested Fix Plan

**Based on:** DetailedFindings.md independent review  
**Date:** May 14, 2026  
**Goal:** Make the app safe, usable, and production-ready  
**Total Issues to Fix:** 27 (7 Critical, 5 High, 9 Medium, 2 Low, 4 Info)

---

## How to Use This Document

Fixes are organized into 4 tiers. **Do Tier 1 first — stop there and verify before moving on.**  
Each fix includes: what the problem is in plain English, what change to make, and where in the code to find it.

---

## 🔴 TIER 1 — Critical Security Fixes (Do These First — Before Sharing with Anyone)

---

### FIX-01: Escape User Text in All Tables (Stops XSS Attacks)

**Problem (plain English):**  
When the app shows transactions on screen, it pastes raw text from your data directly into HTML. If that text contains code (like `<script>` tags), the browser runs it. This could happen from an imported CSV file.

**What to change:**  
Add a helper function called `escapeHtml()` and use it everywhere user-typed text is displayed.

**Add this function once near the top of your JavaScript:**
```javascript
function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
```

**Then change these 4 places from using raw variables to wrapped ones:**

| File Location | Change FROM | Change TO |
|---|---|---|
| Line ~2836 (renderRecentEntries) | `${t.category\|\|'—'}` | `${escapeHtml(t.category)\|\|'—'}` |
| Line ~2836 | `${t.description\|\|'—'}` | `${escapeHtml(t.description)\|\|'—'}` |
| Line ~2925 (renderRevTable) | `${t.category}` | `${escapeHtml(t.category)}` |
| Line ~2933 (renderExpTable) | `${t.category}` | `${escapeHtml(t.category)}` |

**Fixes issues:** FIND-S1, FIND-S2, FIND-S3  
**Difficulty:** Easy (30–60 mins)  
**Priority:** 🔴 Do first

---

### FIX-02: Escape CSV Preview Headers and Data (Stops Import XSS)

**Problem (plain English):**  
When you import a CSV file, the app shows a preview of the first few rows. If a CSV column header contains code, it runs during the preview — before you even confirm the import.

**What to change:**  
In the `openMappingModal` function (lines ~3034–3035), wrap column headers and cell values with `escapeHtml()`:

```javascript
// BEFORE:
document.getElementById('preview-thead').innerHTML = '<tr>' +
  csvHeaders.map(h => `<th>${h}</th>`).join('') + '</tr>';

// AFTER:
document.getElementById('preview-thead').innerHTML = '<tr>' +
  csvHeaders.map(h => `<th>${escapeHtml(h)}</th>`).join('') + '</tr>';
```

Same change for the data preview rows — wrap each `c` with `escapeHtml(c)`.

**Fixes issues:** FIND-S4  
**Difficulty:** Easy (15 mins)  
**Priority:** 🔴 Do first

---

### FIX-03: Fix the Broken Category Pill Escaping (One Word Change)

**Problem (plain English):**  
The developer wrote a `safe` variable to escape category names, but then accidentally used the original unsafe `name` variable in the HTML. It's a one-word bug.

**What to change:**  
In `catPillHTML` function (line ~4042):

```javascript
// BEFORE:
<span class="cat-name">${name}</span>

// AFTER:
<span class="cat-name">${safe}</span>
```

That's literally the entire fix — change `name` to `safe` in that one line.

**Fixes issues:** FIND-S5  
**Difficulty:** Trivial (2 mins)  
**Priority:** 🔴 Do first

---

### FIX-04: Fix Notification Toast to Use Safe Text (Not HTML)

**Problem (plain English):**  
The app's popup notifications use `innerHTML` to show messages. If the message text ever comes from an outside source (like a remote version check), it could inject code.

**What to change:**  
In the `toast()` function (line ~3783):

```javascript
// BEFORE:
el.innerHTML = `<span>${icon}</span> ${msg}`;

// AFTER:
const span = document.createElement('span');
span.textContent = icon;
el.textContent = '';
el.appendChild(span);
el.appendChild(document.createTextNode(' ' + msg));
```

Or simpler — just escape the msg:
```javascript
el.innerHTML = `<span>${icon}</span> ${escapeHtml(msg)}`;
```

**Fixes issues:** FIND-S6  
**Difficulty:** Easy (15 mins)  
**Priority:** 🔴 Do first

---

### FIX-05: Add a Content Security Policy (Browser Safety Wall)

**Problem (plain English):**  
Even if the above 4 fixes are applied, there's no browser-level protection. A Content Security Policy is like a second lock on the door — even if someone gets through the first, they can't run code.

**What to change:**  
Add this one line inside the `<head>` section of your HTML file, right after `<meta charset="UTF-8">`:

```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com;
  style-src 'self' 'unsafe-inline';
  connect-src 'self' https://*.supabase.co https://accounts.google.com https://sheets.googleapis.com;
  img-src 'self' data:;
  font-src 'self' data:;
">
```

**Note:** `unsafe-inline` is included because the app uses inline scripts. In a future version, remove `unsafe-inline` and add a nonce instead for maximum security.

**Fixes issues:** FIND-S7  
**Difficulty:** Easy (10 mins)  
**Priority:** 🔴 Do first

---

## 🟠 TIER 2 — High Priority Fixes (Do After Tier 1)

---

### FIX-06: Sanitize CSV Exports to Prevent Formula Injection

**Problem (plain English):**  
If a transaction description starts with `=`, `+`, `-`, or `@`, Excel treats it as a formula when you open the exported CSV. This is a known attack called CSV Injection.

**What to change:**  
Add this helper function:
```javascript
function csvSanitize(value) {
  const str = String(value == null ? '' : value);
  if (['+', '-', '=', '@', '\t', '\r'].some(c => str.startsWith(c))) {
    return `'${str}`;  // Prefix with apostrophe — Excel treats as text
  }
  return str;
}
```

Then in all three export locations (`exportCSV` line ~3136, `syncToFile` line ~3123, `gsheetsPush` line ~2558), wrap description and category fields:
```javascript
// BEFORE:
`"${t.description||''}"` 

// AFTER:
`"${csvSanitize(t.description||'')}"` 
```

**Fixes issues:** FIND-S8  
**Difficulty:** Easy (20 mins)  
**Priority:** 🟠 High

---

### FIX-07: Add Pagination to Revenue Table (Stops Browser Freeze)

**Problem (plain English):**  
The Revenue tab tries to display ALL rows at once. With 10,000+ transactions, this freezes the browser.

**What to change:**  
In `renderRevTable()` function (line ~2920), show only 50 rows at a time. Add a page number variable and Prev/Next buttons below the table.

**Simplified approach:**
```javascript
async function renderRevTable(page = 1) {
  const all = await dbGetAll();
  const txns = all.filter(t => t.type === 'revenue');
  const pageSize = 50;
  const start = (page - 1) * pageSize;
  const pageData = txns.slice(start, start + pageSize);
  const totalPages = Math.ceil(txns.length / pageSize);
  
  // Render only pageData rows
  // Add: "Page X of Y" + Prev / Next buttons below table
}
```

**Fixes issues:** FIND-P1 (revenue side)  
**Difficulty:** Medium (1–2 hours)  
**Priority:** 🟠 High

---

### FIX-08: Add Pagination to Expense Table (Same as FIX-07)

**Problem:** Same as FIX-07 but for the Expense tab (`renderExpTable`, line ~2928).

**What to change:** Apply the exact same pagination pattern from FIX-07 to `renderExpTable()`.

**Fixes issues:** FIND-P1 (expense side)  
**Difficulty:** Medium (30 mins after FIX-07 is done — copy same pattern)  
**Priority:** 🟠 High

---

### FIX-09: Show Error When Backup Fails (Stop Silent Data Loss)

**Problem (plain English):**  
When a backup snapshot fails because the data is too big, the app logs a warning in the developer console that users never see. They think they're backed up when they're not.

**What to change:**  
In `takeSnapshot()` function (line ~2111), find the `QuotaExceededError` catch block and add a visible toast message:

```javascript
// BEFORE:
} catch(e) {
  if (e.name === 'QuotaExceededError') {
    console.warn('Snapshot quota exceeded');
  }
}

// AFTER:
} catch(e) {
  if (e.name === 'QuotaExceededError') {
    toast('Browser backup is full — please enable Google Sheets sync to protect your data.', 'error');
  }
}
```

**Fixes issues:** FIND-D1  
**Difficulty:** Easy (10 mins)  
**Priority:** 🟠 High

---

## 🟡 TIER 3 — Medium Priority Fixes (Usability & Data Accuracy)

---

### FIX-10: Support Accounting & European Number Formats in CSV Import

**Problem (plain English):**  
Two common number formats are not supported:
- `(500.00)` — accounting format for negative numbers (QuickBooks, bank exports)
- `1.234,56` — European format meaning 1234.56

Both get silently misread or skipped.

**What to change:**  
Replace the amount parser in `applyMapping()` (line ~3069):

```javascript
function parseAmount(raw) {
  let s = String(raw).trim();
  // Accounting negative: (500.00) → -500.00
  const isNeg = s.startsWith('(') && s.endsWith(')');
  if (isNeg) s = '-' + s.slice(1, -1);
  // EU format: 1.234,56 → detect if comma is decimal
  if (/^-?[\d.]+,\d{2}$/.test(s)) {
    s = s.replace(/\./g, '').replace(',', '.');
  }
  // Standard: strip currency symbols and commas
  s = s.replace(/[$€£,\s]/g, '');
  return parseFloat(s);
}
```

**Fixes issues:** FIND-D2, FIND-D3  
**Difficulty:** Medium (1 hour + testing with real CSV samples)  
**Priority:** 🟡 Medium

---

### FIX-11: Add Date Format Selector in CSV Import Wizard

**Problem (plain English):**  
A date like `13/05/2025` (European: May 13) fails to parse in a US browser because it tries to read it as month 13, which doesn't exist. The month gets stored as "Unknown" and breaks monthly reports.

**What to change:**  
In the CSV import mapping modal, add a simple dropdown before the user clicks import:

```
Date format in your file:
  ○ MM/DD/YYYY (US — default)
  ○ DD/MM/YYYY (European)
  ○ YYYY-MM-DD (ISO)
```

Then use that selection in the date parser:
```javascript
function parseDate(str, fmt) {
  if (!str) return null;
  const parts = str.split(/[\/\-\.]/);
  if (fmt === 'DMY') return new Date(parts[2], parts[1]-1, parts[0]);
  if (fmt === 'YMD') return new Date(parts[0], parts[1]-1, parts[2]);
  return new Date(parts[2], parts[0]-1, parts[1]); // MDY default
}
```

**Fixes issues:** FIND-D4  
**Difficulty:** Medium (2–3 hours)  
**Priority:** 🟡 Medium

---

### FIX-12: Fix Monthly Table — Make Profit Column Consistent

**Problem (plain English):**  
In the Monthly P&L table, each row shows Net Profit but the TOTAL row at the bottom shows Gross Profit. They're different numbers. A business owner comparing the total to their rows will get confused.

**What to change:**  
In `renderMonthlyTable()` (line ~2945), find the total row and change it to also use Net Profit (revenue minus ALL expenses, not just COGS):

```javascript
// BEFORE (total row):
`<td>${fmt(totRev - cogs)}</td>`   // Gross profit — wrong!

// AFTER:
`<td>${fmt(totRev - totExp)}</td>` // Net profit — consistent with row data
```

**Fixes issues:** FIND-D5  
**Difficulty:** Easy (10 mins)  
**Priority:** 🟡 Medium

---

### FIX-13: Fix Rounding Display for Dollar Amounts

**Problem (plain English):**  
Due to how computers handle decimal math, adding many small amounts can produce results like `$99.99999999999986` instead of `$100.00`. It's cosmetically wrong and confusing.

**What to change:**  
Add a display formatter that rounds to 2 decimal places everywhere money is shown:

```javascript
// Already have fmt() function — update it to:
function fmt(n) {
  return '$' + (Math.round((n || 0) * 100) / 100).toFixed(2);
}
```

**Fixes issues:** FIND-D6  
**Difficulty:** Easy (20 mins)  
**Priority:** 🟡 Medium

---

### FIX-14: Fix CSV Quote Handling (RFC 4180)

**Problem (plain English):**  
In standard CSV files, a quote inside a field is written as `""` (two quotes). The app currently reads `""` as nothing (drops the quotes entirely). So `He said ""hello""` becomes `He said hello`.

**What to change:**  
In the `parseCSV()` function (line ~3019), update the quote-toggle logic:

```javascript
// BEFORE (toggle logic):
if (ch === '"') { q = !q; continue; }

// AFTER (RFC 4180 lookahead):
if (ch === '"') {
  if (q && i + 1 < line.length && line[i + 1] === '"') {
    cur += '"'; i++; // escaped quote — add literal " and skip next
  } else {
    q = !q; // open/close quote
  }
  continue;
}
```

**Fixes issues:** FIND-D7  
**Difficulty:** Medium (1 hour + test with RFC 4180 edge cases)  
**Priority:** 🟡 Medium

---

### FIX-15: Show Error Toast When Inline Edit Fails

**Problem (plain English):**  
When you edit a transaction directly in a table cell and it fails to save (e.g., storage full), there's no warning. The user doesn't know their edit was lost.

**What to change:**  
In `inlineEdit()` function (line ~2911):

```javascript
// BEFORE:
putReq.onerror = ev => console.warn('inlineEdit put error', ev.target.error);

// AFTER:
putReq.onerror = ev => {
  console.warn('inlineEdit put error', ev.target.error);
  toast('Could not save your edit — please try again or refresh the page.', 'error');
};
```

**Fixes issues:** FIND-U5  
**Difficulty:** Trivial (5 mins)  
**Priority:** 🟡 Medium

---

### FIX-16: Use Double-Confirm for "Clear All Data"

**Problem (plain English):**  
Clicking "Clear All Data" only shows ONE confirmation dialog. One accidental click and all your data is permanently deleted. The app already has a `showDoubleConfirm()` function built in — it's just not being used here.

**What to change:**  
In `confirmClearData()` function (line ~3208):

```javascript
// BEFORE:
showConfirm('Clear ALL Data?', '...', async () => { await dbClear(); ... });

// AFTER:
showDoubleConfirm(
  'Clear ALL Data?',
  'This cannot be undone. Are you absolutely sure?',
  async () => { await dbClear(); ... }
);
```

**Fixes issues:** FIND-U6  
**Difficulty:** Trivial (2 mins)  
**Priority:** 🟡 Medium

---

### FIX-17: Show User-Friendly Error When Browser Blocks Storage (Private Mode)

**Problem (plain English):**  
If someone opens the app in Incognito/Private Browsing mode, the browser blocks IndexedDB (the local database). The app currently shows a blank screen or a cryptic error.

**What to change:**  
In the `openDB()` error handler (line ~2008):

```javascript
req.onerror = (e) => {
  document.body.innerHTML = `
    <div style="padding:40px;font-family:sans-serif;text-align:center">
      <h2>Storage Not Available</h2>
      <p>This app requires browser storage, which is blocked in Private/Incognito mode.</p>
      <p><strong>Please reopen this page in a normal browser window.</strong></p>
    </div>`;
  reject(e.target.error);
};
```

**Fixes issues:** FIND-U7  
**Difficulty:** Easy (20 mins)  
**Priority:** 🟡 Medium

---

## 🔵 TIER 4 — Usability Improvements (Makes the App Better to Use)

---

### FIX-18: Add a Welcome / Onboarding Screen

**Problem:** New users see a blank app with no guidance.

**What to build:**  
On the very first visit (check with `localStorage.getItem('onboarded')`), show a modal with 3 simple steps:
1. ➕ Add your first transaction OR import a CSV
2. 📊 See your P&L on the Dashboard tab
3. 💾 Connect Google Sheets in the Backup tab to keep your data safe

Add a "Got it, let's go!" button that sets `localStorage.setItem('onboarded', '1')` and closes the modal.

**Fixes issues:** FIND-U1  
**Difficulty:** Medium (2–3 hours)  
**Priority:** 🔵 Low (but high user impact)

---

### FIX-19: Rename Backup Layers to Plain English

**Problem:** "Layer 1 / 2 / 3" means nothing to a business owner.

**What to change (just rename the labels in the UI):**

| Old Label | New Label |
|---|---|
| Layer 1 Backup | Quick Save (Browser) |
| Layer 2 Backup | Save to My Computer |
| Layer 3 Backup | Sync to Google Drive |
| Snapshot Now | Save Now |

No logic change — just text changes in the HTML.

**Fixes issues:** FIND-U3  
**Difficulty:** Easy (30 mins)  
**Priority:** 🔵 Low

---

### FIX-20: Add Accessibility Labels (ARIA)

**Problem:** Screen readers can't read toast notifications or icon-only buttons.

**Two changes:**

1. Add ARIA to toast container (line ~378):
```html
<!-- BEFORE: -->
<div id="toast">

<!-- AFTER: -->
<div id="toast" role="status" aria-live="polite" aria-atomic="true">
```

2. Add aria-label to icon buttons:
```html
<!-- BEFORE: -->
<button onclick="deleteTxn(t.id)">✕</button>

<!-- AFTER: -->
<button onclick="deleteTxn(t.id)" aria-label="Delete transaction">✕</button>
```

**Fixes issues:** FIND-A1, FIND-A2  
**Difficulty:** Easy (30 mins)  
**Priority:** 🔵 Low

---

### FIX-21: Add In-App Help Button

**Problem:** All help documentation lives outside the app on GitHub.

**What to build:**  
Add a small "?" button in the top-right corner that opens a slide-in panel with:
- Quick Start (3 steps)
- Common questions (How do I back up? How do I import? What if I lose data?)
- Link to the full USER_README.md for advanced help

**Fixes issues:** FIND-U4  
**Difficulty:** Medium (3–4 hours)  
**Priority:** 🔵 Low (but high user impact)

---

### FIX-22: Add PWA Install Prompt Inside the App

**Problem:** Users miss the tiny browser address bar install icon and never install the PWA.

**What to build:**  
Listen for the `beforeinstallprompt` browser event and show a visible banner at the top of the app:

```
📱 Install this app on your device for the best experience  [Install Now] [Later]
```

```javascript
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  // Show install banner with button
  document.getElementById('install-banner').style.display = 'block';
  document.getElementById('install-btn').onclick = () => e.prompt();
});
```

**Fixes issues:** FIND-U7  
**Difficulty:** Easy (1 hour)  
**Priority:** 🔵 Low

---

## Recommended Fix Order (Week-by-Week Plan)

| Week | What to Do | Why |
|---|---|---|
| Week 1 | FIX-01 through FIX-05 (all Tier 1 security) | App is a security risk right now — fix this before anything else |
| Week 2 | FIX-06 through FIX-09 (Tier 2 high priority) | Prevent browser freeze, stop silent backup failures |
| Week 3 | FIX-10, FIX-11, FIX-12, FIX-13 (data accuracy) | Fix import issues and number display |
| Week 4 | FIX-14, FIX-15, FIX-16, FIX-17 (UX fixes) | Small fixes that prevent data loss and confusion |
| Week 5+ | FIX-18 through FIX-22 (polish) | Onboarding, better labels, accessibility, install prompt |

---

## Quick Wins (< 30 Minutes Each)

These are super fast to do and have high impact — great place to start:

- ✅ **FIX-03** — Change one word (`name` → `safe`) to fix category XSS
- ✅ **FIX-16** — Change one function call to enable double-confirm on Clear All Data
- ✅ **FIX-15** — Add 2 lines to show an error when inline edit fails
- ✅ **FIX-12** — Fix one line in the monthly table total row
- ✅ **FIX-20** — Add ARIA labels for accessibility (text changes only)
- ✅ **FIX-19** — Rename Layer 1/2/3 to plain English (text changes only)

---

*This fix plan was created as part of an independent end-user and technical review. For the full list of issues and their technical details, see `DetailedFindings.md` and the original `ISSUES_LOG.md`.*
