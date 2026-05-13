# AI Review Prompt — P&L Dashboard v8

Use this prompt when working with **ChatGPT**, **Gemini**, **Claude**, or any other AI tool.
Paste the prompt below (between the triple-dashes) into the AI chat AFTER uploading both files.

---

## Files to upload before pasting this prompt
1. `pl-dashboard-v8.html` — the application under review (4,190 lines)
2. `REVIEW_PLAN.md` — the review and testing plan you will follow

---

## Prompt to paste

```
I have uploaded two files:
- `pl-dashboard-v8.html`: a single-file, zero-backend P&L (Profit & Loss) financial dashboard built with vanilla JavaScript, Chart.js, XLSX.js, IndexedDB, localStorage, File System Access API, and Google Sheets API.
- `REVIEW_PLAN.md`: a structured review and testing plan that tells you exactly what to check, how to log issues, and how to fix them.

Your job is to act as a senior software engineer and perform the **Part A — Static Code Review** from REVIEW_PLAN.md against the uploaded `pl-dashboard-v8.html` file.

---

### INSTRUCTIONS

**Step 1 — Read REVIEW_PLAN.md first.**
Understand the structure:
- Part A = Static code review (you do this entirely from the file — no browser needed)
- Part B = Manual UI testing (a human must run this in Chrome — skip for now unless I tell you otherwise)
- Part C = Issue logging format (use this exact format for every finding)
- Part D = Resolution Playbook (recipes for fixing each issue type)
- Part E = AI-specific notes for your tool
- Part F = Verification and sign-off checklist

**Step 2 — Run Section A1: Inventory Pass.**
From `pl-dashboard-v8.html`:
1. Report the total line count, and where `<style>` and `<script>` blocks begin/end.
2. List every JavaScript function: name, approximate line number, approximate LOC. Flag any function exceeding 80 lines.
3. List all global variables and state objects (look for `let`/`var` at top scope).
4. List all storage keys (strings assigned to `const` like `CATEGORIES_KEY`, `GSHEETS_KEY`, IndexedDB store names).

**Step 3 — Run Section A2: Security Review.**
Search the file for each of these patterns and report findings:
- A2.1: Every `innerHTML =` or template-literal HTML string that interpolates user-supplied data (category names, descriptions, filenames). Flag any that are NOT HTML-escaped.
- A2.2: Count inline `onclick="..."` handlers. Flag any where the handler string is dynamically built from user data.
- A2.3: Search for `eval(`, `new Function(`, `setTimeout("`. Report every hit — there should be zero.
- A2.4: Find the Google OAuth `client_id`. Confirm it looks like a public web client ID (ends in `.apps.googleusercontent.com`). Note the OAuth scopes requested.
- A2.5: Search for where tokens or credentials are written to `localStorage`. Note the key names and whether TTL/expiry is enforced.
- A2.6: Find the CSV/XLSX export function(s). Check whether cell values that begin with `=`, `+`, `-`, or `@` are sanitized (prefixed with a `'` or tab) before being written to the output.

**Step 4 — Run Section A3: Data Integrity Review.**
Check:
- A3.1: Find `onupgradeneeded`. Does it use `oldVersion` branching to avoid dropping the existing store on upgrades from prior versions?
- A3.2: Find `dbBulkPut` (or the equivalent bulk-insert function). Is it wrapped in a single IndexedDB transaction with error rollback?
- A3.3: Find all `parseFloat` / `Number(` calls on user amount inputs. Do they strip `$`, `,`, and handle `(99.00)` accounting-negative format?
- A3.4: Find the date-parsing logic for CSV import. Does it handle `YYYY-MM-DD`, `MM/DD/YYYY`, and `DD/MM/YYYY` without ambiguity, or does it silently pick one?
- A3.5: Are monetary amounts stored as floats or integers (cents)? If floats, flag floating-point precision risk.
- A3.6: Find the Layer 1 snapshot logic. Confirm the rolling buffer is capped at 5 and evicts the oldest without corrupting the array.
- A3.7: Find the Google Sheets pull function. Does it show a confirmation prompt before overwriting local data?

**Step 5 — Run Section A4: Code Quality.**
- A4.1: List all functions over 80 LOC (from your Step 2 inventory) and note what they do.
- A4.2: Identify duplicate rendering logic (e.g., multiple functions that rebuild the same dropdown or table).
- A4.3: List all magic strings (hardcoded repeated string literals that should be named constants).
- A4.4: Find every `fetch(`, `FileReader`, and IndexedDB request. Does each have a `.catch()` or `try/catch` that calls a toast/alert on failure?
- A4.5: Check for ARIA labels on icon-only buttons, `role="status"` on the toast container, and `:focus-visible` CSS rules.
- A4.6: Find the transaction table render function. Does it paginate or virtualize before rendering? What is the max rows rendered at once?

**Step 6 — Run Section A5: Browser Compatibility.**
- A5.1: Is `window.showOpenFilePicker` (File System Access API) guarded by a feature-detection check? What happens on Firefox/Safari where it's unsupported?
- A5.2: Is there a fallback or error message when IndexedDB is unavailable (e.g., private browsing mode)?
- A5.3: List any ES2020+ syntax used (`?.`, `??`, `Promise.allSettled`, etc.) and confirm the app doesn't claim support for IE or old browsers.

---

### OUTPUT FORMAT

For every finding, output a structured issue entry using this exact format (from REVIEW_PLAN.md Part C):

```
## ISSUE-<NNN>: <Short title>
- **Section:** A2.1
- **Severity:** Critical | High | Medium | Low | Info
- **Type:** Security | Data-loss | Functional | UX | Performance | Accessibility | Code-quality
- **Location:** pl-dashboard-v8.html:<line> (function `<name>`)
- **Steps to reproduce:** (for static issues, describe what to search for)
- **Expected:** …
- **Actual:** …
- **Evidence:** paste the relevant code snippet (≤10 lines)
- **Suggested fix:** see Resolution R-<id> from REVIEW_PLAN.md
```

Number issues sequentially starting at ISSUE-001.

After all issues, output:
1. A **summary table** with columns: Issue #, Section, Severity, Type, Short title.
2. A count of Critical / High / Medium / Low / Info issues found.

---

### SCOPE FOR THIS SESSION

- Do **Part A only** (static analysis from the uploaded file).
- Do **not** attempt to run or simulate the HTML.
- Do **not** modify the file.
- Do **not** attempt Part B (that requires a human with a browser).
- If you cannot access a section of the file due to length limits, say so explicitly and I will paste the relevant section.

---

### AFTER PART A IS COMPLETE

Tell me when you are done with Part A. I will then:
1. Manually run Part B (browser testing) and paste my findings back to you.
2. Ask you to log those findings as additional ISSUE-NNN entries.
3. Ask you to produce resolution patches (from Part D of REVIEW_PLAN.md) for any Critical or High severity issues.
```

---

## Notes for specific AI tools

### ChatGPT (GPT-4o / o1)
- Upload both files using the paperclip/attachment button before pasting the prompt.
- If the file is too long for one context window, paste it in chunks of ~200KB and say "This is chunk 1 of N — do not start analysis until I say GO."
- Use **Code Interpreter** (Advanced Data Analysis) for reliable `grep`-style searching.
- For fixes: ask for **unified diffs** (`--- before / +++ after`) rather than full file rewrites.

### Gemini (2.x in AI Studio or Gemini app)
- Use Google AI Studio (aistudio.google.com) for the 1M token context window — paste the full file content.
- Alternatively, use the Files API if using the Gemini API directly.
- Gemini handles long files well in one pass; you can ask it to complete all of Part A in a single response.
- For fixes: ask for inline diffs with line numbers.

### Claude (claude.ai or Claude Code)
- In Claude Code: files are already on disk. Use `Read` with `offset`/`limit` for windowed reading.
- In claude.ai: upload both files via the attachment button.
- Claude handles structured output reliably — the ISSUE-NNN format will be followed consistently.
- After Part A, Claude Code can apply fixes directly to the file using the `Edit` tool.

### Any tool — common guardrails
- Always **snapshot your data** (open the app → Backup tab → Snapshot Now) before applying any code fix.
- Apply fixes **one issue at a time** and re-test the relevant Part B section before moving on.
- Never let the AI commit or push changes without your explicit approval.
