# Universal App Blueprint
**Source:** Patterns proven in pl-dashboard-v8.3.0  
**Purpose:** A domain-agnostic component library. Give this document to an AI or developer with a description of your new app's data and goals. They implement using these proven patterns — zero rewrites, zero guessing.

---

## HOW TO USE THIS DOCUMENT

**You are building a new app.** This document contains 16 proven UI components and a complete foundation. Each component is domain-agnostic — the code patterns work for any kind of data (tasks, inventory, contacts, bookings, expenses, logs, etc.).

**Step 1 — Define your app** using the Domain Adapter (Part 3).  
**Step 2 — Select components** from the Feature Selection Matrix.  
**Step 3 — Implement Foundation first** (always, no exceptions).  
**Step 4 — Add components one at a time**, following each checklist.  
**Step 5 — Run the Audit Plan** before shipping.

> **The P&L Dashboard** is referenced throughout as a working example. It uses every component in this document. Its source file (`pl-dashboard-v8.html`) is the verified reference implementation.

---

## FEATURE SELECTION MATRIX

| ID | Component | What It Does (Plain English) | Requires |
|----|-----------|------------------------------|----------|
| F0 | **Foundation** | Browser storage, settings, theme, security utilities, app shell | — always include |
| C01 | **Navigation Layout** | Sidebar on desktop, bottom bar on mobile, view-switching system | F0 |
| C02 | **KPI Summary Cards** | Row of metric boxes showing computed totals from your data | F0 |
| C03 | **Charts** | Bar, line, and pie/doughnut charts auto-built from your records | F0 |
| C04 | **Filterable Paginated Table** | Sortable, searchable, paginated table for any record type | F0 |
| C05 | **Quick-Entry Form** | Fast single-record add form with autocomplete field | F0 |
| C06 | **Bulk Select + Delete + Undo** | Checkboxes on table rows, delete many at once, 6-second undo | F0, C04 |
| C07 | **CSV / Excel Import** | Upload any spreadsheet, map columns to your fields, bulk import | F0 |
| C08 | **Tag / Label Management** | Create, rename, delete labels used to categorize records | F0 |
| C09 | **Three-Layer Backup** | Auto-snapshots in browser + local file + Google Sheets cloud | F0 |
| C10 | **Settings Panel** | App name, any scalar config values, data summary, sample data | F0 |
| C11 | **Toast Notifications + Undo** | Dismissable pop-ups with optional Undo action | F0 |
| C12 | **Auth Gate** | License key or Google sign-in screen (optional — skip if public app) | F0 |
| C13 | **Theme Toggle** | Dark / light mode switch, remembered across sessions | F0 |
| C14 | **Keyboard Shortcuts** | Key bindings for navigation and common actions | F0, C01 |
| C15 | **PWA / Offline Support** | Works without internet, installable on phone or desktop | F0 |
| C16 | **Data Export** | Download all records as CSV, Excel, or JSON | F0 |

---

## PART 1 — FOUNDATION (F0)
### Always Required. Every other component depends on this.

---

### 1A. App Shell HTML

The entire app lives in a single HTML file. No build step. No bundler. All CSS and JS are inline.

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">

  <!-- SECURITY: Content Security Policy — adjust CDN domains as needed -->
  <meta http-equiv="Content-Security-Policy"
    content="default-src 'self';
             script-src 'self' 'unsafe-inline' https://accounts.google.com;
             style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
             font-src 'self' https://fonts.gstatic.com;
             connect-src 'self' https://*.supabase.co https://sheets.googleapis.com https://www.googleapis.com;">

  <title>YOUR_APP_NAME</title>
  <link rel="manifest" href="manifest.json">

  <style>
    /* === THEME VARIABLES — customize colors here === */
    :root, :root[data-theme="dark"] {
      --bg:           #0f1117;
      --surface:      #181c27;
      --surface2:     #1f2435;
      --border:       #2a3045;
      --border-strong:#3a4260;
      --primary:      #0ecfbe;   /* main accent — change to your brand color */
      --warning:      #f5a623;
      --danger:       #e74c3c;
      --success:      #27ae60;
      --info:         #3b82f6;
      --text:         #e8eaf0;
      --muted:        #6b7394;
      --shadow:       0 4px 24px rgba(0,0,0,.45);
      --radius:       10px;
      --focus:        #6ea8ff;
    }
    :root[data-theme="light"] {
      --bg:           #f5f6fa;
      --surface:      #ffffff;
      --surface2:     #f0f2f8;
      --border:       #d4d8e8;
      --border-strong:#b0b8d0;
      --primary:      #0aab9e;
      --warning:      #d97706;
      --danger:       #dc2626;
      --success:      #16a34a;
      --info:         #2563eb;
      --text:         #1a1f35;
      --muted:        #6b7394;
      --shadow:       0 2px 12px rgba(0,0,0,.12);
      --radius:       10px;
      --focus:        #2563eb;
    }

    /* === RESET + BASE === */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'DM Sans', system-ui, sans-serif; background: var(--bg); color: var(--text);
           font-size: 15px; line-height: 1.5; }
    button { cursor: pointer; font-family: inherit; }
    input, select, textarea { font-family: inherit; font-size: 15px; }

    /* === LAYOUT === */
    #topbar { height: 58px; background: var(--surface); border-bottom: 1px solid var(--border);
              display: flex; align-items: center; justify-content: space-between;
              padding: 0 20px; position: sticky; top: 0; z-index: 100; }
    #app    { display: flex; height: calc(100vh - 58px); overflow: hidden; }
    #sidebar { width: 220px; flex-shrink: 0; background: var(--surface);
               border-right: 1px solid var(--border); overflow-y: auto; padding: 16px 0; }
    #main   { flex: 1; overflow-y: auto; padding: 28px 32px; }

    /* === NAVIGATION === */
    .nav-label { font-size: 11px; font-weight: 600; text-transform: uppercase;
                 letter-spacing: .08em; color: var(--muted); padding: 16px 16px 6px; }
    .nav-item  { display: flex; align-items: center; gap: 10px; padding: 9px 16px;
                 color: var(--muted); text-decoration: none; cursor: pointer;
                 border-radius: 6px; margin: 1px 8px; font-size: 14px; transition: all .15s; }
    .nav-item:hover  { background: var(--surface2); color: var(--text); }
    .nav-item.active { background: rgba(14,207,190,.12); color: var(--primary); font-weight: 600; }

    /* === VIEWS === */
    .view { display: none; }
    .view.active { display: block; }

    /* === CARDS === */
    .card { background: var(--surface); border: 1px solid var(--border);
            border-radius: var(--radius); padding: 20px; }

    /* === BUTTONS === */
    .btn         { padding: 8px 18px; border-radius: 7px; border: none; font-size: 14px;
                   font-weight: 500; transition: opacity .15s; }
    .btn:hover   { opacity: .85; }
    .btn-primary { background: var(--primary); color: #000; }
    .btn-outline { background: transparent; border: 1px solid var(--border); color: var(--text); }
    .btn-danger  { background: var(--danger); color: #fff; }
    .btn-ghost   { background: transparent; color: var(--muted); }

    /* === FORMS === */
    .form-input  { width: 100%; padding: 9px 12px; background: var(--surface2);
                   border: 1px solid var(--border); border-radius: 7px; color: var(--text); }
    .form-input:focus { outline: 2px solid var(--focus); border-color: transparent; }
    .form-label  { font-size: 13px; color: var(--muted); margin-bottom: 5px; display: block; }

    /* === TABLES === */
    .table-wrap  { overflow-x: auto; }
    table        { width: 100%; border-collapse: collapse; font-size: 14px; }
    th           { text-align: left; padding: 10px 12px; background: var(--surface2);
                   color: var(--muted); font-weight: 600; font-size: 12px;
                   text-transform: uppercase; letter-spacing: .04em; border-bottom: 1px solid var(--border); }
    td           { padding: 11px 12px; border-bottom: 1px solid var(--border); }
    tr:last-child td { border-bottom: none; }
    tr:hover td  { background: var(--surface2); }
    th.sortable  { cursor: pointer; user-select: none; }
    th.sortable:hover { color: var(--text); }

    /* === BADGES === */
    .badge       { display: inline-block; padding: 2px 10px; border-radius: 20px;
                   font-size: 12px; font-weight: 500; }
    .badge-primary { background: rgba(14,207,190,.15); color: var(--primary); }
    .badge-danger  { background: rgba(231,76,60,.15);  color: var(--danger); }
    .badge-warning { background: rgba(245,166,35,.15); color: var(--warning); }

    /* === PAGINATION === */
    .pagination  { display: flex; align-items: center; gap: 4px; padding: 14px 0; flex-wrap: wrap; }
    .pagination button { padding: 5px 10px; border-radius: 5px; border: 1px solid var(--border);
                         background: var(--surface2); color: var(--text); font-size: 13px; }
    .pagination button.active { background: var(--primary); color: #000; border-color: var(--primary); }
    .pagination button:disabled { opacity: .4; cursor: not-allowed; }
    .pg-info     { font-size: 13px; color: var(--muted); margin-right: 8px; }

    /* === MOBILE === */
    #bottombar   { display: none; }
    @media (max-width: 640px) {
      #sidebar   { display: none; }
      #main      { padding: 16px; }
      #bottombar { display: flex; position: fixed; bottom: 0; left: 0; right: 0;
                   background: var(--surface); border-top: 1px solid var(--border);
                   z-index: 100; }
      #bottombar button { flex: 1; padding: 10px 0; background: none; border: none;
                          color: var(--muted); font-size: 11px; display: flex;
                          flex-direction: column; align-items: center; gap: 2px; }
      #bottombar button.active { color: var(--primary); }
      #app { height: calc(100vh - 58px - 60px); }
    }
    @media (min-width: 641px) { .mobile-only { display: none !important; } }
  </style>
</head>
<body>

  <header id="topbar">
    <div style="display:flex;align-items:center;gap:12px">
      <span style="font-weight:700;font-size:16px">YOUR_APP_NAME</span>
    </div>
    <div style="display:flex;align-items:center;gap:10px">
      <span id="save-status" style="font-size:12px;color:var(--muted)"></span>
      <button id="theme-toggle" onclick="toggleTheme()" class="btn-ghost btn" style="padding:6px 10px">☀️</button>
    </div>
  </header>

  <div id="app">
    <nav id="sidebar">
      <!-- Inject nav items here — see C01 -->
    </nav>
    <main id="main">
      <!-- Each view is a div.view — only one shown at a time -->
      <!-- <div id="YOUR_VIEW" class="view"> ... </div> -->
    </main>
  </div>

  <nav id="bottombar">
    <!-- Mobile nav buttons — see C01 -->
  </nav>

  <div id="toast" role="status" aria-live="polite" style="position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:9999;display:flex;flex-direction:column;gap:8px;align-items:center"></div>

  <!-- Inline Chart.js 4.4.1 here if using C03 -->
  <!-- Inline XLSX.js 0.18.5 here if using C07 or C16 -->

  <script>
    // All JavaScript goes here — see component sections below
  </script>
</body>
</html>
```

---

### 1B. Security Utilities — MANDATORY, Copy Verbatim

**These two functions must be applied everywhere user data touches the DOM or a file. No exceptions.**

```javascript
// RULE: Wrap EVERY user-sourced string before inserting into innerHTML.
// Safe exceptions: fmt() output, boolean CSS class names, static strings you wrote.
function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

// RULE: Wrap EVERY cell value before writing to a CSV or Excel export.
// Prevents formula injection in Excel/Sheets (=SUM(...), +cmd, -cmd, @, tab, CR).
function csvSanitize(v) {
  const s = String(v == null ? '' : v);
  return /^[=+\-@\t\r]/.test(s) ? "'" + s : s;
}
```

**When to use each:**

| Situation | Use |
|-----------|-----|
| `element.innerHTML = '...' + userValue + '...'` | `escapeHtml(userValue)` |
| `element.textContent = userValue` | Safe — no escaping needed |
| `element.value = userValue` (input) | Safe — no escaping needed |
| Writing a cell to CSV/Excel file | `csvSanitize(value)` |
| onclick attribute with string param: `onclick="fn('${val}')"` | `escapeHtml(val).replace(/'/g, "&#39;")` |
| onclick attribute with numeric/ID param: `onclick="fn(${id})"` | `JSON.stringify(id)` |

---

### 1C. Generic IndexedDB Engine

**This is the data layer. Define your schema once; all CRUD functions below work for any record shape.**

```javascript
// ── CONFIGURE THESE FOR YOUR APP ──────────────────────────────────────────
const DB_NAME    = 'YOUR_APP_DB';     // e.g. 'TaskManager', 'InventoryApp'
const DB_VERSION = 1;
const STORE_NAME = 'records';         // e.g. 'tasks', 'items', 'contacts'

// Fields to index (enables fast filtering — add any field you filter/sort by)
const DB_INDEXES = [
  // { name: 'date',     keyPath: 'date'     },
  // { name: 'status',   keyPath: 'status'   },
  // { name: 'category', keyPath: 'category' },
  // { name: 'priority', keyPath: 'priority' },
  // Add your own:
];
// ── END CONFIG ────────────────────────────────────────────────────────────

let db = null;

async function initDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);

    req.onupgradeneeded = e => {
      const d = e.target.result;
      if (!d.objectStoreNames.contains(STORE_NAME)) {
        const store = d.createObjectStore(STORE_NAME, { keyPath: 'id' });
        DB_INDEXES.forEach(idx => store.createIndex(idx.name, idx.keyPath, { unique: false }));
      }
    };

    req.onsuccess = e => { db = e.target.result; resolve(db); };

    req.onerror = e => {
      // NEVER fail silently — show a visible error to the user
      document.body.innerHTML = `
        <div style="padding:40px;text-align:center;font-family:sans-serif;color:#e8eaf0;background:#0f1117;min-height:100vh">
          <h2>Storage Unavailable</h2>
          <p>This app needs browser storage to work.<br>Try a different browser, or disable private/incognito mode.</p>
          <p style="color:#6b7394;font-size:12px;margin-top:16px">${e.target.error}</p>
        </div>`;
      reject(e.target.error);
    };
  });
}

// ── CRUD ──────────────────────────────────────────────────────────────────

function dbPut(record) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(STORE_NAME, 'readwrite');
    const req = tx.objectStore(STORE_NAME).put(record);
    req.onsuccess = () => resolve();
    tx.onerror    = e => reject(e.target.error);
  });
}

function dbGet(id) {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(STORE_NAME, 'readonly');
    const req = tx.objectStore(STORE_NAME).get(id);
    req.onsuccess = () => resolve(req.result);
    tx.onerror    = e => reject(e.target.error);
  });
}

function dbDelete(id) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).delete(id).onsuccess = () => resolve();
    tx.onerror = e => reject(e.target.error);
  });
}

function dbGetAll() {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(STORE_NAME, 'readonly');
    const req = tx.objectStore(STORE_NAME).getAll();
    req.onsuccess = () => resolve(req.result || []);
    tx.onerror    = e => reject(e.target.error);
  });
}

function dbBulkPut(records, onProgress) {
  return new Promise((resolve, reject) => {
    if (!records.length) { resolve(); return; }
    const tx    = db.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    let done = 0;
    records.forEach(r => {
      const req   = store.put(r);
      req.onsuccess = () => {
        done++;
        if (onProgress) onProgress(done, records.length);
        if (done === records.length) resolve();
      };
    });
    tx.onerror = e => reject(e.target.error);
  });
}

function dbClear() {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite');
    tx.objectStore(STORE_NAME).clear().onsuccess = () => resolve();
    tx.onerror = e => reject(e.target.error);
  });
}

function dbCount() {
  return new Promise((resolve, reject) => {
    const tx  = db.transaction(STORE_NAME, 'readonly');
    const req = tx.objectStore(STORE_NAME).count();
    req.onsuccess = () => resolve(req.result);
    tx.onerror    = e => reject(e.target.error);
  });
}

// Advanced query: filter, search, sort, paginate — all in memory after dbGetAll()
// Customize the 'search' function to match your field names.
async function dbQuery({
  search   = '',
  filters  = {},    // { fieldName: 'value' } — any number of exact-match filters
  sort     = 'id',
  dir      = 'desc',
  page     = 1,
  pageSize = 25
} = {}) {
  let rows = await dbGetAll();

  // Apply exact-match filters (e.g. { status: 'active', category: 'Work' })
  Object.entries(filters).forEach(([key, val]) => {
    if (val !== '' && val != null) rows = rows.filter(r => String(r[key]) === String(val));
  });

  // Full-text search across SEARCH_FIELDS — customize this array for your app
  if (search.trim()) {
    const q = search.trim().toLowerCase();
    rows = rows.filter(r =>
      SEARCH_FIELDS.some(f => String(r[f] ?? '').toLowerCase().includes(q))
    );
  }

  // Sort — handles strings and numbers correctly
  rows.sort((a, b) => {
    let av = a[sort] ?? '', bv = b[sort] ?? '';
    if (typeof av === 'number' || !isNaN(+av)) { av = +av; bv = +bv; }
    if (av < bv) return dir === 'asc' ? -1 : 1;
    if (av > bv) return dir === 'asc' ?  1 : -1;
    return 0;
  });

  const total = rows.length;
  const start = (page - 1) * pageSize;
  return { rows: rows.slice(start, start + pageSize), total };
}

// ── CONFIGURE: which fields to search across ──────────────────────────────
// Replace with your record's text fields
const SEARCH_FIELDS = ['name', 'description', 'category', 'notes'];
// ─────────────────────────────────────────────────────────────────────────
```

---

### 1D. Record ID Generation

```javascript
// RULE: Always use this pattern. Never use sequential integers.
// Sequential IDs break if the user clears and reimports data (collisions).
// This float ID is unique per session and safe for IndexedDB keyPath.
function newId() {
  return Date.now() + Math.random();
}

// When passing an ID into an HTML onclick attribute:
//   CORRECT:   onclick="deleteRecord(${JSON.stringify(record.id)})"
//   INCORRECT: onclick="deleteRecord(${record.id})"   ← float may render as "1.234e+15"
```

---

### 1E. Settings System

```javascript
// ── CONFIGURE: define your app's settings ────────────────────────────────
const SETTINGS_KEY = 'YOUR_APP_settings_v1';

// Default values — add/remove fields for your app
let settings = {
  appName:  '',        // shown in sidebar / header
  // Add your own scalar config here, e.g.:
  // timezone: 'UTC',
  // defaultView: 'list',
  // itemsPerPage: 25,
};
// ─────────────────────────────────────────────────────────────────────────

function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) settings = { ...settings, ...JSON.parse(raw) };
  } catch { /* use defaults */ }
}

function saveSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}
```

---

### 1F. App Initialization — Required Order

```javascript
// Run in this exact order. Changing order causes blank screens or missing data.
async function initApp() {
  loadSettings();       // 1. Settings first — formatters depend on settings
  loadTags();           // 2. Load labels/tags (if using C08)
  applyTheme();         // 3. Theme before any rendering — prevents flash
  await initDB();       // 4. Open IndexedDB — must succeed before any data operation
  checkAuthSession();   // 5. Auth check (skip if no auth gate)
  showView(DEFAULT_VIEW); // 6. Show initial view
  scheduleVersionCheck(); // 7. Non-blocking update check
}

window.addEventListener('DOMContentLoaded', initApp);
```

---

## PART 2 — UI COMPONENTS

---

### C01 — Navigation Layout

**What it does:** Sidebar navigation on desktop, bottom tab bar on mobile. One function (`showView`) switches between views and updates active state everywhere.

**Customization points:** Define your views and nav items.

```javascript
// ── CONFIGURE: your app's views ───────────────────────────────────────────
const DEFAULT_VIEW = 'YOUR_MAIN_VIEW';  // e.g. 'dashboard', 'list-view'

// Map view ID → render function to call when switching to it
const VIEW_RENDERERS = {
  'YOUR_MAIN_VIEW':   renderMainView,
  'YOUR_LIST_VIEW':   () => renderTable({ page: 1 }),
  'YOUR_ADD_VIEW':    initAddForm,
  'YOUR_SETTINGS':    loadSettingsForm,
  // Add your views here
};

// Fields used to build mobile bottom bar (max 5 items)
const MOBILE_NAV = [
  { view: 'YOUR_MAIN_VIEW',  label: 'Home',   icon: '🏠' },
  { view: 'YOUR_LIST_VIEW',  label: 'List',   icon: '📋' },
  { view: 'YOUR_ADD_VIEW',   label: 'Add',    icon: '+',  fab: true },
  { view: 'YOUR_SETTINGS',   label: 'Settings', icon: '⚙️' },
];
// ─────────────────────────────────────────────────────────────────────────

function showView(viewId) {
  // Hide all views
  document.querySelectorAll('.view').forEach(v => {
    v.style.display = 'none';
    v.classList.remove('active');
  });

  // Show target view
  const target = document.getElementById(viewId);
  if (!target) { console.warn('View not found:', viewId); return; }
  target.style.display = 'block';
  target.classList.add('active');

  // Update sidebar active state
  document.querySelectorAll('.nav-item[data-view]').forEach(a => {
    a.classList.toggle('active', a.dataset.view === viewId);
  });

  // Update mobile bottom bar active state
  document.querySelectorAll('#bottombar button[data-view]').forEach(b => {
    b.classList.toggle('active', b.dataset.view === viewId);
  });

  // Run the view's render function
  const renderer = VIEW_RENDERERS[viewId];
  if (renderer) renderer();
}

// Build mobile bottom bar from MOBILE_NAV config
function buildMobileNav() {
  const bar = document.getElementById('bottombar');
  bar.innerHTML = MOBILE_NAV.map(item => `
    <button data-view="${item.view}" onclick="showView('${item.view}')"
            ${item.fab ? 'style="font-size:24px;font-weight:700;color:var(--primary)"' : ''}>
      <span>${item.icon}</span>
      <span>${item.fab ? '' : item.label}</span>
    </button>
  `).join('');
}
```

**HTML for sidebar nav items:**
```html
<nav id="sidebar">
  <div class="nav-label">SECTION NAME</div>
  <a class="nav-item" data-view="YOUR_VIEW_ID" onclick="showView('YOUR_VIEW_ID')">
    🏠 View Name
  </a>
  <!-- repeat for each view -->
</nav>
```

**Known bugs to avoid:**
- Always call `showView()` for navigation — never toggle `display` directly, it skips the renderer and active-state updates.
- If a view renders a chart, only call `renderChart()` inside its VIEW_RENDERER — not on load — or the canvas will be 0px height.

---

### C02 — KPI Summary Cards

**What it does:** A row of metric boxes showing totals, counts, averages, or any computed number from your records.

**Customization points:** Define what metrics to show and how to compute them.

```javascript
// ── CONFIGURE: define your KPI metrics ───────────────────────────────────
// Each metric: { id, label, compute(records) → value, format(value) → string, colorFn(value) → css-color-var }
const KPI_METRICS = [
  {
    id:      'kpi-total',
    label:   'Total Records',
    compute: records => records.length,
    format:  v => v.toLocaleString(),
    color:   () => 'var(--primary)',
  },
  {
    id:      'kpi-active',
    label:   'Active',
    compute: records => records.filter(r => r.status === 'active').length,
    format:  v => v.toLocaleString(),
    color:   v => v > 0 ? 'var(--success)' : 'var(--muted)',
  },
  // Add your own metrics here...
];
// ─────────────────────────────────────────────────────────────────────────

async function renderKPICards() {
  const records = await dbGetAll();
  // Apply any active filters (e.g. date range) before passing to compute
  const filtered = applyGlobalFilter(records); // define this for your app

  KPI_METRICS.forEach(metric => {
    const el = document.getElementById(metric.id);
    if (!el) return;
    const value = metric.compute(filtered);
    el.textContent = metric.format(value);
    el.style.color = metric.color(value);
  });
}
```

**HTML template (repeat per metric):**
```html
<div class="kpi-grid">
  <!-- Generated from KPI_METRICS config -->
  <div class="card kpi-card">
    <div class="kpi-label">LABEL</div>
    <div class="kpi-value" id="kpi-METRICID" style="font-size:26px;font-weight:700">—</div>
    <div class="kpi-sub" id="kpi-METRICID-sub" style="font-size:12px;color:var(--muted)"></div>
  </div>
</div>
```

**CSS:**
```css
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
.kpi-card { padding: 20px; }
.kpi-label { font-size: 13px; color: var(--muted); margin-bottom: 8px; }
```

**Known bugs to avoid:**
- Always guard divide-by-zero: `denominator > 0 ? numerator / denominator : 0`
- Use `Math.round(value * 100) / 100` for any decimal before display — prevents `0.30000000000000004`

**P&L Dashboard example:** 6 KPIs: Total Revenue, Expenses, Net Profit, Gross Profit, Margin %, Avg Monthly Revenue.

---

### C03 — Charts

**What it does:** Bar, line, and pie/doughnut charts that visualize your record data.

**Dependency:** Chart.js 4.4.1 (inline the library in your HTML — no CDN at runtime, for offline support).

```javascript
// ── CONFIGURE: define your charts ────────────────────────────────────────
// Chart instances stored here so they can be destroyed before recreating
const charts = {};

// Read CSS variables at render time (not at init) so theme changes work
function themeColors() {
  const s = getComputedStyle(document.documentElement);
  return {
    text:    s.getPropertyValue('--text').trim(),
    muted:   s.getPropertyValue('--muted').trim(),
    surface: s.getPropertyValue('--surface').trim(),
    border:  s.getPropertyValue('--border').trim(),
    primary: s.getPropertyValue('--primary').trim(),
    warning: s.getPropertyValue('--warning').trim(),
    danger:  s.getPropertyValue('--danger').trim(),
  };
}
// ─────────────────────────────────────────────────────────────────────────

// RULE: Always destroy before recreating. Chart.js throws if canvas is reused.
function destroyChart(key) {
  if (charts[key]) { try { charts[key].destroy(); } catch(e) {} delete charts[key]; }
}

// Shared chart base options (reuse for all chart types)
function baseChartOptions(tc) {
  return {
    responsive:          true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: tc.text, font: { size: 12 } } },
    },
    scales: {
      x: { ticks: { color: tc.muted }, grid: { color: tc.border + '55' } },
      y: { ticks: { color: tc.muted }, grid: { color: tc.border + '55' } },
    }
  };
}

// ── EXAMPLE: Bar chart (adapt GROUP_BY and VALUE_FIELD for your data) ─────
async function renderBarChart() {
  const records = await dbGetAll();
  const tc      = themeColors();

  // Group records by a field (e.g. month, status, category)
  const grouped = {};
  records.forEach(r => {
    const key = r.YOUR_GROUP_BY_FIELD || 'Other'; // e.g. r.month, r.status
    grouped[key] = (grouped[key] || 0) + (r.YOUR_NUMERIC_FIELD || 0);
  });

  const labels = Object.keys(grouped);
  const data   = Object.values(grouped);

  // Guard: don't create empty chart
  if (!data.length) return;

  destroyChart('bar');
  charts.bar = new Chart(document.getElementById('chart-bar'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'YOUR_LABEL', data, backgroundColor: tc.primary + '99' }]
    },
    options: baseChartOptions(tc)
  });
}

// ── EXAMPLE: Pie/doughnut chart ───────────────────────────────────────────
const CHART_COLORS = ['#0ecfbe','#3b82f6','#f5a623','#e74c3c','#8b5cf6','#10b981','#f59e0b','#6366f1','#ec4899','#14b8a6','#a855f7','#ef4444'];

async function renderPieChart() {
  const records = await dbGetAll();
  const tc      = themeColors();

  const grouped = {};
  records.forEach(r => {
    const key = r.YOUR_CATEGORY_FIELD || 'Uncategorized';
    grouped[key] = (grouped[key] || 0) + 1; // or + r.YOUR_NUMERIC_FIELD
  });

  const labels = Object.keys(grouped);
  const data   = Object.values(grouped);
  if (!data.length) return;

  destroyChart('pie');
  charts.pie = new Chart(document.getElementById('chart-pie'), {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: CHART_COLORS.slice(0, labels.length) }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { color: tc.text, font: { size: 11 }, boxWidth: 12 } }
      }
    }
  });
}

// Call after theme toggle (destroy + recreate is simpler than patching colors)
function retintCharts() {
  // Re-call each render function — they destroy and recreate
  renderBarChart();
  renderPieChart();
}
```

**HTML canvases:**
```html
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
  <div class="card"><h3>YOUR CHART TITLE</h3>
    <div style="position:relative;height:240px"><canvas id="chart-bar"></canvas></div>
  </div>
  <div class="card"><h3>YOUR PIE TITLE</h3>
    <div style="position:relative;height:240px"><canvas id="chart-pie"></canvas></div>
  </div>
</div>
```

**Known bugs to avoid:**
- `destroyChart(key)` before every `new Chart()` — without this the second render throws.
- Read `themeColors()` inside the render function, not at module load — otherwise theme toggle won't update chart colors.
- If data is empty, skip chart creation. Chart.js renders a broken empty circle otherwise.

---

### C04 — Filterable Paginated Table

**What it does:** A sortable, searchable, paginated table. Works for any record type.

**Customization points:** Define columns, default sort, filter fields.

```javascript
// ── CONFIGURE: define your table columns ─────────────────────────────────
const TABLE_COLUMNS = [
  // { key: fieldName, label: 'Header Text', sortable: true, render: (record) => htmlString }
  { key: 'name',        label: 'Name',        sortable: true,
    render: r => escapeHtml(r.name || '—') },
  { key: 'status',      label: 'Status',      sortable: true,
    render: r => `<span class="badge badge-primary">${escapeHtml(r.status || '')}</span>` },
  { key: 'created_at',  label: 'Created',     sortable: true,
    render: r => escapeHtml(r.created_at || '') },
  // Add your columns here. ALWAYS use escapeHtml() in render functions.
  { key: '_actions',    label: '',             sortable: false,
    render: r => `<button class="btn btn-ghost" onclick="deleteRecord(${JSON.stringify(r.id)})">🗑</button>` },
];

// Filter fields — dropdowns above the table
// Each: { key: fieldName, label: 'Label', options: [] or 'dynamic' }
const TABLE_FILTERS = [
  { key: 'status',   label: 'Status',   options: ['active','inactive','pending'] },
  { key: 'category', label: 'Category', options: 'dynamic' }, // populated from data
];
// ─────────────────────────────────────────────────────────────────────────

// Table state (module-level)
let tableState = {
  page:     1,
  pageSize: 25,
  sort:     TABLE_COLUMNS.find(c => c.sortable)?.key || 'id',
  dir:      'desc',
  search:   '',
  filters:  {},
};

async function renderTable(overrides = {}) {
  Object.assign(tableState, overrides);

  const { rows, total } = await dbQuery({
    search:   tableState.search,
    filters:  tableState.filters,
    sort:     tableState.sort,
    dir:      tableState.dir,
    page:     tableState.page,
    pageSize: tableState.pageSize,
  });

  const tbody = document.getElementById('main-tbody');

  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="${TABLE_COLUMNS.length}" style="text-align:center;padding:40px;color:var(--muted)">
      No records found.
    </td></tr>`;
  } else {
    // BUG: escapeHtml is applied inside each column's render() — never skip it
    tbody.innerHTML = rows.map(r =>
      `<tr>${TABLE_COLUMNS.map(col => `<td>${col.render(r)}</td>`).join('')}</tr>`
    ).join('');
  }

  // Update count label
  const countEl = document.getElementById('table-count');
  if (countEl) countEl.textContent = `${total.toLocaleString()} records`;

  // Render pagination
  renderPagination('table-pagination', tableState.page, total, tableState.pageSize, p => {
    tableState.page = p;
    renderTable();
  });

  // Update sort indicators on headers
  document.querySelectorAll('th[data-sort]').forEach(th => {
    const isActive = th.dataset.sort === tableState.sort;
    th.textContent = th.dataset.label + (isActive ? (tableState.dir === 'asc' ? ' ↑' : ' ↓') : '');
  });
}

function sortTable(col) {
  if (tableState.sort === col) {
    tableState.dir = tableState.dir === 'asc' ? 'desc' : 'asc';
  } else {
    tableState.sort = col;
    tableState.dir  = 'asc';
  }
  tableState.page = 1;
  renderTable();
}

// Shared pagination renderer (reuse for every table in the app)
function renderPagination(containerId, currentPage, total, pageSize, onPageChange) {
  const totalPages = Math.ceil(total / pageSize);
  const el = document.getElementById(containerId);
  if (!el) return;
  if (totalPages <= 1) { el.innerHTML = ''; return; }

  const start = (currentPage - 1) * pageSize + 1;
  const end   = Math.min(currentPage * pageSize, total);

  // Build page number array with ellipsis
  const pageNums = [];
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) pageNums.push(i);
  }
  const withGaps = [];
  pageNums.forEach((p, i) => {
    if (i > 0 && p - pageNums[i-1] > 1) withGaps.push('…');
    withGaps.push(p);
  });

  el.innerHTML = `
    <span class="pg-info">Showing ${start}–${end} of ${total}</span>
    <button onclick="(${onPageChange})(1)"               ${currentPage===1?'disabled':''}>«</button>
    <button onclick="(${onPageChange})(${currentPage-1})" ${currentPage===1?'disabled':''}>‹</button>
    ${withGaps.map(p => p === '…'
      ? `<span style="padding:0 4px;color:var(--muted)">…</span>`
      : `<button class="${p===currentPage?'active':''}" onclick="(${onPageChange})(${p})">${p}</button>`
    ).join('')}
    <button onclick="(${onPageChange})(${currentPage+1})" ${currentPage===totalPages?'disabled':''}>›</button>
    <button onclick="(${onPageChange})(${totalPages})"     ${currentPage===totalPages?'disabled':''}>»</button>`;
}

// Debounced search (prevents DB query on every keypress)
let _searchTimer;
function onTableSearch(value) {
  clearTimeout(_searchTimer);
  _searchTimer = setTimeout(() => {
    tableState.search = value;
    tableState.page   = 1; // RULE: reset to page 1 on new search
    renderTable();
  }, 250);
}

// Filter dropdown change
function onTableFilter(field, value) {
  tableState.filters[field] = value;
  tableState.page = 1; // RULE: reset to page 1 on filter change
  renderTable();
}
```

**HTML structure:**
```html
<div id="YOUR_LIST_VIEW" class="view">
  <!-- Toolbar: search + filter dropdowns -->
  <div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
    <input type="search" placeholder="Search..." oninput="onTableSearch(this.value)"
           style="flex:1;min-width:200px" class="form-input">
    <!-- Repeat per TABLE_FILTERS entry: -->
    <select class="form-input" style="width:auto" onchange="onTableFilter('status', this.value)">
      <option value="">All Status</option>
      <option value="active">Active</option>
    </select>
    <span id="table-count" style="color:var(--muted);font-size:13px;align-self:center"></span>
  </div>

  <!-- Table -->
  <div class="card table-wrap">
    <table>
      <thead>
        <tr>
          <!-- Generated from TABLE_COLUMNS config — mark sortable ones -->
          <th class="sortable" data-sort="name" data-label="Name" onclick="sortTable('name')">Name ↓</th>
          <th>Status</th>
          <th>Created</th>
          <th></th>
        </tr>
      </thead>
      <tbody id="main-tbody"></tbody>
    </table>
  </div>
  <div id="table-pagination" class="pagination"></div>
</div>
```

**Known bugs to avoid:**
- Search timer must reset `tableState.page = 1` — otherwise you stay on page 5 with 0 results.
- Every column `render()` function must use `escapeHtml()` on user data. Forgetting one column is all XSS needs.
- Sort direction must persist across page changes — never reset `tableState.sort/dir` in `renderTable()`.

---

### C05 — Quick-Entry Form

**What it does:** A fast single-record add form. Includes an autocomplete field, keyboard-first flow (Enter to submit), and a "recently added" preview below the form.

**Customization points:** Define your form fields and validation rules.

```javascript
// ── CONFIGURE: define your form fields ───────────────────────────────────
const FORM_FIELDS = [
  // { id: 'htmlInputId', key: 'recordFieldName', required: true, transform: fn }
  { id: 'f-name',        key: 'name',        required: true,  transform: v => v.trim() },
  { id: 'f-category',    key: 'category',    required: false, transform: v => v.trim() || 'Uncategorized' },
  { id: 'f-amount',      key: 'amount',      required: true,  transform: v => Math.abs(parseFloat(v)) },
  { id: 'f-date',        key: 'date',        required: true,  transform: v => v },
  { id: 'f-description', key: 'description', required: false, transform: v => v.trim() },
];

// Validation rules: return error string or null
const FORM_VALIDATORS = [
  ({ amount }) => (!amount || amount <= 0) ? 'Amount must be a positive number' : null,
  ({ date })   => (!date) ? 'Date is required' : null,
  ({ name })   => (!name) ? 'Name is required' : null,
];

// Fields to show in the "recently added" preview table
const RECENT_COLUMNS = [
  { key: 'date',     label: 'Date',     render: r => escapeHtml(r.date || '') },
  { key: 'name',     label: 'Name',     render: r => escapeHtml(r.name || '') },
  { key: 'category', label: 'Category', render: r => `<span class="badge badge-primary">${escapeHtml(r.category || '')}</span>` },
];
// ─────────────────────────────────────────────────────────────────────────

function initAddForm() {
  // Set date to today (UTC-safe)
  const todayInput = document.getElementById('f-date');
  if (todayInput && !todayInput.value) {
    todayInput.value = new Date().toISOString().slice(0, 10);
  }
  updateAutocompleteList(); // Populate datalist for autocomplete field (see below)
  renderRecentEntries();
}

async function submitAddForm(e) {
  if (e) e.preventDefault();

  // Clear previous error
  const errEl = document.getElementById('form-error');
  if (errEl) errEl.textContent = '';

  // Read + transform all fields
  const raw = {};
  FORM_FIELDS.forEach(f => {
    const el = document.getElementById(f.id);
    raw[f.key] = el ? f.transform(el.value) : '';
  });

  // Validate
  for (const validator of FORM_VALIDATORS) {
    const err = validator(raw);
    if (err) {
      if (errEl) errEl.textContent = err;
      return;
    }
  }

  // Build record — add any derived fields here
  const record = {
    id: newId(),
    ...raw,
    created_at: new Date().toISOString(),
    // Add your derived fields:
    // month: getMonthFromDate(raw.date),
    // year:  getYearFromDate(raw.date),
  };

  await dbPut(record);
  scheduleSnapshot();

  // Clear amount + description, keep date/category for rapid entry
  ['f-amount', 'f-description', 'f-name'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });

  // Refocus first required field for rapid re-entry
  document.getElementById('f-name')?.focus();

  toast('Record added', 'success');
  renderRecentEntries();
}

async function renderRecentEntries() {
  const all    = await dbGetAll();
  const recent = all.sort((a, b) => b.id - a.id).slice(0, 5);
  const tbody  = document.getElementById('recent-tbody');
  if (!tbody) return;

  tbody.innerHTML = recent.length
    ? recent.map(r =>
        `<tr>${RECENT_COLUMNS.map(col => `<td>${col.render(r)}</td>`).join('')}</tr>`
      ).join('')
    : `<tr><td colspan="${RECENT_COLUMNS.length}" style="color:var(--muted);text-align:center;padding:20px">No records yet</td></tr>`;
}

// Autocomplete datalist — populate from existing records + static tags
async function updateAutocompleteList() {
  const all    = await dbGetAll();
  // Extract unique values from your autocomplete field (e.g. category)
  const values = [...new Set(all.map(r => r.category).filter(Boolean)), ...TAGS];
  const list   = document.getElementById('autocomplete-list');
  if (list) list.innerHTML = values.map(v => `<option value="${escapeHtml(v)}">`).join('');
}
```

**HTML:**
```html
<div id="YOUR_ADD_VIEW" class="view">
  <form onsubmit="submitAddForm(event)" style="max-width:520px">
    <div id="form-error" style="color:var(--danger);font-size:13px;margin-bottom:10px"></div>

    <div style="margin-bottom:14px">
      <label class="form-label">Name *</label>
      <input id="f-name" type="text" class="form-input" required>
    </div>

    <div style="margin-bottom:14px">
      <label class="form-label">Category</label>
      <input id="f-category" type="text" class="form-input" list="autocomplete-list" autocomplete="off">
      <datalist id="autocomplete-list"></datalist>
    </div>

    <div style="margin-bottom:14px">
      <label class="form-label">Date *</label>
      <input id="f-date" type="date" class="form-input" required>
    </div>

    <div style="margin-bottom:20px">
      <label class="form-label">Notes</label>
      <input id="f-description" type="text" class="form-input">
    </div>

    <button type="submit" class="btn btn-primary">Add Record</button>
  </form>

  <!-- Recently added preview -->
  <div style="margin-top:32px">
    <h3 style="font-size:15px;margin-bottom:12px">Recently Added</h3>
    <div class="card table-wrap">
      <table><thead><tr>
        <!-- Match RECENT_COLUMNS -->
        <th>Date</th><th>Name</th><th>Category</th>
      </tr></thead>
      <tbody id="recent-tbody"></tbody></table>
    </div>
  </div>
</div>
```

**Known bugs to avoid:**
- `new Date().toISOString().slice(0,10)` for today — never `new Date().toLocaleDateString()` (locale-dependent format).
- `Math.abs(parseFloat(v))` for numeric fields — prevents negative storage, NaN.
- Clear the error element at the start of every submit — stale errors confuse users.
- `newId()` = `Date.now() + Math.random()` — never a sequential counter that resets on page reload.

---

### C06 — Bulk Select + Delete + Undo

**What it does:** Adds checkboxes to table rows. When rows are selected, a floating action bar appears. Deleting shows a 6-second Undo toast before the action becomes permanent.

```javascript
// Module-level selection set — stores String(record.id)
const selectedIds = new Set();

// Call after rendering each table row to wire up checkboxes
function onRowCheck(checkbox) {
  const id = checkbox.value; // stored as string
  if (checkbox.checked) selectedIds.add(id);
  else                  selectedIds.delete(id);
  updateBulkBar();
}

function toggleSelectAll(masterCheckbox) {
  document.querySelectorAll('.row-checkbox').forEach(cb => {
    cb.checked = masterCheckbox.checked;
    onRowCheck(cb);
  });
}

function updateBulkBar() {
  const bar   = document.getElementById('bulk-bar');
  const count = document.getElementById('bulk-count');
  if (!bar) return;
  bar.style.display = selectedIds.size > 0 ? 'flex' : 'none';
  if (count) count.textContent = `${selectedIds.size} selected`;
}

async function deleteBulkSelected() {
  if (!selectedIds.size) return;
  const ids = [...selectedIds];

  // Load records BEFORE deleting (for undo)
  const deleted = (await Promise.all(ids.map(id => dbGet(+id || id)))).filter(Boolean);

  if (!confirm(`Delete ${ids.length} record(s)?`)) return;

  await Promise.all(ids.map(id => dbDelete(+id || id)));
  selectedIds.clear();
  updateBulkBar();
  renderTable();
  offerUndo(`Deleted ${deleted.length} record(s)`, deleted);
}

// Delete a single record with undo
async function deleteRecord(id) {
  const record = await dbGet(id);
  if (!record) return;
  await dbDelete(id);
  renderTable();
  offerUndo('Record deleted', [record]);
}
```

**Add to table rows (inside your column render or tbody HTML):**
```html
<!-- Header row -->
<th><input type="checkbox" id="check-all" onchange="toggleSelectAll(this)"></th>

<!-- Data rows (in render function) -->
<td><input type="checkbox" class="row-checkbox" value="${JSON.stringify(r.id)}" onchange="onRowCheck(this)"></td>
```

**Bulk action bar (floating, shown when selection > 0):**
```html
<div id="bulk-bar" style="display:none;position:fixed;bottom:80px;left:50%;transform:translateX(-50%);
  background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 20px;
  box-shadow:var(--shadow);gap:14px;align-items:center;z-index:200">
  <span id="bulk-count">0 selected</span>
  <button class="btn btn-danger" onclick="deleteBulkSelected()">Delete Selected</button>
  <button class="btn btn-ghost" onclick="selectedIds.clear();updateBulkBar();renderTable()">Cancel</button>
</div>
```

**Known bugs to avoid:**
- Store IDs as `String(record.id)` in the Set — floats compare unreliably as object keys.
- When deleting, convert back: `dbDelete(+id || id)` handles both float and string IDs.
- Fetch records for undo BEFORE calling `dbDelete` — after deletion, `dbGet` returns undefined.
- Clear `selectedIds` after every bulk delete and after switching views.

---

### C07 — CSV / Excel Import with Field Mapping

**What it does:** User uploads any CSV or XLSX file. A mapping modal lets them connect each file column to a record field. Large files use a Web Worker so the UI stays responsive.

```javascript
// ── CONFIGURE: define your importable fields ──────────────────────────────
const IMPORT_FIELDS = [
  // { key: 'recordField', label: 'Display Name', required: true }
  { key: 'name',        label: 'Name',        required: true  },
  { key: 'date',        label: 'Date',        required: true  },
  { key: 'category',    label: 'Category',    required: false },
  { key: 'description', label: 'Description', required: false },
  // { key: 'amount', label: 'Amount', required: true, numeric: true },
  // Add your fields here
];

// Keywords that auto-guess column mapping from CSV headers
const IMPORT_GUESS_KEYWORDS = {
  name:        ['name', 'title', 'item', 'product'],
  date:        ['date', 'time', 'period', 'created'],
  category:    ['category', 'cat', 'type', 'class', 'group'],
  description: ['description', 'desc', 'note', 'memo', 'detail'],
  amount:      ['amount', 'total', 'value', 'price', 'cost', 'sum'],
};
// ─────────────────────────────────────────────────────────────────────────

let _csvRows = []; // module-level: rows[][] from parsed file

// RFC 4180 compliant CSV parser — handles quoted fields, embedded commas, escaped quotes
function parseCSV(text) {
  text = text.replace(/^﻿/, ''); // strip BOM
  const rows = [];
  let field = '', row = [], inQ = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (inQ) {
      if (ch === '"') {
        if (text[i+1] === '"') { field += '"'; i++; } // escaped quote
        else inQ = false;
      } else field += ch;
    } else {
      if (ch === '"')  inQ = true;
      else if (ch === ',') { row.push(field); field = ''; }
      else if (ch === '\n' || (ch === '\r' && text[i+1] !== '\n')) {
        row.push(field); if (row.some(c => c !== '')) rows.push(row); row = []; field = '';
      } else if (ch !== '\r') field += ch;
    }
  }
  if (field || row.length) { row.push(field); if (row.some(c => c !== '')) rows.push(row); }
  return rows;
}

// Web Worker source for large files (> 500KB)
const CSV_WORKER = `
  self.onmessage = function(e) {
    const text = e.data;
    text.replace(/^\\uFEFF/, '');
    const rows = [];
    let field='', row=[], inQ=false;
    for (let i=0; i<text.length; i++) {
      const ch=text[i];
      if(inQ){if(ch==='"'){if(text[i+1]==='"'){field+='"';i++;}else inQ=false;}else field+=ch;}
      else{if(ch==='"')inQ=true;else if(ch===','){row.push(field);field='';}
      else if(ch==='\\n'||(ch==='\\r'&&text[i+1]!=='\\n')){row.push(field);if(row.some(c=>c!==''))rows.push(row);row=[];field='';}
      else if(ch!=='\\r')field+=ch;}
    }
    if(field||row.length){row.push(field);if(row.some(c=>c!==''))rows.push(row);}
    self.postMessage(rows);
  };
`;

async function handleFileSelect(file) {
  const text = await file.text();
  let rows;

  if (text.length > 500_000 && typeof Worker !== 'undefined') {
    rows = await new Promise(resolve => {
      const blob   = new Blob([CSV_WORKER], { type: 'application/javascript' });
      const worker = new Worker(URL.createObjectURL(blob));
      worker.onmessage = e => { worker.terminate(); resolve(e.data); };
      worker.postMessage(text);
    });
  } else {
    rows = parseCSV(text);
  }

  if (rows.length < 2) { toast('File is empty or has only headers', 'error'); return; }
  openMappingModal(rows, file.name);
}

function openMappingModal(rows, filename) {
  _csvRows = rows;
  const headers  = rows[0] || [];
  const preview  = rows.slice(1, 4);

  // Auto-guess field mapping
  const guessed = {};
  headers.forEach((h, i) => {
    const low = (h || '').toLowerCase().trim();
    Object.entries(IMPORT_GUESS_KEYWORDS).forEach(([field, keywords]) => {
      if (keywords.some(k => low.includes(k)) && guessed[field] == null) guessed[field] = i;
    });
  });

  // Build mapping modal HTML
  const modal = document.getElementById('import-modal');
  document.getElementById('import-preview-thead').innerHTML =
    `<tr>${headers.map(h => `<th>${escapeHtml(h)}</th>`).join('')}</tr>`;
  document.getElementById('import-preview-tbody').innerHTML =
    preview.map(row => `<tr>${row.map(c => `<td>${escapeHtml(c)}</td>`).join('')}</tr>`).join('');

  document.getElementById('import-field-map').innerHTML = IMPORT_FIELDS.map(f => `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
      <label style="width:120px;font-size:13px">${f.label}${f.required ? ' *' : ''}</label>
      <select id="map-${f.key}" class="form-input" style="flex:1">
        <option value="-1">— skip —</option>
        ${headers.map((h, i) => `<option value="${i}" ${guessed[f.key]===i?'selected':''}>${escapeHtml(h)}</option>`).join('')}
      </select>
    </div>
  `).join('');

  modal.style.display = 'flex';
}

async function applyImport() {
  const headers  = _csvRows[0] || [];
  const dataRows = _csvRows.slice(1);

  // Read column mapping
  const map = {};
  IMPORT_FIELDS.forEach(f => {
    map[f.key] = +document.getElementById(`map-${f.key}`).value;
  });

  // Validate required fields are mapped
  const missing = IMPORT_FIELDS.filter(f => f.required && map[f.key] < 0).map(f => f.label);
  if (missing.length) { toast(`Map required fields: ${missing.join(', ')}`, 'error'); return; }

  const imported = [], skipped = [];

  dataRows.forEach((row, i) => {
    const raw = {};
    IMPORT_FIELDS.forEach(f => {
      raw[f.key] = map[f.key] >= 0 ? (row[map[f.key]] || '').trim() : '';
    });

    // Validate required fields have values
    if (IMPORT_FIELDS.filter(f => f.required).some(f => !raw[f.key])) {
      skipped.push(i + 2); return;
    }

    imported.push({
      id: newId(),
      ...raw,
      // Add derived fields for your app here, e.g.:
      // year: getYearFromDate(raw.date),
    });
  });

  if (!imported.length) { toast('No valid rows found — check column mapping', 'error'); return; }

  await dbBulkPut(imported);
  scheduleSnapshot();
  document.getElementById('import-modal').style.display = 'none';
  toast(`Imported ${imported.length} records${skipped.length ? ` (${skipped.length} skipped)` : ''}`, 'success');
  renderTable();
}
```

**HTML for import modal:**
```html
<!-- Import trigger -->
<button class="btn btn-outline" onclick="document.getElementById('file-input').click()">Import CSV</button>
<input id="file-input" type="file" accept=".csv,.xlsx" style="display:none"
       onchange="handleFileSelect(this.files[0]);this.value=''">

<!-- Mapping Modal -->
<div id="import-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);
  z-index:500;align-items:center;justify-content:center">
  <div class="card" style="width:min(700px,95vw);max-height:85vh;overflow-y:auto">
    <h3 style="margin-bottom:16px">Map CSV Columns</h3>

    <!-- Preview -->
    <div class="table-wrap" style="margin-bottom:20px;max-height:150px;overflow:auto">
      <table><thead id="import-preview-thead"></thead><tbody id="import-preview-tbody"></tbody></table>
    </div>

    <!-- Field mapping -->
    <div id="import-field-map"></div>

    <div style="display:flex;gap:10px;margin-top:20px">
      <button class="btn btn-primary" onclick="applyImport()">Import</button>
      <button class="btn btn-outline" onclick="document.getElementById('import-modal').style.display='none'">Cancel</button>
    </div>
  </div>
</div>
```

**Known bugs to avoid:**
- RFC 4180: `""` inside quoted fields = literal `"`. Must handle in parser or imports with quotes in text corrupt silently.
- Strip BOM (`﻿`) from CSV text before parsing — Excel-exported CSVs have it and it breaks header detection.
- `this.value = ''` after reading file input — allows re-selecting the same file.
- Large file web worker must inline the CSV parser (it can't import external scripts).

---

### C08 — Tag / Label Management

**What it does:** Users create, rename, and delete labels used to categorize records. Renaming propagates to all existing records automatically.

```javascript
// ── CONFIGURE ─────────────────────────────────────────────────────────────
const TAGS_KEY = 'YOUR_APP_tags_v1';

// Default tags for a fresh install
const DEFAULT_TAGS = [
  'General', 'Work', 'Personal', 'Urgent',
  // Add your defaults here
];

let TAGS = [...DEFAULT_TAGS];

function loadTags() {
  try {
    const raw = localStorage.getItem(TAGS_KEY);
    if (raw) TAGS = JSON.parse(raw);
  } catch { TAGS = [...DEFAULT_TAGS]; }
}

function saveTags() {
  localStorage.setItem(TAGS_KEY, JSON.stringify(TAGS));
}
// ─────────────────────────────────────────────────────────────────────────

function renderTagManager() {
  const container = document.getElementById('tag-list');
  if (!container) return;
  // BUG: always escapeHtml on tag name — user-supplied string in innerHTML
  container.innerHTML = TAGS.map((tag, i) => `
    <div style="display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--border)">
      <span style="flex:1">${escapeHtml(tag)}</span>
      <button class="btn btn-ghost" onclick="openRenameTag(${i})">✏️</button>
      <button class="btn btn-ghost" onclick="deleteTag(${i})">🗑</button>
    </div>
  `).join('');
}

function addTag(name) {
  name = name.trim();
  if (!name) { toast('Tag name required', 'error'); return; }
  // Case-insensitive duplicate check
  if (TAGS.some(t => t.toLowerCase() === name.toLowerCase())) {
    toast('Tag already exists', 'error'); return;
  }
  TAGS.push(name);
  saveTags();
  renderTagManager();
  updateAutocompleteList();
  toast(`Tag "${name}" added`, 'success');
}

async function renameTag(index, newName) {
  newName = newName.trim();
  if (!newName) { toast('Name required', 'error'); return; }
  if (TAGS.some((t, i) => i !== index && t.toLowerCase() === newName.toLowerCase())) {
    toast('Name already in use', 'error'); return;
  }

  const oldName = TAGS[index];

  // Propagate rename to all records — update the field that holds tags
  const all      = await dbGetAll();
  const toUpdate = all.filter(r => r.category === oldName); // change 'category' to your tag field
  await Promise.all(toUpdate.map(r => dbPut({ ...r, category: newName })));

  TAGS[index] = newName;
  saveTags();
  renderTagManager();
  updateAutocompleteList();
  toast(`Renamed to "${newName}" — ${toUpdate.length} records updated`, 'success');
}

async function deleteTag(index) {
  const name = TAGS[index];
  if (!confirm(`Delete tag "${name}"? Records using it will be set to "Uncategorized".`)) return;

  const all      = await dbGetAll();
  const toUpdate = all.filter(r => r.category === name);
  await Promise.all(toUpdate.map(r => dbPut({ ...r, category: 'Uncategorized' })));

  TAGS.splice(index, 1);
  saveTags();
  renderTagManager();
  updateAutocompleteList();
  toast(`Deleted "${name}" — ${toUpdate.length} records updated`, 'success');
}
```

**Known bugs to avoid:**
- `escapeHtml(tag)` in `renderTagManager` — tag names are user-supplied and will be in `innerHTML`.
- Rename: check for duplicates at `idx !== index` — otherwise it flags the tag being renamed as a duplicate of itself.
- After rename/delete, call `updateAutocompleteList()` to keep the add form datalist in sync.

---

### C09 — Three-Layer Backup System

**What it does:**
- **Layer 1** — Auto-saves a browser snapshot every 3 seconds after any data change (up to 5 kept in localStorage).
- **Layer 2** — Links a file on your computer; auto-saves to it every 30 minutes (Chrome/Edge/Brave only).
- **Layer 3** — OAuth sign-in to sync with Google Sheets in the cloud.

```javascript
// ── Layer 1: Browser Snapshots ────────────────────────────────────────────
const SNAPSHOTS_KEY  = 'YOUR_APP_snapshots_v1';
const MAX_SNAPSHOTS  = 5;
let   _snapTimer     = null;

// Call this after EVERY data mutation (dbPut, dbDelete, dbBulkPut, dbClear)
function scheduleSnapshot() {
  clearTimeout(_snapTimer);
  _snapTimer = setTimeout(takeSnapshot, 3000); // debounce 3 seconds
}

async function takeSnapshot() {
  const all  = await dbGetAll();
  let   snaps = loadSnapshots();

  snaps.unshift({ ts: Date.now(), count: all.length, data: all });
  snaps = snaps.slice(0, MAX_SNAPSHOTS);

  try {
    localStorage.setItem(SNAPSHOTS_KEY, JSON.stringify(snaps));
  } catch (e) {
    if (e.name === 'QuotaExceededError') {
      // Trim further and retry
      try { localStorage.setItem(SNAPSHOTS_KEY, JSON.stringify(snaps.slice(0, 2))); } catch {}
      toast('Storage nearly full — older snapshots trimmed', 'warning');
    }
  }
}

function loadSnapshots() {
  try { return JSON.parse(localStorage.getItem(SNAPSHOTS_KEY) || '[]'); } catch { return []; }
}

async function restoreSnapshot(ts) {
  const snaps = loadSnapshots();
  const snap  = snaps.find(s => s.ts === ts);
  if (!snap) { toast('Snapshot not found', 'error'); return; }

  const current = await dbCount();
  if (!confirm(`Restore ${snap.count} records? This replaces your current ${current} records.`)) return;

  await dbClear();
  await dbBulkPut(snap.data);
  toast(`Restored ${snap.count} records`, 'success');
  showView(DEFAULT_VIEW);
}

// ── Layer 2: Local File Auto-Backup ───────────────────────────────────────
let   _autoFileHandle = null;
let   _autoBackupTimer = null;
const L2_META_KEY      = 'YOUR_APP_l2_v1';

function isFileSystemSupported() { return typeof window.showSaveFilePicker === 'function'; }

async function linkBackupFile() {
  if (!isFileSystemSupported()) {
    toast('File backup requires Chrome, Edge, or Brave', 'error'); return;
  }
  try {
    _autoFileHandle = await window.showSaveFilePicker({
      suggestedName: 'YOUR_APP_backup.json',
      types: [{ description: 'JSON', accept: { 'application/json': ['.json'] } }]
    });
    localStorage.setItem(L2_META_KEY, JSON.stringify({ fileName: _autoFileHandle.name, lastBackup: null }));
    clearInterval(_autoBackupTimer);
    _autoBackupTimer = setInterval(runFileBackup, 30 * 60 * 1000);
    await runFileBackup();
    toast(`Linked to ${_autoFileHandle.name}`, 'success');
  } catch (e) {
    if (e.name !== 'AbortError') toast('Could not link file: ' + e.message, 'error');
  }
}

async function runFileBackup() {
  if (!_autoFileHandle) return;
  try {
    const all  = await dbGetAll();
    const json = JSON.stringify({ settings, records: all, backedUpAt: Date.now() }, null, 2);
    const w    = await _autoFileHandle.createWritable();
    await w.write(json); await w.close();
    const meta = JSON.parse(localStorage.getItem(L2_META_KEY) || '{}');
    meta.lastBackup = Date.now();
    localStorage.setItem(L2_META_KEY, JSON.stringify(meta));
  } catch (e) {
    toast('Auto-backup failed: ' + e.message, 'error');
  }
}

function unlinkBackupFile() {
  _autoFileHandle = null;
  clearInterval(_autoBackupTimer);
  localStorage.removeItem(L2_META_KEY);
  toast('File backup unlinked', 'info');
}
```

**Known bugs to avoid:**
- `AbortError` when user cancels the file picker dialog — catch and ignore, don't show an error toast.
- File handle does NOT persist across page reloads — store only the filename string (for UI) in localStorage.
- `clearInterval(_autoBackupTimer)` on unlink — otherwise the old timer keeps firing.
- Layer 1 `QuotaExceededError` — always catch, always trim further, never let it crash the app silently.

---

### C10 — Settings Panel

**What it does:** A form to configure scalar app settings (names, display options). Includes a sample data loader, a "clear all data" destructive action, and storage info.

```javascript
function loadSettingsForm() {
  // Populate form from settings object
  Object.keys(settings).forEach(key => {
    const el = document.getElementById(`setting-${key}`);
    if (el) el.value = settings[key] ?? '';
  });
  updateStorageInfo();
}

function saveSettingsForm(e) {
  if (e) e.preventDefault();
  Object.keys(settings).forEach(key => {
    const el = document.getElementById(`setting-${key}`);
    if (el) settings[key] = el.value.trim();
  });
  saveSettings();
  toast('Settings saved', 'success');
  // Apply any immediate effects (e.g., update header title)
  document.querySelector('#topbar span').textContent = settings.appName || 'YOUR_APP_NAME';
}

async function updateStorageInfo() {
  const count = await dbCount();
  const el    = document.getElementById('storage-info');
  if (el) el.textContent = `${count.toLocaleString()} records stored`;
}

// Double-confirm for destructive clear — NEVER use single confirm for this
function confirmClearAll() {
  if (!confirm('Delete ALL data? This cannot be undone.')) return;
  if (!confirm('Are you absolutely sure? Type OK to confirm.')) return;
  dbClear().then(() => {
    scheduleSnapshot();
    toast('All data cleared', 'info');
    showView(DEFAULT_VIEW);
  });
}

// Sample data loader — marks records with _sample: true so they can be cleared separately
async function loadSampleData(sampleRecords) {
  const tagged = sampleRecords.map(r => ({ ...r, id: newId(), _sample: true }));
  await dbBulkPut(tagged);
  scheduleSnapshot();
  toast(`Loaded ${tagged.length} sample records`, 'success');
  showView(DEFAULT_VIEW);
}

async function clearSampleData() {
  const all      = await dbGetAll();
  const toDelete = all.filter(r => r._sample);
  await Promise.all(toDelete.map(r => dbDelete(r.id)));
  scheduleSnapshot();
  toast(`Removed ${toDelete.length} sample records`, 'success');
}
```

---

### C11 — Toast Notifications + Undo

**What it does:** Dismissable notification pop-ups. Supports an optional Undo action (6-second window to restore deleted records).

```javascript
function toast(msg, type = 'info', opts = {}) {
  const container = document.getElementById('toast');
  const duration  = opts.duration || 3200;

  const el = document.createElement('div');
  el.style.cssText = `padding:12px 18px;border-radius:8px;font-size:14px;cursor:pointer;
    box-shadow:var(--shadow);display:flex;align-items:center;gap:10px;max-width:360px;
    ${type==='success' ? 'background:var(--success);color:#fff' :
      type==='error'   ? 'background:var(--danger);color:#fff'  :
      type==='warning' ? 'background:var(--warning);color:#000' :
                         'background:var(--surface2);color:var(--text);border:1px solid var(--border)'}`;

  // Use textContent (not innerHTML) — toast messages may contain user data
  const msgNode = document.createTextNode(msg);
  el.appendChild(msgNode);

  if (opts.action) {
    const btn = document.createElement('button');
    btn.textContent = opts.action.label;
    btn.style.cssText = 'background:rgba(255,255,255,.25);border:none;color:inherit;padding:2px 10px;border-radius:4px;cursor:pointer;font-weight:600;margin-left:4px';
    btn.onclick = () => { opts.action.onClick(); el.remove(); };
    el.appendChild(btn);
  }

  el.addEventListener('click', () => el.remove());
  container.appendChild(el);

  setTimeout(() => {
    el.style.opacity = '0';
    el.style.transition = 'opacity .3s';
    setTimeout(() => el.remove(), 300);
  }, duration);
}

// Undo system — 6-second window to restore deleted records
function offerUndo(label, deletedRecords) {
  // Clone before async operations can modify the originals
  const saved = deletedRecords.map(r => ({ ...r }));

  toast(label, 'info', {
    duration: 6000,
    action: {
      label:   'Undo',
      onClick: async () => {
        await dbBulkPut(saved);
        scheduleSnapshot();
        renderTable();
        toast('Restored', 'success');
      }
    }
  });
}
```

---

### C12 — Auth Gate (Optional)

**What it does:** A sign-in screen that blocks access until the user authenticates. Skip entirely for public or personal apps.

```javascript
const AUTH_KEY     = 'YOUR_APP_auth_v1';
const SESSION_TTL  = 24 * 60 * 60 * 1000; // 24 hours
let   authUser     = null;

function checkAuthSession() {
  try {
    const raw  = localStorage.getItem(AUTH_KEY);
    if (!raw) { showAuthGate(); return; }
    const sess = JSON.parse(raw);
    if (Date.now() - sess.ts > SESSION_TTL) { showAuthGate(); return; }
    authUser = sess;
    bootApp();
  } catch { showAuthGate(); }
}

function cacheSession(user) {
  authUser = { ...user, ts: Date.now() };
  localStorage.setItem(AUTH_KEY, JSON.stringify(authUser));
}

function signOut() {
  localStorage.removeItem(AUTH_KEY);
  authUser = null;
  showAuthGate();
}

function showAuthGate() {
  document.querySelectorAll('.view').forEach(v => v.style.display = 'none');
  document.getElementById('auth-gate').style.display = 'flex';
}

function bootApp() {
  document.getElementById('auth-gate').style.display = 'none';
  showView(DEFAULT_VIEW);
}

// Verify against Supabase (or your own API)
async function verifyCredentials(email, key) {
  const SUPA_URL = 'https://YOUR_PROJECT.supabase.co';
  const SUPA_KEY = 'YOUR_ANON_KEY'; // protected by RLS

  const res = await fetch(
    `${SUPA_URL}/rest/v1/YOUR_USERS_TABLE?email=eq.${encodeURIComponent(email)}&select=*`,
    { headers: { 'apikey': SUPA_KEY, 'Authorization': `Bearer ${SUPA_KEY}` } }
  );
  if (!res.ok) throw new Error('Cannot connect to auth server');
  const rows = await res.json();
  if (!rows.length) throw new Error('No account found for this email');
  const user = rows[0];
  if (user.license_key !== key) throw new Error('Invalid license key');
  return user;
}
```

---

### C13 — Theme Toggle

```javascript
const THEME_KEY = 'YOUR_APP_theme';

function applyTheme() {
  const saved = localStorage.getItem(THEME_KEY) || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = saved === 'dark' ? '☀️' : '🌙';
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next    = current === 'dark' ? 'light' : 'dark';
  localStorage.setItem(THEME_KEY, next);
  document.documentElement.setAttribute('data-theme', next);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
  if (typeof retintCharts === 'function') retintCharts(); // update charts if C03 included
}
```

---

### C14 — Keyboard Shortcuts

```javascript
// ── CONFIGURE: define your shortcuts ─────────────────────────────────────
const SHORTCUTS = {
  'n': () => showView('YOUR_ADD_VIEW'),   // n = new record
  '/': () => document.getElementById('search-input')?.focus(),
  '?': toggleShortcutsHelp,
};

// Two-key shortcuts (press g then a key)
const G_SHORTCUTS = {
  'h': () => showView('YOUR_MAIN_VIEW'),
  'l': () => showView('YOUR_LIST_VIEW'),
  's': () => showView('YOUR_SETTINGS'),
  // Add your views here
};
// ─────────────────────────────────────────────────────────────────────────

let _gKeyActive = false;

document.addEventListener('keydown', e => {
  // Skip when typing in inputs
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;

  const key = e.key.toLowerCase();

  if (e.key === 'Escape') { closeAllModals(); return; }

  if (_gKeyActive) {
    _gKeyActive = false;
    if (G_SHORTCUTS[key]) { G_SHORTCUTS[key](); }
    return;
  }

  if (key === 'g') { _gKeyActive = true; return; }
  if (SHORTCUTS[key]) SHORTCUTS[key]();
});

function closeAllModals() {
  document.querySelectorAll('[id$="-modal"]').forEach(m => m.style.display = 'none');
}
```

---

### C15 — PWA / Offline Support

**manifest.json** — place in your project root:
```json
{
  "name": "YOUR APP NAME",
  "short_name": "YOUR APP",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#0f1117",
  "background_color": "#0f1117",
  "icons": [
    { "src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ],
  "shortcuts": [
    { "name": "Add Record",  "url": "/?action=add",  "description": "Quickly add a new record" },
    { "name": "View All",    "url": "/?action=list", "description": "See all records"           }
  ]
}
```

**service-worker.js** — handles URL shortcut actions and offline caching:
```javascript
const CACHE = 'YOUR_APP_v1';
const CORE  = ['/', '/index.html', '/manifest.json', '/icon-192.png', '/icon-512.png'];

self.addEventListener('install',  e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  // Bypass API calls — never cache network requests to external services
  if (e.request.url.includes('supabase.co') || e.request.url.includes('googleapis.com')) return;
  e.respondWith(caches.match(e.request).then(cached => cached || fetch(e.request).then(res => {
    if (res.ok) caches.open(CACHE).then(c => c.put(e.request, res.clone()));
    return res;
  })));
});
```

**Register in app HTML:**
```javascript
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('/service-worker.js'));
}

// Handle PWA shortcuts (?action=add, ?action=list, etc.)
window.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(location.search);
  const action = params.get('action');
  if (action === 'add')  showView('YOUR_ADD_VIEW');
  if (action === 'list') showView('YOUR_LIST_VIEW');
});
```

---

### C16 — Data Export

```javascript
// Export all records as CSV
async function exportCSV(filename = 'export') {
  const records = await dbGetAll();
  if (!records.length) { toast('No records to export', 'info'); return; }

  // ── CONFIGURE: define your CSV columns ──────────────────────────────────
  const CSV_COLUMNS = [
    { header: 'Name',        value: r => r.name        || '' },
    { header: 'Category',    value: r => r.category    || '' },
    { header: 'Date',        value: r => r.date        || '' },
    { header: 'Description', value: r => r.description || '' },
    // Add your columns here
  ];
  // ────────────────────────────────────────────────────────────────────────

  const lines = [
    CSV_COLUMNS.map(c => `"${c.header}"`).join(','),
    ...records.map(r =>
      CSV_COLUMNS.map(c => `"${String(csvSanitize(c.value(r))).replace(/"/g, '""')}"`).join(',')
    )
  ];

  downloadBlob(lines.join('\n'), `${filename}_${Date.now()}.csv`, 'text/csv;charset=utf-8;');
}

// Export all records as JSON backup
async function exportJSON(filename = 'backup') {
  const records = await dbGetAll();
  const payload = JSON.stringify({ settings, records, exportedAt: new Date().toISOString() }, null, 2);
  downloadBlob(payload, `${filename}_${Date.now()}.json`, 'application/json');
}

// Import JSON backup
async function importJSON(file) {
  try {
    const data = JSON.parse(await file.text());
    if (!Array.isArray(data.records)) { toast('Invalid backup file', 'error'); return; }
    if (!confirm(`Import ${data.records.length} records? Duplicates (same ID) will be skipped.`)) return;
    const existingIds = new Set((await dbGetAll()).map(r => r.id));
    const toImport    = data.records.filter(r => !existingIds.has(r.id));
    await dbBulkPut(toImport);
    scheduleSnapshot();
    toast(`Imported ${toImport.length} new records`, 'success');
    renderTable();
  } catch { toast('Could not read backup file', 'error'); }
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), { href: url, download: filename });
  a.click();
  URL.revokeObjectURL(url);
}
```

---

## PART 3 — DOMAIN ADAPTATION GUIDE

**How to apply this blueprint to any new app in 6 steps:**

---

### Step 1 — Define Your Record

Replace the P&L `Transaction` with your own shape. Every record **must** have `id`. Everything else is your choice.

```javascript
// EXAMPLES for different app types:

// Task Manager
const Record = { id, title, status, priority, due_date, assignee, tags, created_at };

// Inventory Tracker
const Record = { id, sku, name, quantity, unit_price, category, location, last_updated };

// Client CRM
const Record = { id, name, email, company, status, next_followup, notes, created_at };

// Event Logger
const Record = { id, event_type, description, severity, source, timestamp };

// Recipe Book
const Record = { id, name, cuisine, prep_time, difficulty, ingredients, instructions };
```

**Rules for any record shape:**
- `id` = always `newId()` (float: `Date.now() + Math.random()`)
- Date fields = always `"YYYY-MM-DD"` strings (ISO format)
- Numeric fields = always store as numbers, always positive (use a separate field for sign if needed)
- Text fields = stored raw in DB; `escapeHtml()` applied at render time

---

### Step 2 — Configure the DB Schema

```javascript
// Change these at the top of your script
const DB_NAME    = 'TaskManagerDB';
const STORE_NAME = 'tasks';
const DB_INDEXES = [
  { name: 'status',   keyPath: 'status'   },
  { name: 'due_date', keyPath: 'due_date' },
  { name: 'priority', keyPath: 'priority' },
];

// Configure search fields (what gets searched when user types in the search box)
const SEARCH_FIELDS = ['title', 'assignee', 'tags', 'description'];
```

---

### Step 3 — Configure the Table

```javascript
const TABLE_COLUMNS = [
  { key: 'title',    label: 'Task',     sortable: true,  render: r => escapeHtml(r.title) },
  { key: 'status',   label: 'Status',   sortable: true,  render: r => `<span class="badge badge-primary">${escapeHtml(r.status)}</span>` },
  { key: 'priority', label: 'Priority', sortable: true,  render: r => escapeHtml(r.priority) },
  { key: 'due_date', label: 'Due',      sortable: true,  render: r => escapeHtml(r.due_date) },
  { key: '_actions', label: '',         sortable: false, render: r => `<button onclick="deleteRecord(${JSON.stringify(r.id)})">🗑</button>` },
];

const TABLE_FILTERS = [
  { key: 'status',   label: 'Status',   options: ['open', 'in-progress', 'done'] },
  { key: 'priority', label: 'Priority', options: ['low', 'medium', 'high']       },
];
```

---

### Step 4 — Configure the Add Form

```javascript
const FORM_FIELDS = [
  { id: 'f-title',    key: 'title',    required: true,  transform: v => v.trim()       },
  { id: 'f-status',   key: 'status',   required: false, transform: v => v || 'open'    },
  { id: 'f-priority', key: 'priority', required: false, transform: v => v || 'medium'  },
  { id: 'f-due',      key: 'due_date', required: false, transform: v => v              },
  { id: 'f-notes',    key: 'description', required: false, transform: v => v.trim()    },
];

const FORM_VALIDATORS = [
  ({ title }) => !title ? 'Title is required' : null,
];
```

---

### Step 5 — Configure KPI Cards

```javascript
const KPI_METRICS = [
  { id: 'kpi-total',    label: 'Total Tasks',   compute: r => r.length,                               format: v => v, color: () => 'var(--text)' },
  { id: 'kpi-open',     label: 'Open',          compute: r => r.filter(t => t.status==='open').length, format: v => v, color: v => v>0?'var(--warning)':'var(--muted)' },
  { id: 'kpi-done',     label: 'Completed',     compute: r => r.filter(t => t.status==='done').length, format: v => v, color: v => v>0?'var(--success)':'var(--muted)' },
  { id: 'kpi-overdue',  label: 'Overdue',       compute: r => r.filter(t => t.due_date && t.due_date < new Date().toISOString().slice(0,10) && t.status!=='done').length, format: v => v, color: v => v>0?'var(--danger)':'var(--muted)' },
];
```

---

### Step 6 — Configure Navigation

```javascript
const DEFAULT_VIEW = 'dashboard';

const VIEW_RENDERERS = {
  'dashboard':  () => { renderKPICards(); renderBarChart(); },
  'task-list':  () => renderTable({ page: 1 }),
  'add-task':   initAddForm,
  'settings':   loadSettingsForm,
};

const MOBILE_NAV = [
  { view: 'dashboard', label: 'Home',  icon: '🏠' },
  { view: 'task-list', label: 'Tasks', icon: '📋' },
  { view: 'add-task',  label: 'Add',   icon: '+',  fab: true },
  { view: 'settings',  label: 'Setup', icon: '⚙️' },
];
```

---

## PART 4 — AUDIT PLAN

### Foundation Audit (run first, on every new app)

```
[ ] App loads in Chrome without console errors
[ ] App loads in Firefox without console errors  
[ ] App loads in Safari without console errors
[ ] Reload after adding a record — record persists (IndexedDB working)
[ ] Open in private/incognito — shows "Storage Unavailable" message (not blank)
[ ] Settings save and reload correctly after page refresh
[ ] Theme preference persists after reload (dark/light)
[ ] escapeHtml('<script>alert(1)</script>') returns '&lt;script&gt;alert(1)&lt;/script&gt;'
[ ] csvSanitize('=SUM(A1)') returns "'=SUM(A1)"
[ ] newId() called 1000 times produces 1000 unique values (verify with Set)
```

### Component Audits

**C02 KPI Cards:**
```
[ ] Cards show correct values (verify manually with known test data)
[ ] No divide-by-zero when denominator is 0 (e.g. no records → 0%, not NaN%)
[ ] Cards update after adding a record and navigating back
[ ] Cards with color logic show correct color (e.g. red when overdue)
```

**C03 Charts:**
```
[ ] All charts render without JS errors on first load
[ ] Charts update after adding data and revisiting the view
[ ] Toggle theme dark→light → charts re-render with correct colors
[ ] No chart created when data array is empty (no broken empty circle)
[ ] Chart tooltips show formatted values
```

**C04 Table:**
```
[ ] Search "xyz" → only matching rows shown
[ ] Clear search → all rows return
[ ] Pagination: "Showing 1–25 of 100" is accurate
[ ] Next/Prev/First/Last buttons work correctly
[ ] Last page: Next and Last buttons are disabled
[ ] Click column header → sorts ascending; click again → descending
[ ] Sort persists when changing page
[ ] Filter dropdown → shows only matching records
[ ] XSS test: add record with name "<script>alert(1)</script>" → renders as text, no alert
```

**C05 Add Form:**
```
[ ] Submit empty form → shows validation error
[ ] Submit with required field missing → specific error shown
[ ] Submit valid data → record appears in table, form resets
[ ] Date field defaults to today
[ ] Press Enter in a form field → submits (if wired up)
[ ] Recently added list updates after submit
[ ] Rapid entry: add 10 records quickly → all 10 saved (no ID collisions)
```

**C06 Bulk Select + Undo:**
```
[ ] Select 3 checkboxes → bulk bar shows "3 selected"
[ ] Select all → all visible rows selected
[ ] Delete selected → rows removed from DB (not just hidden in UI)
[ ] Undo toast appears for 6 seconds
[ ] Click Undo within 6s → rows restored and visible
[ ] Let Undo expire (7s) → rows not restored
[ ] Selection cleared after bulk delete
[ ] Selection cleared after switching views
```

**C07 CSV Import:**
```
[ ] Upload CSV with 10 rows → mapping modal opens with preview
[ ] Auto-guess detects column headers correctly
[ ] Cancel → nothing imported
[ ] Import → records appear in table
[ ] Import same file twice → no duplicates (dedup working)
[ ] CSV with field containing comma inside quotes → parses correctly
[ ] CSV with formula "=SUM(A1)" in a field → imported as text, not formula
[ ] Large file > 500KB → UI does not freeze during parse (Web Worker used)
[ ] Required field not mapped → error message shown, modal stays open
[ ] File with only headers (no data rows) → "no valid rows" error
```

**C08 Tags:**
```
[ ] Add tag → appears in list and in form autocomplete
[ ] Add duplicate tag (case-insensitive) → error shown, not added
[ ] Add tag with XSS payload → rendered as escaped text, no JS executes
[ ] Rename tag → all records with old tag updated
[ ] Delete tag → all records relabeled "Uncategorized"
[ ] Tags persist after page reload
```

**C09 Backup:**
```
[ ] Add record → snapshot auto-created after ~3 seconds
[ ] Maximum 5 snapshots kept (older discarded)
[ ] Restore snapshot → confirm dialog shown (shows current count vs snapshot count)
[ ] Restore → data replaced with snapshot data
[ ] File backup (Chrome): link file → backup file created
[ ] File backup: Firefox → shows "requires Chrome/Edge" message, not an error
[ ] Cancel file picker dialog → no error toast shown
[ ] After 30 minutes with file linked → file auto-updated
```

**C10 Settings:**
```
[ ] Save app name → appears in header/sidebar immediately
[ ] Settings persist after reload
[ ] Clear all data → requires TWO confirms
[ ] Clear all data → DB wiped, redirected to main view
[ ] Cancel on first or second confirm → no data deleted
[ ] Load sample data → records appear, tagged _sample:true
[ ] Clear sample data → only _sample records removed, real data untouched
```

**C11 Toasts:**
```
[ ] Success toast → correct color
[ ] Error toast → correct color
[ ] Toast auto-dismisses after ~3 seconds
[ ] Click toast → dismisses immediately
[ ] Multiple toasts → stack vertically
[ ] Undo toast stays 6 seconds (not 3)
[ ] Mobile: toasts appear above bottom nav bar
```

**C13 Theme:**
```
[ ] Toggle switches dark ↔ light
[ ] Theme persists after reload
[ ] All text readable in both themes (no invisible text)
[ ] Charts re-render with correct colors after toggle
```

**C15 PWA:**
```
[ ] manifest.json accessible at /manifest.json (no 404)
[ ] App installs in Chrome (install icon in address bar)
[ ] Installed app opens in standalone mode (no browser chrome)
[ ] Offline: disconnect internet, reload → app still loads
[ ] Offline: add record → saves to IndexedDB (no server needed)
[ ] PWA shortcuts appear (long-press icon on Android)
```

**C16 Export:**
```
[ ] Export CSV → file downloads
[ ] Open exported CSV in Excel → all data present, correct
[ ] Description containing "=SUM(A1)" → exported as "'=SUM(A1)" (formula blocked)
[ ] Export JSON → valid JSON with records array
[ ] Import JSON backup → records added (no duplicates by ID)
```

---

### End-to-End Smoke Test (Run Before Every Release)

```
1. Open app fresh (clear all browser data first)
2. Verify empty state shown
3. Go to Settings → set app name, save → verify name appears in header
4. Go to Add → add 3 records with valid data
5. Go to main list → verify 3 records appear
6. Search for one record by name → verify only that record shown
7. Clear search → all 3 records return
8. Sort by a column → verify order changes
9. Select 2 records → bulk bar shows "2 selected" → delete → undo → verify restored
10. Go to Import → upload a 5-row CSV → map columns → import → verify 5 records added
11. Export CSV → verify file downloads, open it, verify data correct
12. Toggle theme → app switches correctly, charts update
13. Go to Backup → verify snapshot was auto-created → restore snapshot
14. Reload page → all data and settings still present
15. Open in mobile viewport (375px) → bottom nav visible, layout usable

PASS: All 15 steps complete without errors or console warnings.
```

---

## PART 5 — COMMON BUGS PREVENTION TABLE

| Bug | Cause | Prevention |
|-----|-------|-----------|
| XSS — script executes in table cell | `innerHTML` used with raw user data | `escapeHtml()` on every user string in every `render()` function |
| XSS — script executes in toast | `innerHTML` or string concat used for toast message | Use `document.createTextNode(msg)` in toast, never `innerHTML` |
| CSV formula injection | `=SUM(...)` in description field opens in Excel | `csvSanitize()` on every cell in every export |
| Float display error (`$0.30000000000000004`) | Raw floating-point arithmetic | `Math.round(x * 100) / 100` before any display |
| Date off by one day | `new Date("2025-01-15")` = UTC midnight → displays as Jan 14 in UTC-5 | Parse as `[y,m,d] = date.split('-').map(Number)` — no Date constructor |
| Duplicate chart canvas error | `new Chart()` on canvas that already has a chart | Always `destroyChart(key)` before `new Chart()` |
| Search stuck on wrong page | Search fires but `page` stays at 5 | Always reset `page = 1` when search or filter changes |
| Duplicate record IDs on import | Sequential counter reset on each reload | Always use `newId()` = `Date.now() + Math.random()` |
| IndexedDB silent failure | `onerror` only logs to console | Show user-visible error UI in `req.onerror` — never just `console.error` |
| localStorage quota crash | Too many/large snapshots | Catch `QuotaExceededError`, trim, retry, warn user |
| Stale bulk selection after delete | `selectedIds` Set not cleared | `selectedIds.clear()` after every bulk operation |
| Undo restores wrong data | Deleted array mutated before undo fires | Clone before deleting: `saved = records.map(r => ({...r}))` |
| Tag rename misses some records | Wrong field name in propagation query | Double-check field name (`r.category`, `r.tag`, etc.) matches your record schema |
| Chart blank when view not visible | Chart.js renders to 0px container | Only call `renderChart()` inside `VIEW_RENDERERS` — never on app load |
| File picker cancel shows error | `AbortError` not caught separately | `if (e.name !== 'AbortError') toast(...)` |
| File backup lost after reload | FileSystemFileHandle not serializable | Store only filename string in localStorage for UI — handle must be re-linked |
| Auth session never expires | No TTL check on cached session | Always check `Date.now() - sess.ts > SESSION_TTL` before trusting cache |
| PWA install prompt in standalone | Already installed but still showing prompt | Check `window.matchMedia('(display-mode: standalone)').matches` first |
| CSV BOM corrupts first header | Excel exports UTF-8 BOM (`﻿`) | `text.replace(/^﻿/, '')` before parsing |
| CSV quoted field with embedded `""` | Parser treats `""` as end of field | RFC 4180: if `inQuotes && ch==='"' && nextCh==='"'`, append `"` and skip both |

---

## APPENDIX — P&L DASHBOARD REFERENCE IMPLEMENTATION

The P&L Dashboard (`pl-dashboard-v8.html`) uses all components in this blueprint. Here is how it maps each component to financial concepts — use as a concrete example when implementing financial apps.

| Component | P&L Implementation | Your App Could Use It For |
|-----------|-------------------|--------------------------|
| **F0 DB Schema** | `{ id, date, type, category, description, amount, month, year }` | Any record with dates + numeric fields |
| **C02 KPI Cards** | Revenue, Expenses, Net Profit, Margin %, Avg Monthly Revenue, Gross Profit | Sales totals, task counts, inventory value |
| **C03 Bar Chart** | Revenue vs Expenses by month | Any two metrics over time |
| **C03 Line Chart** | Net Profit trend by month | Any single metric trend |
| **C03 Pie Charts** | Revenue by Category, Expenses by Category | Record breakdown by any grouping field |
| **C04 Table** | All Transactions (date, type, category, description, amount) | Any list of records |
| **C04 Filters** | Year, Month, Type (Revenue/Expense) | Status, date range, category |
| **C05 Add Form** | Date, Type toggle, Category, Amount, Description | Any record creation form |
| **C05 Autocomplete** | Category name from past transactions | Tags, labels, names from history |
| **C08 Tags** | Revenue categories + Expense categories, industry templates | Task tags, product categories, client types |
| **C09 Snapshots** | Auto-snapshot after every transaction add/edit/delete | Universal — use verbatim |
| **C10 Settings** | Business name, fiscal year, currency symbol | Any app-level config |
| **C16 Export CSV** | Date, Type, Category, Description, Amount, Month, Year | Any tabular data |

**P&L-specific logic NOT in this blueprint** (only needed for financial apps):
- COGS detection via keyword matching on category name
- Fiscal year filtering (non-calendar year support)
- Accounting format parsing `(1,234.56)` = negative
- Currency symbol in KPI cards
- Monthly P&L rollup table (revenue vs expenses per month)
- Net Profit = Revenue total − Expense total (type-based sum)

These patterns exist in the reference implementation at `pl-dashboard-v8.html` but are intentionally excluded from this universal blueprint because they are domain-specific.
