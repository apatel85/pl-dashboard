# P&L Dashboard

A single-file, zero-backend Profit & Loss tracker for small businesses.

`pl-dashboard-v8.html` is **one self-contained file** (~1.3 MB) that works in
two ways:

| Use case | How |
|---|---|
| **Online** | Open `https://apatel85.github.io/pl-dashboard/pl-dashboard-v8.html` in any modern browser. Bookmark and use. |
| **Offline** | Download the same file from the repo (click **Raw** → save as) and double-click to open. No internet needed. |

Chart.js and XLSX.js are inlined into the file, so it loads instantly and works
without any CDN or external libraries.

All financial data is stored locally in the browser's IndexedDB. Nothing is sent
to a server unless the user explicitly enables Google Sheets sync (Layer 3 backup).

---

## Google Sheets sync — important nuance

The **button is available in both online and offline modes.** Whether the OAuth
authentication completes depends on how the page was opened:

| Origin | Google Sheets sync |
|---|---|
| `https://apatel85.github.io/...` (online) | ✅ Works fully |
| `https://apatel85.github.io/...` (revisited offline, browser cache) | ✅ Works for already-authenticated sessions |
| `file:///.../pl-dashboard-v8.html` (downloaded file) | ⚠️ Blocked by Google — see below |

### Why `file://` blocks OAuth

Google requires OAuth client IDs to whitelist `http://` or `https://` origins.
`file://` URLs cannot be added to **Authorized JavaScript origins** in Google
Cloud Console — Google's policy explicitly rejects them.

### How users get Sheets sync to work everywhere

There are two clean paths:

**Path 1 (recommended) — Always use the GitHub Pages URL.** Even when offline,
your browser caches the page. As long as the user visits the online URL at least
once, modern browsers (Chrome, Edge, Firefox) keep it available via cache. The
origin stays `https://apatel85.github.io`, so OAuth works the same online or
offline.

**Path 2 — Run a tiny local server.** If a user wants the file fully offline AND
Sheets sync, they can:

```bash
cd /folder/with/pl-dashboard-v8.html
python3 -m http.server 8000
# then open http://localhost:8000/pl-dashboard-v8.html
```

For this to work, you (the app owner) add `http://localhost:8000` (and any other
ports you support) to **Authorized JavaScript origins** in Google Cloud Console.

For most users, **Path 1 is the right answer.** Tell them: "Bookmark the online
URL. It works offline once you've visited it."

---

## For end users (suggested wording)

> Visit https://apatel85.github.io/pl-dashboard/pl-dashboard-v8.html in Chrome,
> Edge, or Brave. Bookmark it. The page works offline after your first visit —
> your data stays on your device and never leaves your browser. To save a copy
> of your data, use the **Backup** tab: click **Snapshot Now** for quick saves,
> **Link Local File** for auto-save to a file on your disk, or **Connect Google
> Sheets** for cloud sync.

---

## Feature matrix

| Feature | Online URL | Offline `file://` | Offline (via localhost) |
|---|---|---|---|
| Manual transaction entry | ✅ | ✅ | ✅ |
| CSV / Excel import | ✅ | ✅ | ✅ |
| KPI dashboard with charts | ✅ | ✅ | ✅ |
| Revenue / Expense / Monthly tables | ✅ | ✅ | ✅ |
| Categories | ✅ | ✅ | ✅ |
| CSV / Excel / JSON export | ✅ | ✅ | ✅ |
| Layer 1 backup (localStorage) | ✅ | ✅ | ✅ |
| Layer 2 backup (linked local file) | ✅ Chrome/Edge | ✅ Chrome/Edge | ✅ Chrome/Edge |
| Layer 3 backup (Google Sheets) | ✅ | ❌ (Google blocks `file://`) | ✅ (if origin whitelisted) |
| Supabase license check | ✅ | ✅ | ✅ |

Best browsers: **Chrome**, **Edge**, **Brave**. Firefox works but disables
IndexedDB in private mode. Safari has limited File System Access API support.

---

## Deployment (already done in this repo)

- ✅ Self-contained `pl-dashboard-v8.html` committed at repo root
- ✅ GitHub Pages enabled (see Step 2 in the PR summary)
- ✅ Google OAuth `Authorized JavaScript origins` includes
  `https://apatel85.github.io` (see Step 3 in the PR summary)
- ✅ Supabase RLS protects the `pl_licensed_users` table

### Updating the deployed app

1. Edit `pl-dashboard-v8.html` directly.
   - The file contains inlined Chart.js 4.4.1 and XLSX.js 0.18.5. To upgrade
     either library, replace the inlined block (look for the comment
     `/* Chart.js 4.4.1 (inlined for offline use) */` and the matching XLSX
     comment). Source libraries are available from `npm pack chart.js@<ver>`
     and `npm pack xlsx@<ver>`.
2. Bump `version.json`.
3. Commit and push:
   ```bash
   git add pl-dashboard-v8.html version.json
   git commit -m "feat: ..."
   git push
   ```
4. GitHub Pages will redeploy within 1–2 minutes.

---

## Scale: 1,000–10,000 users

GitHub Pages does **not** crash. It serves static files from a global CDN with
generous bandwidth (~100 GB/month soft limit). At ~1.3 MB per page load, that's
roughly 75,000 page loads/month before approaching limits.

The real cost driver is **Supabase** (license check, RLS-protected reads):

| Users | Supabase free tier | Action |
|---|---|---|
| < 10,000 active | ✅ Free tier (50k MAU, 500 MB DB, 2 GB egress) covers it | Nothing |
| 10k–50k | ✅ Still free tier | Monitor usage on Supabase dashboard |
| > 50k | Upgrade to Pro plan (~$25/mo) | Pay-as-you-grow |

IndexedDB is per-device, so it scales for free.

---

## Security posture

| Patch | Status | Resolves |
|---|---|---|
| FIX-001/002/003/012 — XSS escaping | ✅ Applied | Critical XSS via category/description/CSV import |
| FIX-004 — Content Security Policy | ✅ Applied | Defence-in-depth against script injection |
| FIX-005 — CSV formula injection | ✅ Applied | Prevents Excel formula execution in exports |
| FIX-006 — Library inlining | ✅ Applied | Eliminates CDN tampering risk entirely (libs inlined, not fetched) |
| FIX-007/008 — Table pagination | ✅ Applied | No browser freeze on large datasets |
| FIX-009/016 — Visible error messages | ✅ Applied | No more silent failures |
| FIX-010/011/013/014 — Parsing fixes | ✅ Applied | Accounting/EU number formats, RFC 4180 CSV |
| FIX-015 — Monthly totals correction | ✅ Applied | Per-row and total-row use consistent Net Profit |
| FIX-017 — Double-confirm destructive | ✅ Applied | Two prompts before "Clear All Data" |
| FIX-018 — IndexedDB error UI | ✅ Applied | Friendly error page instead of blank screen |
| FIX-019/020 — Accessibility ARIA | ✅ Applied | Screen reader announcements |

See `review/ISSUES_LOG.md`, `review/FIXES.md`, and `review/SCORECARD.md` for the full audit. Current grade: **B+ (82/100)**, up from F (59/100) at the audit baseline.

---

## Recent feature highlights (2026-05-14 → 2026-05-19)

Beyond the security/reliability fixes, the v8.1.0–v8.3.0 releases and the in-progress mobile UX branch added:

- **Landing page + first-run flow** — friendly landing page before the auth gate; sample-data mode loads 6 months of demo transactions for first-time exploration.
- **Industry templates** — one-click setup for Consulting / E-commerce / SaaS / Restaurant / Generic, each with tailored revenue + expense categories.
- **Auto-categorize from history** — typing a description suggests the matching category from prior transactions.
- **Light/dark mode** — system-aware theme toggle persisted per device.
- **Mobile UX overhaul** — mobile-optimized topbar, custom category dropdown that stays open on scroll, card-mode transaction tables, tap-to-edit cards, 44px tap targets, iOS safe-area support.
- **Undo deletes** — 6-second Undo toast replaces confirm dialogs (Linear / Gmail pattern); also covers bulk delete.
- **Instant search** on Revenue and Expense tabs with 150ms debounce.
- **Web Worker CSV import** — files over 500 KB parse on a background thread; UI stays responsive.
- **Automatic duplicate detection** on import.
- **Optimistic Google Drive sync indicator** — top-bar status shows Syncing / Synced / Sync failed.
- **Keyboard shortcuts** (`?` to view all), **PWA shortcuts** and **Share Target API** for CSV/XLSX.
- **In-app Help drawer** with Quick Start and 7 FAQs; smart PWA install banner shown only after 3+ transactions.
- **Plain-English backup labels** — Quick Save / Save to My Computer / Sync to Google Drive.
- **Loading-sequence fix** — landing-vs-bootApp session-shape race resolved; Google popup no longer flashes for unauthenticated visitors.
- **Save-and-sign-out** — explicit safe sign-out that flushes pending writes.

See `CHANGELOG.md` for the full release history.

---

## Repository contents

| File | Role |
|---|---|
| `pl-dashboard-v8.html` | **The app** — single self-contained file (online + offline) |
| `index.html` | Mirror of `pl-dashboard-v8.html` so the clean `/` URL serves the app directly |
| `service-worker.js` | PWA service worker (pre-caches both URLs for offline) |
| `manifest.json` | PWA manifest |
| `version.json` | Machine-readable version + release notes |
| `CHANGELOG.md` | Human-readable release notes (Keep-a-Changelog format) |
| `README.md` | This file |
| `review/` | Audit documents (live, with Status columns). See `review/README.md`. |
| `review/REVIEW_PLAN.md` | The AI-driven review plan (Parts A–H) |
| `review/AI_REVIEW_PROMPT.md` | One-shot prompt to re-run the review with any AI |
| `review/ISSUES_LOG.md` | All 30 issues with Status (21 resolved, 2 open, 7 info-only) |
| `review/FIXES.md` | 20 auto-applyable patches — all applied |
| `review/SCORECARD.md` | Health scorecard (current B+ + original F baseline) |
| `docs/` | End-user docs + plain-English audit. See `docs/README.md`. |
| `docs/USER_README.md` | End-user guide |
| `docs/DetailedFindings.md` | Plain-English audit findings with Status markers |
| `docs/SuggestedFix.md` | Tiered remediation plan — all fixes shipped |
| `archive/` | Historical snapshots of v5/v6/v7 dashboards. See `archive/README.md`. |
| `mock-data/` | 7 generated CSV datasets used for testing |
| `tests/e2e.spec.js` | Playwright stub for browser-only features |
| `tests/sim.py` | Python simulation harness used during the review |

---

## Data privacy

- The app stores all financial data only in your browser's IndexedDB on your
  own device.
- No data is transmitted to any server unless you explicitly enable Google
  Sheets sync — and even then, only to your own Google Sheet.
- The Supabase license check transmits only your email/license key, never
  transaction data.
