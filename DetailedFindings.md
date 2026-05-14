# PL Dashboard — Detailed Findings Report

**Review Date:** May 14, 2026  
**Reviewed By:** Independent AI Review (Perplexity / Claude)  
**App URL:** https://apatel85.github.io/pl-dashboard/  
**Version Reviewed:** v8 (pl-dashboard-v8.html, 4,190 lines)  
**Overall Grade:** F (7 Critical Issues)  
**Overall Health Score:** 59 / 100

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

## Section 1 — Usability Findings (End User Perspective)

### FIND-U1: No Welcome Screen or Onboarding
- **What happens:** First-time users land on a blank screen with no guidance on what to do.
- **Why it matters:** Apps like Wave, QuickBooks, or Zoho show a setup wizard. Without it, new users get confused and leave.
- **Impact:** High — directly causes user drop-off.

### FIND-U2: Confusing URL Structure
- **What happens:** The working app URL is `/pl-dashboard-v8.html` — a version number in the URL that changes over time. The root `/` redirects to a different page.
- **Why it matters:** Users bookmark `/v8.html`, then a new version drops and their bookmark breaks.
- **Impact:** Medium — causes confusion and support requests.

### FIND-U3: "Layer 1 / 2 / 3 Backup" Terminology
- **What happens:** The Backup tab uses developer language like "Layer 1", "Layer 2", "Layer 3".
- **Why it matters:** A small business owner doesn't know what "Layer 2 backup" means.
- **Impact:** Medium — users skip backup setup and lose data.

### FIND-U4: No In-App Help or Tooltips
- **What happens:** All instructions live in a separate `USER_README.md` file outside the app. There is no "?" help button inside the app.
- **Why it matters:** Users won't find documentation unless they know to look for it on GitHub.
- **Impact:** Medium — causes repeated support questions.

### FIND-U5: No Visual Feedback on Failed Inline Edits
- **What happens:** If you edit a transaction directly in a table and it fails (e.g., storage is full), there is NO error message — it just quietly fails.
- **Why it matters:** User thinks their edit was saved but it wasn't. Data loss.
- **Impact:** High — silent data loss with no warning.

### FIND-U6: "Clear All Data" Only Asks Once
- **What happens:** Clicking "Clear All Data" shows one confirmation popup. If you click OK accidentally, everything is gone.
- **Why it matters:** This is a destructive, irreversible action that should ask TWICE. The code even has a `showDoubleConfirm` function built in but it's not being used here.
- **Impact:** High — accidental permanent data loss.

### FIND-U7: No Install Prompt Inside the App
- **What happens:** To install the app as a PWA, users have to find the tiny browser address bar install icon. There's no visible button or prompt inside the app itself.
- **Why it matters:** Most users won't notice the address bar icon. Installing as a PWA is the recommended way to use this app safely.
- **Impact:** Medium — most users will run it as a tab, which is less reliable.

---

## Section 2 — Security Findings (Critical)

> ⚠️ These must be fixed before sharing this app with anyone.

### FIND-S1: XSS in Transaction Display (renderRecentEntries)
- **What happens:** If you import a CSV file that has `<script>alert(1)</script>` in the Description or Category column, that code actually RUNS in your browser when you view the Dashboard tab.
- **Real Risk:** A malicious CSV file (sent to you by email, or downloaded from a bad source) could steal ALL your financial data stored in the browser.
- **Location:** Line 2834–2841 in the HTML file.
- **Severity:** 🔴 Critical

### FIND-S2: XSS in Revenue Table (renderRevTable)
- **Same problem** as FIND-S1 but on the Revenue tab.
- **Location:** Line 2925.
- **Severity:** 🔴 Critical

### FIND-S3: XSS in Expense Table (renderExpTable)
- **Same problem** as FIND-S1 but on the Expense tab.
- **Location:** Line 2933.
- **Severity:** 🔴 Critical

### FIND-S4: XSS in CSV Import Preview (openMappingModal)
- **What happens:** When you upload a CSV to import, the app shows a preview. If the CSV column headers or data contain `<script>` tags, they execute BEFORE you even finish importing.
- **Location:** Lines 3034–3035.
- **Severity:** 🔴 Critical

### FIND-S5: XSS in Category Pills (catPillHTML)
- **What happens:** If you create a category with a name like `<img src=x onerror=alert(1)>`, it executes as code on screen.
- **Note:** The code even has a variable called `safe` that was supposed to escape this, but the developer accidentally used the raw `name` variable instead. The fix is literally one word change.
- **Location:** Line 4039–4047.
- **Severity:** 🔴 Critical

### FIND-S6: XSS in Notification Toasts (toast function)
- **What happens:** The popup notification function (`toast()`) uses `innerHTML` instead of `textContent`. Any message that contains HTML (including from remote version check responses) could inject code.
- **Location:** Line 3783.
- **Severity:** 🔴 Critical (previously classified High, upgraded due to remote data path)

### FIND-S7: No Content Security Policy (CSP)
- **What happens:** There is no browser-level safety wall. Even if some XSS fixes are applied, without a CSP, any injected script still runs freely.
- **Why it matters:** A CSP would block ALL the above attacks as a safety net, even before code-level fixes.
- **Location:** `<head>` section of HTML.
- **Severity:** 🔴 Critical

### FIND-S8: CSV Export Formula Injection
- **What happens:** If a transaction description starts with `=`, `+`, `-`, or `@` (e.g., `=SUM(A1:A10)`), the exported CSV file carries that formula. When someone opens that CSV in Excel or Google Sheets, Excel EXECUTES the formula.
- **Real Risk:** An attacker could craft a formula that runs commands on the user's computer via Excel macros.
- **Location:** Lines 3136, 3123, 2558.
- **Severity:** 🟠 High

### FIND-S9: No Integrity Check on External Libraries
- **What happens:** The app loads Chart.js and XLSX.js from a public CDN. If that CDN is hacked or intercepted, a fake version of these libraries could be served to users with malicious code.
- **Location:** `<head>` script tags.
- **Severity:** 🟠 High

---

## Section 3 — Data & Functional Findings

### FIND-D1: Silent Backup Failure for Large Datasets
- **What happens:** With 10,000+ transactions, each backup snapshot is ~1.4MB. Five snapshots = ~7MB, but the browser only allows 5MB. When it fails, the app just logs a warning in the developer console — the user sees nothing and thinks their backup worked.
- **Impact:** 🔴 High — user has NO backup without knowing it.

### FIND-D2: Accounting Number Format Not Supported
- **What happens:** Bank exports and QuickBooks often use formats like `(500.00)` for negative numbers. The app can't parse this and silently skips those rows.
- **Impact:** 🟡 Medium — imported data is incomplete without warning.

### FIND-D3: European Number Format Causes Wrong Amounts
- **What happens:** European number format `1.234,56` (meaning one thousand two hundred thirty-four dollars and fifty-six cents) gets misread as `1.23456` (just over a dollar). The wrong amount gets saved.
- **Impact:** 🟡 Medium — financial data is silently corrupted.

### FIND-D4: Date Format Confusion (DD/MM vs MM/DD)
- **What happens:** A date like `13/05/2025` (May 13th in European format) fails to parse correctly in US browsers. The month gets stored as "Unknown" and monthly groupings break.
- **Impact:** 🟡 Medium — monthly P&L reports show wrong data.

### FIND-D5: Monthly Table Shows Inconsistent Profit Numbers
- **What happens:** In the Monthly P&L table, each month row shows "Net Profit" in column 4, but the TOTAL row at the bottom shows "Gross Profit" instead. These are different numbers — it's misleading.
- **Impact:** 🟡 Medium — confusing financial reporting.

### FIND-D6: Small Rounding Errors in Totals
- **What happens:** Due to how computers handle decimal math (IEEE 754 floating point), adding thousands of transactions can produce results like `$100.000000000014` instead of `$100.00`.
- **Impact:** 🟡 Medium — visible with large data sets; misleading to users.

### FIND-D7: CSV Quotes Not Handled Correctly (RFC 4180)
- **What happens:** A CSV field like `He said ""hello""` (standard way to escape quotes in CSV) is imported as `He said hello` — the quotes are dropped.
- **Impact:** 🟡 Medium — description text gets silently mangled.

---

## Section 4 — Performance Findings

### FIND-P1: Revenue and Expense Tables Freeze Browser with Large Data
- **What happens:** The Revenue and Expense tabs try to render ALL rows at once. With 100,000 rows, this creates 100,000 DOM elements in the browser at the same time, causing it to freeze completely.
- **Impact:** 🔴 High — app becomes unusable for power users.

### FIND-P2: Memory Usage Too High for Large Datasets
- **What happens:** Loading 100,000 transactions uses ~61.7 MB of browser memory. The target budget is 50 MB. On low-end devices, this causes slowdowns or crashes.
- **Impact:** 🟡 Medium.

---

## Section 5 — Accessibility Findings

### FIND-A1: Notifications Not Read Aloud by Screen Readers
- **What happens:** The popup notification bar (toast) has no accessibility role. Screen readers don't announce it, so visually impaired users miss important messages.
- **Impact:** 🟡 Low-Medium.

### FIND-A2: Icon Buttons Have No Labels
- **What happens:** Buttons that only show emoji (✕ delete, ⬇ download) have no text description. A screen reader just says "button" with no context.
- **Impact:** 🟡 Low-Medium.

---

## Section 6 — Comparison to Leading Apps in This Space

| Feature | PL Dashboard | Wave | QuickBooks | Zoho Books |
|---|---|---|---|---|
| Onboarding Wizard | ❌ None | ✅ Yes | ✅ Yes | ✅ Yes |
| Offline Support | ✅ Full | ❌ Online only | ❌ Online only | ❌ Online only |
| Data Privacy (local storage) | ✅ Best-in-class | ❌ Server-stored | ❌ Server-stored | ❌ Server-stored |
| Security (XSS protection) | ❌ Not applied yet | ✅ Enterprise-grade | ✅ Enterprise-grade | ✅ Enterprise-grade |
| Mobile App | ⚠️ PWA only | ✅ Native app | ✅ Native app | ✅ Native app |
| Multi-currency | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Invoice generation | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| Price | Free | Free | $30–$200/mo | $15–$240/mo |
| No account needed | ✅ Yes | ❌ Requires signup | ❌ Requires signup | ❌ Requires signup |

**Bottom line:** PL Dashboard wins on privacy, cost, and offline use. It loses on security (currently), onboarding, and ecosystem features.

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

---

*This report was generated as part of an independent end-user and technical review of the PL Dashboard v8. See `SuggestedFix.md` for the step-by-step remediation plan.*
