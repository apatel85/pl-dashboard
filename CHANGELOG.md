# Changelog

All notable changes to the P&L Dashboard are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project loosely follows semantic versioning. Machine-readable release metadata lives in [`version.json`](./version.json).

## [Unreleased] — branch `claude/enhance-dashboard-mobile-ux-nv4hi`

### Added
- **Landing page** before the auth gate so first-time visitors see a friendly intro instead of a sign-in dialog.
- **Light/dark mode** toggle, system-aware and persisted per device.
- **Tap-to-edit mobile transaction cards** — Revenue/Expense tables switch to card mode on phones with a single tap to edit any field.
- **Custom category dropdown** that stays open while scrolling on mobile and clips correctly inside the topbar.

### Fixed
- **Loading sequence race**: the landing-vs-`bootApp()` session-shape mismatch that briefly flashed the Google sign-in popup for unauthenticated visitors.
- **Mobile table overlap** on the topbar and page-action rows.
- **Category dropdown scroll** no longer closes the menu prematurely on touch devices.
- **Re-applied audit XSS patches** that had regressed during the mobile refactor.

### Changed
- **Save-and-sign-out** flow flushes pending writes before clearing the session.
- Monthly P&L column layout tightened; redundant subtitles dropped.

## [8.3.0] — 2026-05-14
**Industry Templates, Smart Categories, Keyboard Shortcuts & Bulk Actions**

### Added
- One-click **industry templates** (Consulting / E-commerce / SaaS / Restaurant / Generic) that merge with existing categories without overwriting data.
- **Auto-categorize from history** — typing a description suggests the matching category from prior transactions, with a one-tap "Use this" button.
- **Keyboard shortcuts**: `?` for cheat sheet, `n` new transaction, `/` focus search, `g+d/r/e/b/s/i/t/m` jump to views, `Esc` close dialogs.
- **Bulk actions** on Revenue/Expense — checkbox per row + select-all-on-page, floating action bar, bulk delete with the same 6-second Undo.
- **PWA shortcuts** (long-press app icon) for Add Transaction / Import CSV / Dashboard.
- **Share Target API** — "Share to P&L Dashboard" appears in the phone share sheet for CSV/XLSX.
- **Clear Sample Data** button shown on the Dashboard whenever demo transactions are loaded.

## [8.2.0] — 2026-05-14
**Power Features — Undo, Search, Duplicates, Workers & Optimistic Sync**

### Added
- **Undo deletes** — 6-second Undo toast (Linear / Gmail pattern) replaces confirm dialogs.
- **Instant inline search** on Revenue and Expense tabs (descriptions, categories, amounts, dates, months) with 150 ms debounce.
- **Pagination Prev/Next** controls visible on Revenue and Expense tables.
- **Web Worker CSV import** — files over 500 KB parse on a background thread; UI stays responsive with a live progress bar.
- **Automatic duplicate detection** on CSV import — flags rows matching existing transactions on date + amount + description + type.
- **Optimistic Google Drive sync indicator** — top-bar shows Syncing / Synced / Sync failed.

### Changed
- CSP updated to allow `blob:` workers while keeping all other lock-downs intact.

## [8.1.0] — 2026-05-14
**CX Polish — Help, Install Prompt, Plain-Language Backup & Empty States**

### Added
- **CSV import format selectors** — date (Auto / US / European / ISO) and number (Auto / US 1,234.56 / EU 1.234,56).
- **Empty states** on Dashboard, Revenue, and Expense with three CTAs (Add Transaction / Import CSV / Try Sample Data).
- **Sample Data mode** — one click loads 6 months of realistic demo transactions.
- **In-app Help drawer** — `?` button opens Quick Start steps and 7 FAQs.
- **Smart PWA install banner** — shown only after 3+ transactions (engaged users accept at ~25% vs ~3% on first load).

### Changed
- Backup tab labels renamed from "Layer 1/2/3" to **Quick Save**, **Save to My Computer**, **Sync to Google Drive**.
- Canonical URL meta tag added; manifest `start_url` updated to `/`.

## [8.0.4] — 2026-05-14
**License Key Sign-In + Blank-Page Hardening**

### Added
- Alternative sign-in with **email + license key**; no Google account needed.

### Fixed
- Blank-page root cause: malformed cached session no longer throws in `unlockApp()` after the auth gate hides — defensive field handling restores the auth gate on any error.
- `bootApp()` wrapped in try/catch so any boot crash clears the cached session and brings back the auth gate.

## [8.0.3] — 2026-05-14
**Direct Index + CSP Fix for Google OAuth**

### Fixed
- Blank page at clean URL — `index.html` now contains the full dashboard directly (no redirect dance).
- CSP `frame-src 'none'` was blocking Google OAuth iframes — relaxed to allow `accounts.google.com`.

### Changed
- CSP allows Google profile images and `oauth2.googleapis.com`.
- Service worker pre-caches both `index.html` and `pl-dashboard-v8.html`.

## [8.0.2] — 2026-05-14
**Always-Latest Loader + One-Click Update**

### Added
- Clean URL `https://apatel85.github.io/pl-dashboard/` auto-redirects to the newest build with cache-busting.
- Update banner now has a **Reload Now** button that clears caches and forces the latest build.

### Changed
- Cache-Control headers force browsers to revalidate the HTML on every visit.
- Service worker bumped — old caches auto-purge on next load.

## [8.0.1] — 2026-05-14
**Mobile Layout Overhaul**

### Fixed
- Charts now stack vertically on mobile (class-name typo).
- Mapping modal field grid no longer overlaps on phones.

### Changed
- All buttons and inputs meet 44 px tap-target minimum.
- 16 px input font on mobile prevents iOS auto-zoom on focus.
- iOS safe-area insets respected; modals slide up from the bottom on mobile.
- Backup tier rows, snapshot list rows, and Sheets connect card all stack properly on small screens.
- Toast pinned to bottom-center on mobile, above the iOS home indicator.

## [8.0.0] — 2026-05-13
**Security, Performance & Offline Hardening — audit-driven baseline**

This is the release that resolved all 20 audit fixes from `review/FIXES.md`. The audit grade moved from **F (59/100)** to **B+ (82/100)** with this release plus the polish releases above.

### Added
- **Single self-contained HTML** — Chart.js + XLSX.js inlined, no CDN dependency; works fully offline from a downloaded file.
- **Content-Security-Policy** meta tag (FIX-004).
- **Date format selector** in the CSV mapping modal (FIX-011).
- **Double-confirmation** for Clear All Data (FIX-017).
- **IndexedDB unavailable** user-facing error screen (FIX-018).

### Fixed
- **XSS hardening** across all user-controlled fields — descriptions, categories, CSV import, toast messages (FIX-001/002/003/012).
- **CSV export formula injection** — leading-quote prefix for `= + - @` cells (FIX-005).
- **Amount parser** handles accounting-negative `(99.00)` and EU `1.234,56` formats (FIX-010).
- **CSV parser** correctly handles RFC 4180 escaped quotes and strips BOM (FIX-014).
- **Monthly P&L total row** uses consistent Net Profit math (FIX-015).
- **Float drift** suppressed in displayed totals (FIX-013).

### Changed
- **Revenue and Expense tables** paginate at 50 rows/page — instant render at 100k+ transactions (FIX-007/008).
- **Snapshot quota errors** surface a clear toast instead of failing silently (FIX-009).
- **Toast notifications** announce to screen readers via ARIA live region (FIX-019); icon buttons get ARIA labels (FIX-020).

## [5.0.0] — 2025-05-12
**3-Layer Backup + Google Sheets Cloud Sync**

### Added
- Layer 1 auto browser snapshots (last 5 states, one-click restore).
- Layer 2 auto file backup every 30 min (Chrome/Edge/Brave).
- Layer 3 Google Sheets live sync (push/pull from any device).
- Protection score banner, in-app Google sign-in guide, persistent-storage request, storage health dashboard.

## [4.0.0] — 2025-04-01
**IndexedDB Engine + File Sync**

### Added
- IndexedDB storage for 100k+ transactions with proper indexing.
- Quick-Add form with Enter-key rapid entry.
- Inline editing of all transaction fields.
- Paginated transactions table with sort, search, multi-filter.
- File System Access API sync to a CSV or XLSX on disk.
- Excel export with Transactions + Monthly Summary sheets.

## [1.0.0] — 2025-01-01
**Initial Release**

### Added
- CSV upload with intelligent field mapping.
- Revenue & expense tracking with category breakdown.
- 4 interactive charts (bar, line, donut).
- Auto-save between sessions.
- CSV and JSON export.
