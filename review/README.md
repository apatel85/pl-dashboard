# review/

Audit documents from the **2026-05-13 security/quality review** of `pl-dashboard-v8.html`.

All Tier 1–3 fixes (FIX-001 through FIX-020) have been applied to the live file. Each document in this folder now carries Status columns / markers showing what is resolved and what intentionally remains open.

Files here are kept **live (not archived)** because they remain the source of truth for the issue → fix traceability matrix.

| File | What it is |
|---|---|
| `REVIEW_PLAN.md` | The original review plan (Parts A–H) that drove the audit |
| `AI_REVIEW_PROMPT.md` | One-shot prompt for re-running the review with any AI |
| `ISSUES_LOG.md` | All 30 issues, now with a **Status** column (21 Resolved, 2 Open, 7 Info — no action) |
| `FIXES.md` | 20 auto-applyable patches, each marked **Status: ✅ APPLIED** |
| `SCORECARD.md` | Current State section (B+ / 82) at the top, Original Audit (F / 59) preserved below |

For plain-English versions of the audit, see `docs/DetailedFindings.md` and `docs/SuggestedFix.md`. For release-level history, see `CHANGELOG.md`.
