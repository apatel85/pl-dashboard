# TEST_GAPS.md — pl-dashboard-v8.html

**Date:** 2026-05-15  
**Scope:** What could not be verified by static analysis alone

---

## What Could Not Be Verified Without a Browser

| Area | Gap | Risk |
|---|---|---|
| XSS execution | innerHTML injection was confirmed by code inspection; actual JS execution requires a browser | Medium — inspection is sufficient for High confidence |
| Toast aria-live | role="status" is present in HTML; whether screen readers announce toasts requires NVDA/VoiceOver | Low |
| Focus trapping | Modals lack role=dialog; whether focus actually escapes requires keyboard testing | Low |
| Service worker update flow | Whether users see the update prompt when a new version deploys | Medium |
| IndexedDB private mode | Whether the error page renders correctly in Firefox/Safari private mode | Low |
| OAuth token expiry | Whether a 401 from Sheets API correctly clears the token and shows re-auth prompt | Medium |
| Layer 2 auto-backup (File System API) | Whether file writes succeed and fail gracefully on Chrome/Edge | Low |
| Duplicate detection accuracy | Whether txnHash dedup correctly handles float-imprecise amounts | Medium |
| Import progress bar accuracy | Whether the Web Worker progress events match actual parse progress | Low |
| Keyboard shortcuts | Whether all shortcuts work without conflicting with browser hotkeys | Low |

---

## Suggested Manual Test Steps

### Critical path (before every release)
1. Open app in Chrome Incognito → verify IndexedDB error page appears
2. Add 3 transactions → navigate to Monthly P&L → confirm 6 columns show correct data
3. Export CSV → open in text editor → verify no `=`, `+`, `-` formulas in category/description without leading apostrophe
4. Export XLSX → open in Excel → verify no formula execution
5. Import CSV with XSS payload in description (`<img src=x onerror=alert(1)>`) → confirm no alert fires
6. Open "What's New" modal → confirm all text displays as plain text

### Google Auth path
7. Sign in → verify welcome message shows plain text name
8. Deny auth → verify error message shows escaped email
9. Trigger cloud restore → verify sheet name displays as plain text in restore panel

### Service worker
10. Load app → DevTools → Application → Service Workers → confirm version matches

### Accessibility
11. Tab through app with keyboard only → confirm all interactive elements reachable
12. Open confirm modal with keyboard → confirm Tab is trapped inside
13. Trigger toast → confirm VoiceOver announces it

---

## Suggested Playwright Test Cases

```js
// tests/e2e.spec.js additions

test('XSS: imported category does not execute', async ({ page }) => {
  // Import CSV with <img src=x onerror=alert(1)> as category
  let alerted = false;
  page.on('dialog', () => { alerted = true; });
  await importCSV(page, [
    ['2025-01-01', 'revenue', '<img src=x onerror=alert(1)>', 'Test', '100']
  ]);
  await page.waitForTimeout(500);
  expect(alerted).toBe(false);
});

test('Monthly table: 6 columns have data', async ({ page }) => {
  await addTransaction(page, { date:'2025-01-15', type:'revenue', amount:1000 });
  await addTransaction(page, { date:'2025-01-20', type:'expense', amount:300 });
  await page.click('[data-view="monthly-view"]');
  const cells = await page.$$('#monthly-tbody tr:first-child td');
  expect(cells.length).toBe(6);
  const grossProfit = await cells[3].textContent();
  expect(grossProfit).toMatch(/\$[\d,]+/);  // should have a value, not be empty
});

test('XLSX export: formula injection prefixed', async ({ page }) => {
  await addTransaction(page, { 
    date:'2025-01-15', type:'revenue', 
    category: '=HYPERLINK("http://evil.com","Click")',
    amount: 100 
  });
  const download = await triggerDownload(page, '#btn-export-xlsx');
  // Parse and verify category cell starts with apostrophe
});

test('Changelog modal: version.json XSS escaped', async ({ page }) => {
  await page.route('**/version.json', route => route.fulfill({
    body: JSON.stringify({
      latest_version: '9.0.0<script>alert(1)</script>',
      release_notes: [{ version:'9.0.0', title:'<img src=x onerror=alert(1)>', changes:[] }]
    })
  }));
  let alerted = false;
  page.on('dialog', () => { alerted = true; });
  await page.click('#btn-changelog');
  await page.waitForTimeout(300);
  expect(alerted).toBe(false);
});

test('Confirm modal: has role=dialog', async ({ page }) => {
  await page.click('#btn-clear-all');
  const role = await page.$eval('#confirm-modal', el => el.getAttribute('role'));
  expect(role).toBe('dialog');
});
```

---

## Suggested Regression Suite

After applying Tier 1 fixes, run these regressions to confirm no breakage:

| Test | Verifies |
|---|---|
| Import 100-row CSV → KPI totals match Python reference | parseAmount / KPI aggregation |
| Import EU-format CSV (1.234,56) → amounts correct | EU number parsing |
| Import accounting-negative CSV → amounts negative | Accounting format |
| Add transaction, delete, undo → transaction restored | Undo registry |
| Import 5,000 rows → Revenue tab renders < 2s | Pagination performance |
| Import 5,000 rows → Expense tab renders < 2s | Same |
| Snapshot after 1,000 rows → localStorage under 5 MB | Snapshot size |
| Export JSON → import JSON → counts match | Round-trip fidelity |
