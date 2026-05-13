# P&L Dashboard

A single-file, zero-backend Profit & Loss tracker for small businesses.
Built with vanilla JavaScript, Chart.js, XLSX.js, IndexedDB, optional Google Sheets
sync, and a 3-layer backup system (localStorage snapshots, File System Access API,
Google Sheets).

Two builds are shipped:

| File | Use case | Internet required |
|---|---|---|
| `pl-dashboard-v8.html` | **Online** — hosted on GitHub Pages or any web host | Yes (loads Chart.js + XLSX.js from CDN) |
| `pl-dashboard-v8-offline.html` | **Offline / local file** — download once, run forever | No (Chart.js + XLSX.js are inlined) |

Both builds store all financial data locally in the browser's IndexedDB. Nothing is
sent to a server unless the user explicitly enables Google Sheets sync.

---

## Quick start (end users)

### Option A — Use it online (recommended for sharing)

Visit `https://apatel85.github.io/pl-dashboard/` in Chrome, Edge, Brave, or Firefox.
Bookmark it. Your data stays on your device.

### Option B — Use it offline (recommended for privacy / no-internet)

1. Download [`pl-dashboard-v8-offline.html`](pl-dashboard-v8-offline.html) from the
   GitHub repo (click **Raw** → save as).
2. Double-click the file. It opens in your default browser.
3. That's it. Bookmark the local file and you're done.

**Best browsers for offline use:** Chrome, Edge, or Brave. Firefox works but its
private-window mode disables IndexedDB. Safari has limitations with File System
Access API.

---

## Feature support: online vs offline

| Feature | Online (GitHub Pages) | Offline (`file://`) |
|---|---|---|
| Manual transaction entry | ✅ | ✅ |
| CSV/Excel import | ✅ | ✅ |
| KPI dashboard with charts | ✅ | ✅ |
| Revenue / Expense / Monthly tables | ✅ | ✅ |
| Categories | ✅ | ✅ |
| CSV / Excel / JSON export | ✅ | ✅ |
| Layer 1 backup (localStorage snapshots) | ✅ | ✅ |
| Layer 2 backup (linked local file) | ✅ (Chrome/Edge) | ✅ (Chrome/Edge) |
| Layer 3 backup (Google Sheets sync) | ✅ | ⚠️ Requires extra Google OAuth setup (see below) |
| Supabase license check | ✅ | ✅ |

---

## Deploying online (GitHub Pages)

The repository already includes `pl-dashboard-v8.html`. To make it accessible to
others via the web:

1. Push the latest changes to the `main` branch.
2. On GitHub, go to **Settings → Pages**.
3. Under **Build and deployment → Source**, select **Deploy from a branch**.
4. Branch: `main`. Folder: `/ (root)`. Click **Save**.
5. Wait 1–2 minutes. GitHub will publish the site at:
   `https://apatel85.github.io/pl-dashboard/pl-dashboard-v8.html`
6. For a cleaner URL, copy the contents of `pl-dashboard-v8.html` into
   `index.html` (or rename it) so visitors can use
   `https://apatel85.github.io/pl-dashboard/` directly.

### Google OAuth setup (required for Google Sheets sync on the online build)

If you want the **Sheets sync** feature to work for your users:

1. Open https://console.cloud.google.com/apis/credentials.
2. Find the OAuth 2.0 Client ID listed in `pl-dashboard-v8.html`
   (`319401977574-ldicfj8e93m040t42vnjboq7mmmo00ro.apps.googleusercontent.com`).
3. Under **Authorized JavaScript origins**, add:
   - `https://apatel85.github.io`
4. Save. Changes take effect within ~5 minutes.

### Supabase Row Level Security (required for license check)

The Supabase anon key is embedded in the JavaScript source — that's normal and
expected for client-side apps. Anyone can read it, so security depends on Row
Level Security (RLS) policies:

1. Open https://supabase.com/dashboard → your project → **Authentication → Policies**.
2. On the `pl_licensed_users` table, confirm RLS is **enabled**.
3. Confirm policies only allow `SELECT` and only when `auth.uid()` (or your
   licensing logic) authorizes it. Never allow anonymous `INSERT`/`UPDATE`/`DELETE`.

---

## Deploying offline (download & use locally)

### Building a fresh offline file

Run this once after every change to `pl-dashboard-v8.html`:

```bash
python3 build-offline.py
```

This:
- Downloads Chart.js 4.4.1 and XLSX.js 0.18.5 from the npm registry (cached in `vendor/`).
- Inlines both into the HTML.
- Strips the Google Fonts CDN reference (falls back to system fonts).
- Tightens the Content-Security-Policy (no longer needs `cdnjs.cloudflare.com`).
- Writes `pl-dashboard-v8-offline.html` (~1.3 MB).

Distribute that single file. Users open it directly — no install, no server.

### Telling users to use it offline (suggested wording)

> Download `pl-dashboard-v8-offline.html` and save it anywhere on your computer.
> Double-click the file to open it in your browser. Your data stays on your device
> and is never sent anywhere. To back up your data, use the **Backup** tab inside
> the app — click **Snapshot Now** or **Link Local File** to auto-save to a file
> on your disk.

### Google OAuth setup (only if you want Sheets sync offline)

OAuth flows do not natively support `file://` URLs. Recommendation: offline users
should use **Layer 2** (local file backup via File System Access API) instead of
Sheets sync — it works perfectly from `file://` in Chrome and Edge, and is
actually faster and more private.

---

## Scale: can GitHub host this for many users?

**Yes, easily — even for 1,000–10,000 users.**

- GitHub Pages serves static files via a fast global CDN. Bandwidth limits are
  generous (100 GB / month soft limit). At ~600 KB per page load, that's
  ~170,000 page loads / month before approaching the limit.
- The CDN handles Chart.js and XLSX.js, taking that load off GitHub entirely.
- The real bottleneck is **Supabase** (license check):
  - Free tier: 50,000 monthly active users, 500 MB DB, 2 GB egress — fine for
    most cases.
  - If you exceed the free tier, Supabase scales linearly with paid plans.
- IndexedDB is per-user/per-device — no shared state, so it has zero scaling cost.

**Bottom line:** at 10,000 users, GitHub Pages won't crash. Watch Supabase
quotas; everything else is essentially free.

---

## Security posture (post-fixes)

Patches applied in this release (see `FIXES.md`, `ISSUES_LOG.md`,
`SCORECARD.md` for the full audit):

| Area | Status |
|---|---|
| XSS via category/description fields | ✅ Patched (FIX-001, 002, 003, 012) |
| Content Security Policy | ✅ Added (FIX-004) |
| CSV formula injection on export | ✅ Patched (FIX-005) |
| Subresource Integrity for CDN scripts | ✅ Added in online build (FIX-006) |
| Performance: 100k-row table render | ✅ Paginated (FIX-007, 008) |
| Silent storage failures | ✅ Surfaced to user (FIX-009, 016) |
| Number/date parsing edge cases | ✅ Handled (FIX-010, 011, 013, 014) |
| Monthly totals math | ✅ Corrected (FIX-015) |
| Destructive-action guards | ✅ Double-confirm (FIX-017) |
| IndexedDB unavailable error | ✅ User-facing message (FIX-018) |
| Accessibility (toast ARIA, button labels) | ✅ Added (FIX-019, 020) |

---

## Development

| File | Role |
|---|---|
| `pl-dashboard-v8.html` | Source of truth — edit this file |
| `pl-dashboard-v8-offline.html` | Generated by `build-offline.py` — do NOT edit by hand |
| `build-offline.py` | Build script — regenerates the offline HTML |
| `vendor/` | Cached CDN libraries (Chart.js, XLSX.js) |
| `version.json` | Version metadata |
| `REVIEW_PLAN.md` | The AI-driven review plan (Parts A–H) |
| `AI_REVIEW_PROMPT.md` | One-shot prompt for ChatGPT/Gemini/Claude to re-run the review |
| `ISSUES_LOG.md` | All 27 issues found by the review |
| `FIXES.md` | 20 auto-applyable patches |
| `SCORECARD.md` | Health scorecard and performance numbers |
| `mock-data/` | 7 generated CSV datasets (10 → 100k rows) used for testing |
| `tests/e2e.spec.js` | Playwright stub for browser-only features |
| `tests/sim.py` | Python simulation harness used during the review |

### Workflow after editing the HTML

```bash
# 1. Edit pl-dashboard-v8.html
# 2. Regenerate the offline build
python3 build-offline.py
# 3. Bump version.json
# 4. Commit both files
git add pl-dashboard-v8.html pl-dashboard-v8-offline.html version.json
git commit -m "feat: ..."
git push
```

---

## Data privacy

- The app stores all financial data **only** in your browser's IndexedDB.
- No data is transmitted to any server unless you explicitly enable Google
  Sheets sync (Layer 3 backup) — and even then, only to your own Sheet.
- The Supabase license check transmits only your email/license key — never
  transaction data.
