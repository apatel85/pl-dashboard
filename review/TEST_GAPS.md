# TEST_GAPS.md — pl-dashboard-v8.html

**Date:** 2026-05-15  
**Scope:** What could not be verified by static analysis and Python simulation alone

---

## What Could Not Be Verified Without a Browser

| Area | Gap | Risk if Wrong |
|---|---|---|
| XSS execution | innerHTML injection confirmed by code inspection; actual JS execution requires a live browser | Medium — code inspection gives high confidence |
| Toast aria-live | `role="status"` present in HTML; whether screen readers announce dynamically-added toast elements requires NVDA/VoiceOver | Low |
| Modal focus trapping | Modals lack `role="dialog"`; whether focus actually escapes the modal requires keyboard testing | Low |
| Service worker update prompt | Whether users see the update banner when a new SW version is waiting | Medium |
| IndexedDB private mode | Whether the error page renders correctly in Firefox/Safari private browsing | Low |
| OAuth token expiry | Whether a 401 from Sheets API correctly clears the token and triggers re-auth UI | Medium |
| Layer 2 (File System Access API) | Whether periodic file writes succeed and fail gracefully on permission revoke | Low |
| Web Worker CSV parse | Whether the background-thread CSV parsing actually keeps the UI responsive during large imports | Low |
| Duplicate detection accuracy | Whether `txnHash()` correctly deduplicates when amounts have float drift | Medium |
| Monthly table visual alignment | Whether the 6-col header + 5-col data mismatch is user-visible vs browser-autocorrected | High — browsers may silently reflow |
| Keyboard shortcuts | Whether all shortcuts work without conflicting with browser or OS hotkeys | Low |

---

## Suggested Manual Test Steps

### Critical path (before every release)

1. Open app in Chrome Incognito → verify IndexedDB error page appears with helpful message
2. Add 3 revenue + 2 expense transactions → navigate to Monthly P&L → confirm:
   - 6 columns displayed
   - "Gross Profit" column shows correct value (not the same as Net Profit)
   - "Margin %" column is not blank
3. Export CSV → open in text editor → verify categories/descriptions starting with `=`, `+`, `-`, `@` are prefixed with `'`
4. Export XLSX → open in Excel → verify no formula executes on open
5. Import CSV with XSS payload in description (`<img src=x onerror=alert(1)>`) → confirm no dialog fires in any tab
6. Open "What's New" modal → confirm all text is plain text (no HTML rendered as HTML)
7. Sign in with Google → verify welcome name is plain text in auth panel
8. Version check: trigger manually → verify banner shows plain text version number

### Google Auth path

9. Sign in → verify welcome message shows escaped name
10. Create a Supabase row with `name = '<img src=x onerror=alert(1)>'` → sign in → confirm no alert
11. Trigger auth denial → confirm email displays as plain text in error message
12. Trigger cloud restore → verify spreadsheet name displays as plain text in restore panel

### Service worker

13. Load app → DevTools → Application → Service Workers → confirm registered version matches `APP_VERSION`
14. Simulate update: bump `CACHE_VERSION` in `service-worker.js` → reload → verify update banner appears

### Accessibility

15. Tab through app with keyboard only → confirm all interactive elements are reachable
16. Open confirm modal with keyboard → confirm Tab is trapped inside the modal
17. Dismiss modal → confirm focus returns to the trigger element
18. Trigger toast → confirm VoiceOver/NVDA announces the message

### Performance

19. Import 1,000 rows via CSV → navigate to Revenue tab → confirm render completes in < 1s
20. Import 10,000 rows → navigate to Revenue tab → time the render (target < 2s)
21. With 10,000 rows: open Backup tab → check snapshot list → verify no storage warning fires

---

## Suggested Playwright Test Cases

```js
// Additions to tests/e2e.spec.js

test('XSS: imported description does not execute in any view', async ({ page }) => {
  let alerted = false;
  page.on('dialog', d => { alerted = true; d.dismiss(); });
  await importCSV(page, [[
    '2025-01-01', 'revenue', '<img src=x onerror=alert(1)>',
    '<script>alert(2)</script>', '500'
  ]]);
  await page.click('[data-view="revenue-view"]');
  await page.click('[data-view="expenses-view"]');
  await page.click('[data-view="dashboard-view"]');
  await page.waitForTimeout(500);
  expect(alerted).toBe(false);
});

test('Monthly table: 6 data columns match 6 headers', async ({ page }) => {
  await addTransaction(page, { date:'2025-01-15', type:'revenue', amount:1000 });
  await addTransaction(page, { date:'2025-01-20', type:'expense', amount:300, category:'Cost of Goods Sold (COGS)' });
  await page.click('[data-view="monthly-view"]');
  const headerCells = await page.$$('#monthly-table thead th');
  const dataCells   = await page.$$('#monthly-tbody tr:first-child td');
  expect(headerCells.length).toBe(dataCells.length);
  expect(headerCells.length).toBe(6);
  const grossProfitVal = await dataCells[3].textContent();
  expect(grossProfitVal.trim()).toMatch(/\$[\d,]+\.\d{2}/);
  const marginVal = await dataCells[5].textContent();
  expect(marginVal.trim()).toMatch(/[\d.]+%/);
});

test('XLSX export: category formula prefixed', async ({ page }) => {
  await addTransaction(page, {
    date: '2025-01-15', type: 'revenue',
    category: '=HYPERLINK("http://evil.com","CLICK")',
    amount: 100
  });
  const [ download ] = await Promise.all([
    page.waitForEvent('download'),
    page.click('#btn-export-xlsx')
  ]);
  const path = await download.path();
  // Parse with xlsx and verify category cell starts with apostrophe prefix
  // or does not begin with '='
});

test('Changelog XSS: version.json payload is escaped', async ({ page }) => {
  await page.route('**/version.json', route => route.fulfill({
    contentType: 'application/json',
    body: JSON.stringify({
      latest_version: '9.0.0<script>alert(1)</script>',
      minimum_version: '1.0.0',
      release_notes: [{
        version: '9.0.0',
        date: '2026-01-01',
        title: '<img src=x onerror=alert(2)>',
        summary: '<img src=x onerror=alert(3)>',
        changes: [{ type: 'new', text: '<img src=x onerror=alert(4)>' }]
      }]
    })
  }));
  let alerted = false;
  page.on('dialog', d => { alerted = true; d.dismiss(); });
  await page.waitForTimeout(1000);
  await page.click('#btn-changelog');
  await page.waitForTimeout(500);
  expect(alerted).toBe(false);
  const body = await page.textContent('#changelog-body');
  expect(body).toContain('<img');  // escaped as text, not executed
});

test('Auth XSS: Supabase name with payload is escaped', async ({ page }) => {
  // Mock the Supabase auth response with XSS payload in name
  await page.route('**/pl_licensed_users*', route => route.fulfill({
    contentType: 'application/json',
    body: JSON.stringify([{
      email: 'test@example.com',
      name: '<img src=x onerror=alert(1)>',
      plan: 'pro',
      google_sub: 'test-sub'
    }])
  }));
  let alerted = false;
  page.on('dialog', d => { alerted = true; d.dismiss(); });
  // Trigger auth flow
  await page.evaluate(() => window.showAuthSuccess({
    name: '<img src=x onerror=alert(1)>',
    plan: 'pro',
    email: 'test@example.com'
  }));
  await page.waitForTimeout(300);
  expect(alerted).toBe(false);
  const msg = await page.textContent('#auth-success-msg');
  expect(msg).toContain('<img');  // visible as text, not parsed
});

test('Confirm modal has role=dialog', async ({ page }) => {
  await page.evaluate(() => window.showConfirm('Test', 'Test message', () => {}));
  const role = await page.$eval('#confirm-modal', el => el.getAttribute('role'));
  expect(role).toBe('dialog');
  const ariaModal = await page.$eval('#confirm-modal', el => el.getAttribute('aria-modal'));
  expect(ariaModal).toBe('true');
});
```

---

## Suggested Regression Suite (post-fix)

Run after applying any Tier 1 or Tier 2 fix to confirm no breakage:

| Test | Verifies |
|---|---|
| Import 100-row CSV → KPI totals match Python reference | parseAmount / KPI aggregation |
| Import EU-format CSV (1.234,56) → amounts correct | EU number parsing |
| Import accounting-negative CSV (500.00) → amounts negative | Accounting format |
| Add transaction, delete, click Undo → transaction restored | Undo registry |
| Import 5,000 rows → Revenue tab renders < 2s | Pagination performance |
| Import 5,000 rows → Expense tab renders < 2s | Pagination (separate call) |
| Snapshot after 1,000 rows → localStorage under 5 MB | Snapshot size budget |
| Export JSON → import JSON → row counts match | Round-trip fidelity |
| Category with `&`, `<`, `>`, `"` in name → displays correctly in all dropdowns | HTML escaping regression |
| Monthly table with COGS transactions → Gross Profit ≠ Net Profit | Monthly calc fix |
