# AI Review Prompt — P&L Dashboard v8 (v2: full AI-driven testing)

Use this prompt with **ChatGPT (Code Interpreter)**, **Gemini (AI Studio)**, or **Claude (Code or claude.ai)**.
It instructs the AI to perform the entire review, simulation, stress testing, and fix-generation **autonomously** — no human-in-browser required.

---

## Files to upload before pasting the prompt
1. `pl-dashboard-v8.html` — the application under review (4,190 lines)
2. `REVIEW_PLAN.md` — the full plan (the AI follows this end-to-end)

That's it. The AI will generate every other artifact (mock data, issue log, fixes, scorecard).

---

## Prompt to paste

```
You are a senior software engineer + QA automation engineer.

I have uploaded:
- `pl-dashboard-v8.html`: a 4,190-line single-file P&L dashboard (vanilla JS, Chart.js, XLSX.js, IndexedDB, localStorage, File System Access API, Google Sheets API).
- `REVIEW_PLAN.md`: the complete plan you will execute.

Follow REVIEW_PLAN.md end-to-end. You are responsible for ALL testing — including stress testing — using your code-execution sandbox (Python in Code Interpreter / Gemini code execution / Node via Bash for Claude). Do not ask a human to run a browser; instead, extract pure-logic JS functions from the file and re-execute them on mock datasets you generate.

---

### EXECUTE IN THIS ORDER

**Step 1 — Read REVIEW_PLAN.md fully.** Confirm you understand Parts A through H.

**Step 2 — Generate mock datasets (Part C).**
Write Python code that emits these CSV files (use the C7 generator pseudocode as a starting point):
- `mock-10-rev2500-exp1000.csv` (smoke)
- `mock-1000-rev500000-exp300000.csv` (standard)
- `mock-10000-rev1000000-exp500000.csv` (stress)
- `mock-100000-rev10000000-exp5000000.csv` (heavy stress)
- `mock-edge-cases.csv` (all 20 edge cases listed in C4)
- `mock-10000-pennies.csv` (10,000 × $0.01 — float-drift torture)
- `mock-100k-mixed.csv` (24 months × 20 categories)

Each filename's totals must match the actual CSV totals exactly.

**Step 3 — Part A: Static Review.**
Run every check in Sections A1 through A5 against `pl-dashboard-v8.html`. Use regex / `re.findall` on the file's text. Log every finding as an `ISSUE-NNN` entry per Part E's format.

**Step 4 — Part B: Logic Simulation.**
- Extract each pure-logic JS function from the HTML (parseDate, parseAmount, csv parser/sanitizer, KPI calculator, monthly aggregator, htmlEscape, etc.).
- Transliterate each to Python (or run via PyMiniRacer / Node if available). Preserve semantics exactly.
- Run the unit-test matrix in B2 against every extracted function. Log every failure as `ISSUE-NNN`.
- Run the end-to-end integration simulation (B3) on all 7 mock datasets. Log any deviation between computed totals and filename-encoded totals.
- For browser-only features (B4), produce a Playwright stub `tests/e2e.spec.js` covering UI rendering, IndexedDB transactions, File System Access, and Google OAuth flows. Note these as "Confidence: Low" in the scorecard.

**Step 5 — Part D: Stress & Performance.**
For each of D1–D7:
- Time operations with `time.perf_counter()`.
- Record actual values vs budget.
- Flag every breach as an `ISSUE-NNN` (Severity = High if budget missed by ≥ 2×, Medium otherwise).
- Compute Layer 1 snapshot size (D7); if a full 100k dataset stringifies > 1 MB, flag with recommendation for LZ-string compression.

**Step 6 — Produce ISSUES_LOG.md** (Part E format).
Number every finding sequentially (ISSUE-001, ISSUE-002, …) across static + simulation + stress. Every entry must include: section, severity, type, location with line numbers, evidence snippet, and linked FIX-NNN.

**Step 7 — Produce FIXES.md** (Part F format — STRICT).
For every ISSUE-NNN, produce a corresponding FIX-NNN block with:
- `OLD_STRING`: the exact code currently in the file (with enough surrounding lines that it appears exactly once).
- `NEW_STRING`: the exact replacement (preserving indentation byte-for-byte).
- Rationale and verification steps.

This format is designed so a downstream AI tool (ChatGPT, Gemini, or Claude Code) can be given `pl-dashboard-v8.html` + `FIXES.md` and instructed:
> "Apply every FIX-NNN: find OLD_STRING in the file and replace with NEW_STRING. Report any not found."

Constraints:
- Each patch ≤ 50 lines.
- Order patches top-to-bottom by file location so earlier patches don't invalidate later OLD_STRINGs.
- Group new helper functions (e.g., `escapeHtml`) at a stable anchor (after the last top-level `const`).
- Every FIX-NNN links back to its ISSUE-NNN.

**Step 8 — Produce SCORECARD.md** (Part G format).
Include: overall grade (A/B/C/D/F per formula), 7 category scores, issue counts by severity, performance numbers vs budgets, top-5 risks, remediation order, confidence table, recommended next steps.

**Step 9 — Cover note (≤ 200 words).**
Summarize the single most-impactful finding and the one fix to apply first.

---

### DELIVERABLES (output as separate code blocks or downloadable files)

1. `mock-data/*.csv` — all 7 datasets
2. `ISSUES_LOG.md`
3. `FIXES.md` (strict format from Part F — must be auto-applyable)
4. `SCORECARD.md`
5. `tests/e2e.spec.js` — Playwright stub
6. Cover note

If any deliverable would exceed your output limit, split it into Part 1 / Part 2 / … and tell me how many parts to expect.

---

### CONSTRAINTS

- Do NOT ask the human to run anything in a browser. All testing is yours.
- Do NOT modify `pl-dashboard-v8.html` — only describe fixes in `FIXES.md`.
- Do NOT skip stress tests because they're slow — run on 100k rows. If your sandbox runs out of memory, stream the data row-by-row and report the throughput you achieved.
- Be honest about confidence: any browser-only feature gets "Confidence: Low" with reasoning.
- Cite line numbers from `pl-dashboard-v8.html` in every issue.

Begin now with Step 1, then proceed in order. Output Step 2's generator code first so I can see the mock data being created.
```

---

## Tool-Specific Setup

### ChatGPT (4o / o1 with Code Interpreter)
- Click the paperclip → attach both files.
- Paste the prompt above.
- ChatGPT will use Python in its sandbox to generate mocks, run extracted-function simulations, and time stress tests.
- If output is truncated, ask: "Continue from where you stopped, in the same format."

### Gemini (2.x in Google AI Studio)
- Open https://aistudio.google.com → new chat → enable "Code execution".
- Upload both files (paperclip icon).
- Paste the prompt.
- Gemini 2.0+ can execute Python natively; for older versions, ask it to print code blocks you'll run locally.

### Claude (claude.ai or Claude Code)
- claude.ai: attach both files via paperclip.
- Claude Code: files already on disk — say "Execute REVIEW_PLAN.md end-to-end" and Claude will use Read, Bash (`python3` / `node`), and Write tools to produce all artifacts directly into the repo.
- The `FIXES.md` format is designed to feed Claude Code's `Edit` tool one-to-one — after producing it, Claude Code can apply every patch with no human intervention.

---

## Applying the fixes (downstream step)

Once you have `FIXES.md`:

**With Claude Code:** "Apply every FIX-NNN in FIXES.md to pl-dashboard-v8.html using the Edit tool. Report any OLD_STRING not found."

**With ChatGPT / Gemini:** Upload `pl-dashboard-v8.html` + `FIXES.md` to a fresh chat and paste:
> "For every FIX-NNN block in FIXES.md: find OLD_STRING in pl-dashboard-v8.html and replace it with NEW_STRING. Each OLD_STRING is unique in the file. After all fixes are applied, output the patched HTML as a downloadable file. List any FIX-NNN that could not be applied and why."

---

## Guardrails

- Snapshot live data first: open the running app → Backup tab → "Snapshot Now" → confirm at least one Layer-1 snapshot exists before applying fixes.
- Apply fixes in severity order: Critical → High → Medium → Low → Info.
- Re-run Part B simulation after each tier to confirm no regression.
- Never commit / push without explicit approval.
