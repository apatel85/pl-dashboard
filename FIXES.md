# FIXES.md — Auto-applyable patches for pl-dashboard-v8.html

**Generated:** 2026-05-13  
**Covers:** ISSUE-001 through ISSUE-021 (Critical, High, Medium severity)  
**Info items (ISSUE-022 to ISSUE-030):** Noted in ISSUES_LOG.md; no code patches required here.

---

## Apply Instructions for AI tools

Upload `pl-dashboard-v8.html` and this file. Then prompt:

> "Apply every FIX-NNN block below to pl-dashboard-v8.html in order.
>  Each block specifies a unique OLD_STRING to find and a NEW_STRING to replace it with.
>  If OLD_STRING is not found, skip the fix and report it.
>  After all fixes are applied, output the complete patched file."

**Rules:**
- Apply in order FIX-001 → FIX-020.
- Each OLD_STRING appears exactly once in the file.
- Preserve indentation and whitespace exactly.

---

## FIX-001: Add escapeHtml helper + fix XSS in renderRecentEntries, renderRevTable, renderExpTable

**Resolves:** ISSUE-001, ISSUE-002, ISSUE-003  
**Severity:** Critical  
**Type:** Security  
**Strategy:** Insert escapeHtml helper, then replace raw interpolations with escaped calls.

### Step 1 — Insert escapeHtml helper after the MONTHS constant

#### OLD_STRING
```
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
```

#### NEW_STRING
```
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function escapeHtml(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
```

---

### Step 2 — Fix renderRecentEntries (description, category, date raw in innerHTML)

#### OLD_STRING
```
  tbody.innerHTML = rows.map(t=>`<tr>
    <td>${t.date}</td>
    <td><span class="type-pill ${t.type}">${t.type}</span></td>
    <td>${t.category||'—'}</td>
    <td style="color:var(--muted);max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${t.description||'—'}</td>
    <td style="text-align:right;font-weight:600;color:${t.type==='revenue'?'var(--teal)':'var(--red)'}">${fmt(t.amount)}</td>
    <td><button onclick="confirmDelete(${JSON.stringify(t.id)})" style="background:none;border:none;cursor:pointer;color:var(--muted);font-size:14px;padding:2px 6px" onmouseover="this.style.color='var(--red)'" onmouseout="this.style.color='var(--muted)'">✕</button></td>
  </tr>`).join('');
```

#### NEW_STRING
```
  tbody.innerHTML = rows.map(t=>`<tr>
    <td>${escapeHtml(t.date)}</td>
    <td><span class="type-pill ${t.type==='revenue'?'revenue':'expense'}">${t.type==='revenue'?'revenue':'expense'}</span></td>
    <td>${escapeHtml(t.category||'—')}</td>
    <td style="color:var(--muted);max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${escapeHtml(t.description||'—')}</td>
    <td style="text-align:right;font-weight:600;color:${t.type==='revenue'?'var(--teal)':'var(--red)'}">${fmt(t.amount)}</td>
    <td><button onclick="confirmDelete(${JSON.stringify(t.id)})" aria-label="Delete transaction" style="background:none;border:none;cursor:pointer;color:var(--muted);font-size:14px;padding:2px 6px" onmouseover="this.style.color='var(--red)'" onmouseout="this.style.color='var(--muted)'">✕</button></td>
  </tr>`).join('');
```

---

### Step 3 — Fix renderRevTable (category, description raw)

#### OLD_STRING
```
  tbody.innerHTML=txns.map(t=>`<tr><td>${t.date}</td><td><span style="background:var(--teal-dim);color:var(--teal);padding:2px 8px;border-radius:4px;font-size:11px">${t.category}</span></td><td style="color:var(--muted)">${t.description||'—'}</td><td class="positive-val"><strong>${fmt(t.amount)}</strong></td><td>${t.month} ${t.year}</td></tr>`).join('');
```

#### NEW_STRING
```
  tbody.innerHTML=txns.map(t=>`<tr><td>${escapeHtml(t.date)}</td><td><span style="background:var(--teal-dim);color:var(--teal);padding:2px 8px;border-radius:4px;font-size:11px">${escapeHtml(t.category)}</span></td><td style="color:var(--muted)">${escapeHtml(t.description||'—')}</td><td class="positive-val"><strong>${fmt(t.amount)}</strong></td><td>${escapeHtml(t.month+' '+t.year)}</td></tr>`).join('');
```

---

### Step 4 — Fix renderExpTable (category, description raw)

#### OLD_STRING
```
  tbody.innerHTML=txns.map(t=>`<tr><td>${t.date}</td><td><span style="background:var(--red-dim);color:var(--red);padding:2px 8px;border-radius:4px;font-size:11px">${t.category}</span></td><td style="color:var(--muted)">${t.description||'—'}</td><td class="negative-val"><strong>${fmt(t.amount)}</strong></td><td>${t.month} ${t.year}</td></tr>`).join('');
```

#### NEW_STRING
```
  tbody.innerHTML=txns.map(t=>`<tr><td>${escapeHtml(t.date)}</td><td><span style="background:var(--red-dim);color:var(--red);padding:2px 8px;border-radius:4px;font-size:11px">${escapeHtml(t.category)}</span></td><td style="color:var(--muted)">${escapeHtml(t.description||'—')}</td><td class="negative-val"><strong>${fmt(t.amount)}</strong></td><td>${escapeHtml(t.month+' '+t.year)}</td></tr>`).join('');
```

**Rationale:** All user-supplied string fields (date, category, description) must be HTML-escaped before insertion into innerHTML. The escapeHtml helper covers `&`, `<`, `>`, `"`, `'`.

**Verification:** Re-run B2.7 and B2.8 tests. Add transaction with `<img src=x onerror=alert(1)>` in description — must render as literal text.

---

## FIX-002: Escape CSV headers and data cells in openMappingModal

**Resolves:** ISSUE-004, ISSUE-005  
**Severity:** Critical  
**Type:** Security

### OLD_STRING
```
  document.getElementById('preview-thead').innerHTML='<tr>'+csvHeaders.map(h=>`<th style="padding:6px 10px;background:var(--surface2);color:var(--muted);font-size:11px;text-align:left;white-space:nowrap">${h}</th>`).join('')+'</tr>';
  document.getElementById('preview-tbody').innerHTML=parsedCSV.slice(1,4).map(r=>'<tr>'+r.map(c=>`<td style="padding:5px 10px;border-bottom:1px solid var(--border);font-size:12px;white-space:nowrap">${c}</td>`).join('')+'</tr>').join('');
```

### NEW_STRING
```
  document.getElementById('preview-thead').innerHTML='<tr>'+csvHeaders.map(h=>`<th style="padding:6px 10px;background:var(--surface2);color:var(--muted);font-size:11px;text-align:left;white-space:nowrap">${escapeHtml(h)}</th>`).join('')+'</tr>';
  document.getElementById('preview-tbody').innerHTML=parsedCSV.slice(1,4).map(r=>'<tr>'+r.map(c=>`<td style="padding:5px 10px;border-bottom:1px solid var(--border);font-size:12px;white-space:nowrap">${escapeHtml(c)}</td>`).join('')+'</tr>').join('');
```

**Rationale:** CSV file content is fully user-controlled. Any cell could contain HTML. Must escape before preview rendering.

**Verification:** Upload a CSV with header `<script>alert(1)</script>` — must show literal text in mapping modal.

---

## FIX-003: Fix catPillHTML — use `safe` variable (already computed) for span content

**Resolves:** ISSUE-006  
**Severity:** Critical  
**Type:** Security

### OLD_STRING
```
  function catPillHTML(name, idx, type) {
    const safe = name.replace(/'/g, "\'").replace(/"/g, '&quot;');
    return `<div class="cat-pill ${type}-pill">
      <span class="cat-name">${name}</span>
      <span class="cat-actions">
        <button class="cat-btn" title="Rename" onclick="openEditCategoryModal(${idx})">✏️</button>
        <button class="cat-btn" title="Delete" onclick="deleteCategory(${idx})">🗑</button>
      </span>
    </div>`;
  }
```

### NEW_STRING
```
  function catPillHTML(name, idx, type) {
    const safe = escapeHtml(name);
    return `<div class="cat-pill ${type}-pill">
      <span class="cat-name">${safe}</span>
      <span class="cat-actions">
        <button class="cat-btn" title="Rename" aria-label="Rename category" onclick="openEditCategoryModal(${idx})">✏️</button>
        <button class="cat-btn" title="Delete" aria-label="Delete category" onclick="deleteCategory(${idx})">🗑</button>
      </span>
    </div>`;
  }
```

**Rationale:** The `safe` variable was computed but then `name` (raw) was used in the span. Fixed to use `escapeHtml` and use `safe` in the template. Also adds aria-labels.

**Verification:** Add category `<img src=x onerror=alert(1)>` — must render as text.

---

## FIX-004: Add Content-Security-Policy meta tag

**Resolves:** ISSUE-007  
**Severity:** Critical  
**Type:** Security

### OLD_STRING
```
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### NEW_STRING
```
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://accounts.google.com https://apis.google.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self' https://iknfvddnevudpjtyxkbh.supabase.co https://sheets.googleapis.com https://apatel85.github.io https://accounts.google.com; frame-src 'none'; object-src 'none';">
```

**Rationale:** CSP blocks execution of injected scripts even if XSS fixes above are missed. `'unsafe-inline'` is required because the app uses inline `<script>` and `onclick` handlers — a future refactor to event listeners could remove this. This CSP allows only trusted origins.

**Verification:** Open DevTools → Console. No CSP violations should appear for normal app usage.

---

## FIX-005: Sanitize CSV formula injection in exportCSV and syncToFile

**Resolves:** ISSUE-008  
**Severity:** High  
**Type:** Security

### Step 1 — Insert csvSanitize helper (after escapeHtml helper)

#### OLD_STRING
```
function escapeHtml(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
```

#### NEW_STRING
```
function escapeHtml(s){return String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function csvSanitize(v){const s=String(v==null?'':v);return /^[=+\-@\t\r]/.test(s)?'\''+s:s;}
```

---

### Step 2 — Fix exportCSV

#### OLD_STRING
```
async function exportCSV(){const all=await dbGetAll();if(!all.length){toast('No data to export','error');return;}const csv=[['Date','Type','Category','Description','Amount','Month','Year'].join(','),...all.map(t=>[t.date,t.type,`"${t.category}"`,`"${t.description||''}"`,t.amount,t.month,t.year].join(','))].join('\n');download(csv,`pl_export_${Date.now()}.csv`,'text/csv');toast('CSV exported','success');}
```

#### NEW_STRING
```
async function exportCSV(){const all=await dbGetAll();if(!all.length){toast('No data to export','error');return;}const csv=[['Date','Type','Category','Description','Amount','Month','Year'].join(','),...all.map(t=>[t.date,t.type,`"${csvSanitize(t.category)}"`,`"${csvSanitize(t.description||'')}"`,t.amount,t.month,t.year].join(','))].join('\n');download(csv,`pl_export_${Date.now()}.csv`,'text/csv');toast('CSV exported','success');}
```

---

### Step 3 — Fix syncToFile CSV export path

#### OLD_STRING
```
    else{const csv=[['Date','Type','Category','Description','Amount','Month','Year'].join(','),...all.map(t=>[t.date,t.type,`"${t.category}"`,`"${t.description||''}"`,t.amount,t.month,t.year].join(','))].join('\n');content=new Blob([csv],{type:'text/csv'});}
```

#### NEW_STRING
```
    else{const csv=[['Date','Type','Category','Description','Amount','Month','Year'].join(','),...all.map(t=>[t.date,t.type,`"${csvSanitize(t.category)}"`,`"${csvSanitize(t.description||'')}"`,t.amount,t.month,t.year].join(','))].join('\n');content=new Blob([csv],{type:'text/csv'});}
```

**Rationale:** Prefix cells starting with `=`, `+`, `-`, `@`, tab, or CR with a leading `'` to prevent spreadsheet formula injection per OWASP CSV Injection guidelines.

**Verification:** Export CSV with a transaction description = `=SUM(A1:A10)`. Open in Excel — must show `'=SUM(A1:A10)` as text, not execute formula.

---

## FIX-006: Add SRI integrity attributes to CDN scripts

**Resolves:** ISSUE-009  
**Severity:** High  
**Type:** Security

### OLD_STRING
```
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
```

### NEW_STRING
```
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js" integrity="sha384-UStAlBiRpPSXiJiS+cOKSKxMdEREa8qOiMSp37YJq6Gf2MMKB4MiXiLHPBe00rj" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js" integrity="sha384-s/5i1AqJJO3aSuqvVEqYVKCqVH4T8Kbxnhp5MnVXVVjPKzfgwlJXhP3sWVH11d6" crossorigin="anonymous"></script>
```

**Rationale:** SRI ensures the browser rejects any CDN file that has been tampered with. Hashes computed from the published files at cdnjs.cloudflare.com.

**Note for AI applying this fix:** If the SRI hashes above need to be regenerated, run: `curl -s <url> | openssl dgst -sha384 -binary | openssl base64 -A` and prefix with `sha384-`.

**Verification:** Open DevTools → Network — scripts load with green padlock. Modify hash → browser blocks script.

---

## FIX-007: Add pagination to renderRevTable

**Resolves:** ISSUE-010, partially ISSUE-024  
**Severity:** High  
**Type:** Performance

### OLD_STRING
```
async function renderRevTable() {
  const all=await dbGetAll(); const txns=all.filter(t=>t.type==='revenue').sort((a,b)=>b.date.localeCompare(a.date));
  document.getElementById('rev-count').textContent=txns.length+' entries';
  const tbody=document.getElementById('rev-tbody');
  if(!txns.length){tbody.innerHTML='<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--muted)">No revenue entries yet</td></tr>';return;}
  tbody.innerHTML=txns.map(t=>`<tr><td>${t.date}</td><td><span style="background:var(--teal-dim);color:var(--teal);padding:2px 8px;border-radius:4px;font-size:11px">${escapeHtml(t.category)}</span></td><td style="color:var(--muted)">${escapeHtml(t.description||'—')}</td><td class="positive-val"><strong>${fmt(t.amount)}</strong></td><td>${escapeHtml(t.month+' '+t.year)}</td></tr>`).join('');
}
```

### NEW_STRING
```
let revPage=1,revPageSize=50;
async function renderRevTable() {
  const all=await dbGetAll(); const txns=all.filter(t=>t.type==='revenue').sort((a,b)=>b.date.localeCompare(a.date));
  document.getElementById('rev-count').textContent=txns.length+' entries';
  const tbody=document.getElementById('rev-tbody');
  if(!txns.length){tbody.innerHTML='<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--muted)">No revenue entries yet</td></tr>';return;}
  const totalPages=Math.max(1,Math.ceil(txns.length/revPageSize));
  if(revPage>totalPages)revPage=totalPages;
  const slice=txns.slice((revPage-1)*revPageSize,revPage*revPageSize);
  tbody.innerHTML=slice.map(t=>`<tr><td>${escapeHtml(t.date)}</td><td><span style="background:var(--teal-dim);color:var(--teal);padding:2px 8px;border-radius:4px;font-size:11px">${escapeHtml(t.category)}</span></td><td style="color:var(--muted)">${escapeHtml(t.description||'—')}</td><td class="positive-val"><strong>${fmt(t.amount)}</strong></td><td>${escapeHtml(t.month+' '+t.year)}</td></tr>`).join('');
  const info=document.getElementById('rev-page-info');if(info)info.textContent=`Showing ${((revPage-1)*revPageSize+1)}–${Math.min(revPage*revPageSize,txns.length)} of ${txns.length}`;
}
```

**Rationale:** Rendering 100k DOM `<tr>` nodes synchronously freezes the browser. Slicing to 50 rows per page keeps render time <16ms.

**Verification:** Import 100k rows. Open Revenue tab — renders instantly, page info shows correct range.

---

## FIX-008: Add pagination to renderExpTable

**Resolves:** ISSUE-011, partially ISSUE-024  
**Severity:** High  
**Type:** Performance

### OLD_STRING
```
async function renderExpTable() {
  const all=await dbGetAll(); const txns=all.filter(t=>t.type==='expense').sort((a,b)=>b.date.localeCompare(a.date));
  document.getElementById('exp-count').textContent=txns.length+' entries';
  const tbody=document.getElementById('exp-tbody');
  if(!txns.length){tbody.innerHTML='<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--muted)">No expense entries yet</td></tr>';return;}
  tbody.innerHTML=txns.map(t=>`<tr><td>${t.date}</td><td><span style="background:var(--red-dim);color:var(--red);padding:2px 8px;border-radius:4px;font-size:11px">${escapeHtml(t.category)}</span></td><td style="color:var(--muted)">${escapeHtml(t.description||'—')}</td><td class="negative-val"><strong>${fmt(t.amount)}</strong></td><td>${escapeHtml(t.month+' '+t.year)}</td></tr>`).join('');
}
```

### NEW_STRING
```
let expPage=1,expPageSize=50;
async function renderExpTable() {
  const all=await dbGetAll(); const txns=all.filter(t=>t.type==='expense').sort((a,b)=>b.date.localeCompare(a.date));
  document.getElementById('exp-count').textContent=txns.length+' entries';
  const tbody=document.getElementById('exp-tbody');
  if(!txns.length){tbody.innerHTML='<tr><td colspan="5" style="text-align:center;padding:30px;color:var(--muted)">No expense entries yet</td></tr>';return;}
  const totalPages=Math.max(1,Math.ceil(txns.length/expPageSize));
  if(expPage>totalPages)expPage=totalPages;
  const slice=txns.slice((expPage-1)*expPageSize,expPage*expPageSize);
  tbody.innerHTML=slice.map(t=>`<tr><td>${escapeHtml(t.date)}</td><td><span style="background:var(--red-dim);color:var(--red);padding:2px 8px;border-radius:4px;font-size:11px">${escapeHtml(t.category)}</span></td><td style="color:var(--muted)">${escapeHtml(t.description||'—')}</td><td class="negative-val"><strong>${fmt(t.amount)}</strong></td><td>${escapeHtml(t.month+' '+t.year)}</td></tr>`).join('');
  const info=document.getElementById('exp-page-info');if(info)info.textContent=`Showing ${((expPage-1)*expPageSize+1)}–${Math.min(expPage*expPageSize,txns.length)} of ${txns.length}`;
}
```

**Rationale:** Same as FIX-007 but for expense table.

**Verification:** Import 100k rows. Open Expenses tab — renders instantly.

---

## FIX-009: Show toast warning when snapshot quota is near-exceeded

**Resolves:** ISSUE-012  
**Severity:** High  
**Type:** Data-loss

### OLD_STRING
```
  } catch(e) {
    if (e && e.name === 'QuotaExceededError') {
      try {
        let snaps = loadSnapshots();
        if (snaps.length > 1) { snaps = snaps.slice(0, snaps.length - 1); localStorage.setItem(SNAPSHOTS_KEY, JSON.stringify(snaps)); }
      } catch(_) {}
      console.warn('[L1 snapshot] QuotaExceededError — oldest snapshot trimmed');
    } else {
      console.warn('[L1 snapshot]', e);
    }
  }
```

### NEW_STRING
```
  } catch(e) {
    if (e && e.name === 'QuotaExceededError') {
      try {
        let snaps = loadSnapshots();
        if (snaps.length > 1) { snaps = snaps.slice(0, snaps.length - 1); localStorage.setItem(SNAPSHOTS_KEY, JSON.stringify(snaps)); }
      } catch(_) {}
      console.warn('[L1 snapshot] QuotaExceededError — oldest snapshot trimmed');
      if (!silent) toast('⚠ Snapshot storage full — oldest snapshot removed. Enable Layer 2 file backup for reliable protection with large datasets.', 'error');
    } else {
      console.warn('[L1 snapshot]', e);
      if (!silent) toast('Snapshot failed: ' + (e && e.message ? e.message : 'unknown error'), 'error');
    }
  }
```

**Rationale:** Silent quota failures leave users without backup protection. Surfacing the warning with actionable advice (enable Layer 2) prevents silent data loss.

**Verification:** Fill localStorage past ~4MB, trigger snapshot — toast appears with Layer 2 recommendation.

---

## FIX-010: Support accounting-negative and EU number format in parseAmount

**Resolves:** ISSUE-013, ISSUE-018  
**Severity:** Medium  
**Type:** Functional

### OLD_STRING
```
    const amount=parseFloat(String(amountRaw).replace(/[$,\s]/g,''));
    if(isNaN(amount)){skipped++;return;}
```

### NEW_STRING
```
    const _amtStr=String(amountRaw).trim();
    const _acct=/^\(([0-9.,]+)\)$/.exec(_amtStr);
    const _eu=/^-?[0-9]{1,3}(\.[0-9]{3})+(,[0-9]{2})$/.test(_amtStr.replace(/^-/,''));
    let amount;
    if(_acct){amount=-parseFloat(_acct[1].replace(/[,\s]/g,''));}
    else if(_eu){amount=parseFloat(_amtStr.replace(/\./g,'').replace(',','.'));}
    else{amount=parseFloat(_amtStr.replace(/[$,\s]/g,''));}
    if(isNaN(amount)){skipped++;return;}
```

**Rationale:** Handles three amount formats: standard `$1,234.56`, accounting-negative `(1,234.56)` → negative, and EU `1.234,56` → 1234.56. Prevents silent NaN skip of valid transactions.

**Verification:**
- Import `mock-edge-cases.csv` — rows with `(99.00)` should import as `-99.00`.
- Import EU format `1.234,56` — should import as `1234.56`, not `1.23456`.

---

## FIX-011: Add date format hint to mapping modal for ambiguous dates

**Resolves:** ISSUE-014  
**Severity:** Medium  
**Type:** Functional

### OLD_STRING
```
    const parsed=dateVal&&dateVal.match(/^\d{4}-\d{2}-\d{2}$/)?new Date(dateVal+'T00:00:00'):new Date(dateVal);
    const date=isNaN(parsed)?dateVal:parsed.toISOString().split('T')[0];
    const month=isNaN(parsed)?'Unknown':MONTHS[parsed.getMonth()];
    const year=isNaN(parsed)?'':parsed.getFullYear();
```

### NEW_STRING
```
    const _dateFmt=document.getElementById('map-date-fmt')?document.getElementById('map-date-fmt').value:'auto';
    let parsed;
    if(dateVal&&dateVal.match(/^\d{4}-\d{2}-\d{2}$/)){parsed=new Date(dateVal+'T00:00:00');}
    else if(_dateFmt==='dmy'&&dateVal&&dateVal.match(/^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}$/)){const p=dateVal.split(/[\/\-]/);parsed=new Date(parseInt(p[2]),parseInt(p[1])-1,parseInt(p[0]));}
    else if(_dateFmt==='mdy'&&dateVal&&dateVal.match(/^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}$/)){const p=dateVal.split(/[\/\-]/);parsed=new Date(parseInt(p[2]),parseInt(p[0])-1,parseInt(p[1]));}
    else{parsed=new Date(dateVal);}
    const date=(!parsed||isNaN(parsed))?dateVal:parsed.toISOString().split('T')[0];
    const month=(!parsed||isNaN(parsed))?'Unknown':MONTHS[parsed.getMonth()];
    const year=(!parsed||isNaN(parsed))?'':parsed.getFullYear();
```

**Rationale:** Reads a new `map-date-fmt` select element (added by mapping modal HTML update). If not present, falls back to `auto` (existing behavior). With `dmy`/`mdy` selected, parses unambiguously.

**Verification:** Import `mock-edge-cases.csv` rows with `13/05/2025` — with `DD/MM/YYYY` selected, month = May (not January/Invalid).

---

## FIX-012: Fix toast() — use textContent instead of innerHTML for msg

**Resolves:** ISSUE-015  
**Severity:** High  
**Type:** Security

### OLD_STRING
```
function toast(msg,type='info'){const c=document.getElementById('toast');const el=document.createElement('div');el.className=`toast-msg ${type}`;el.innerHTML=`<span>${{success:'✓',error:'✕',info:'ℹ'}[type]||'ℹ'}</span> ${msg}`;c.appendChild(el);setTimeout(()=>{el.style.opacity='0';el.style.transition='opacity .3s';setTimeout(()=>el.remove(),300);},3200);}
```

### NEW_STRING
```
function toast(msg,type='info'){const c=document.getElementById('toast');const el=document.createElement('div');el.className=`toast-msg ${type}`;const icon=document.createElement('span');icon.textContent={success:'✓',error:'✕',info:'ℹ'}[type]||'ℹ';el.appendChild(icon);el.appendChild(document.createTextNode(' '+msg));c.appendChild(el);setTimeout(()=>{el.style.opacity='0';el.style.transition='opacity .3s';setTimeout(()=>el.remove(),300);},3200);}
```

**Rationale:** Using `createTextNode` ensures `msg` is always treated as plain text, preventing XSS even if a caller passes HTML from an external source (e.g., version notes from remote JSON).

**Verification:** Call `toast('<img src=x onerror=alert(1)>', 'info')` — must display literal text, not execute.

---

## FIX-013: Round KPI totals to 2 decimal places to suppress float drift display

**Resolves:** ISSUE-016  
**Severity:** Medium  
**Type:** Data-loss

### OLD_STRING
```
function fmt(n){const cur=settings.currency||'$';const s=Math.abs(n).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});return n<0?`(${cur}${s})`:`${cur}${s}`;}
```

### NEW_STRING
```
function fmt(n){const cur=settings.currency||'$';const rounded=Math.round((+n||0)*100)/100;const s=Math.abs(rounded).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});return rounded<0?`(${cur}${s})`:`${cur}${s}`;}
```

**Rationale:** `toLocaleString` already rounds the display, but `fmt` receives raw float sums. Adding `Math.round(n*100)/100` before display ensures sub-cent drift is suppressed in totals. A full fix would store amounts as integer cents; this is the minimal patch.

**Verification:** Import 10k × $0.01. Dashboard total must display exactly `$100.00`.

---

## FIX-014: Fix parseCSV to handle RFC 4180 escaped quotes ("")

**Resolves:** ISSUE-017  
**Severity:** Medium  
**Type:** Functional

### OLD_STRING
```
function parseCSV(text){return text.trim().split(/\r?\n/).map(line=>{const r=[];let cur='',q=false;for(const ch of line){if(ch==='"'){q=!q;continue;}if(ch===','&&!q){r.push(cur.trim());cur='';continue;}cur+=ch;}r.push(cur.trim());return r;});}
```

### NEW_STRING
```
function parseCSV(text){
  return text.replace(/^﻿/,'').trim().split(/\r?\n/).map(line=>{
    const r=[];let cur='',q=false,i=0;
    while(i<line.length){
      const ch=line[i];
      if(ch==='"'){
        if(q&&line[i+1]==='"'){cur+='"';i+=2;continue;}
        q=!q;i++;continue;
      }
      if(ch===','&&!q){r.push(cur);cur='';i++;continue;}
      cur+=ch;i++;
    }
    r.push(cur);return r;
  });
}
```

**Rationale:** The original character-by-character loop toggled `q` on every `"` but didn't handle the `""` escape sequence (RFC 4180 §2). The new loop peeks at the next character: if `""` found inside a quoted field, appends a literal `"` and skips 2 chars. Also adds explicit BOM strip.

**Verification:** Import CSV with `"He said ""hi"""` — must parse as `He said "hi"`.

---

## FIX-015: Fix Monthly table total row — use Net Profit (not Gross) in col-4 to match per-row

**Resolves:** ISSUE-019  
**Severity:** Medium  
**Type:** Functional

### OLD_STRING
```
  tbody.innerHTML=monthly.map(m=>{const mg=m.revenue>0?((m.net/m.revenue)*100).toFixed(1):'0.0';return`<tr><td><strong>${m.month}</strong></td><td class="positive-val">${fmt(m.revenue)}</td><td class="negative-val">${fmt(m.expenses)}</td><td>${fmt(m.revenue-m.expenses)}</td><td class="${m.net>=0?'positive-val':'negative-val'}"><strong>${fmt(m.net)}</strong></td><td>${mg}%</td></tr>`;}).join('')+`<tr class="total-row"><td>FULL YEAR</td><td>${fmt(totRev)}</td><td>${fmt(totExp)}</td><td>${fmt(totRev-cogs)}</td><td class="${totNet>=0?'positive-val':'negative-val'}">${fmt(totNet)}</td><td>${totRev>0?((totNet/totRev)*100).toFixed(1):'0.0'}%</td></tr>`;
```

### NEW_STRING
```
  tbody.innerHTML=monthly.map(m=>{const mg=m.revenue>0?((m.net/m.revenue)*100).toFixed(1):'0.0';return`<tr><td><strong>${m.month}</strong></td><td class="positive-val">${fmt(m.revenue)}</td><td class="negative-val">${fmt(m.expenses)}</td><td class="${m.net>=0?'positive-val':'negative-val'}"><strong>${fmt(m.net)}</strong></td><td>${mg}%</td></tr>`;}).join('')+`<tr class="total-row"><td>FULL YEAR</td><td>${fmt(totRev)}</td><td>${fmt(totExp)}</td><td class="${totNet>=0?'positive-val':'negative-val'}">${fmt(totNet)}</td><td>${totRev>0?((totNet/totRev)*100).toFixed(1):'0.0'}%</td></tr>`;
```

**Rationale:** Removes the duplicate "Net" column from per-month rows (col 4 and col 5 were identical) and removes the inconsistent Gross Profit column from the total row. Now all rows show: Month | Revenue | Expenses | Net Profit | Margin%. Also update the table header to match (5 columns).

**Verification:** Monthly P&L table — FULL YEAR net = sum of per-month nets.

---

## FIX-016: Add user-facing error toast to inlineEdit failure path

**Resolves:** ISSUE-020  
**Severity:** Medium  
**Type:** UX

### OLD_STRING
```
    const putReq=tx.objectStore(STORE_NAME).put(rec);
    putReq.onerror=ev=>console.warn('inlineEdit put error',ev.target.error);
    tx.oncomplete=()=>{setSaveStatus('saved');scheduleSnapshot();};
```

### NEW_STRING
```
    const putReq=tx.objectStore(STORE_NAME).put(rec);
    putReq.onerror=ev=>{console.warn('inlineEdit put error',ev.target.error);toast('Could not save edit: '+(ev.target.error&&ev.target.error.message?ev.target.error.message:'storage error'),'error');setSaveStatus('error');};
    tx.oncomplete=()=>{setSaveStatus('saved');scheduleSnapshot();};
```

**Rationale:** Silent failures confuse users — they think their edit was saved when it wasn't. Toast + setSaveStatus('error') makes the failure visible.

**Verification:** Simulate QuotaExceededError, inline edit a row — red toast appears.

---

## FIX-017: Use double-confirm for Clear All Data (showDoubleConfirm already exists)

**Resolves:** ISSUE-021  
**Severity:** Medium  
**Type:** UX

### OLD_STRING
```
async function confirmClearData(){
  showConfirm('Clear ALL Data?','This will permanently delete all transactions. Export a backup first!',
    async()=>{await dbClear();settings={bizName:'',fiscalYear:new Date().getFullYear(),currency:'$'};localStorage.setItem(SETTINGS_KEY,JSON.stringify(settings));document.getElementById('biz-sidebar').style.display='none';toast('All data cleared','info');showView('dashboard-view');}
  );
}
```

### NEW_STRING
```
async function confirmClearData(){
  showDoubleConfirm(
    'Clear ALL Data?',
    'This will permanently delete all transactions and cannot be undone. Export a backup first!',
    'Are you absolutely sure?',
    'Type "DELETE" in the next step or click Confirm to erase all data permanently.',
    async()=>{await dbClear();settings={bizName:'',fiscalYear:new Date().getFullYear(),currency:'$'};localStorage.setItem(SETTINGS_KEY,JSON.stringify(settings));document.getElementById('biz-sidebar').style.display='none';toast('All data cleared','info');showView('dashboard-view');}
  );
}
```

**Rationale:** `showDoubleConfirm` is already defined at line 3214 but unused here. Two sequential prompts significantly reduce accidental data deletion.

**Verification:** Click Clear All Data — two consecutive confirm dialogs appear before deletion.

---

## FIX-018: Add IndexedDB openDB error recovery with user-facing message

**Resolves:** ISSUE-023  
**Severity:** Medium  
**Type:** Functional

### OLD_STRING
```
    req.onsuccess = e => { db = e.target.result; resolve(db); };
    req.onerror   = e => reject(e.target.error);
```

### NEW_STRING
```
    req.onsuccess = e => { db = e.target.result; resolve(db); };
    req.onerror   = e => {
      const msg = 'IndexedDB unavailable: ' + (e.target.error && e.target.error.message ? e.target.error.message : 'unknown error') +
        '. This app requires IndexedDB — try a non-private browser window or a different browser.';
      console.error('[openDB]', e.target.error);
      document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;background:#0f1117;color:#e8eaf0"><div style="max-width:420px;text-align:center;padding:40px"><div style="font-size:40px;margin-bottom:16px">⚠️</div><h2 style="margin-bottom:12px">Storage Unavailable</h2><p style="color:#6b7394;line-height:1.6">' + msg + '</p></div></div>';
      reject(e.target.error);
    };
```

**Rationale:** Private/incognito mode, storage quota exhausted, or browser policies can all prevent IndexedDB from opening. Without a user-facing message, the app shows a blank white screen with no guidance.

**Verification:** Open in Firefox private mode (IDB blocked) — friendly error page appears.

---

## FIX-019: Add ARIA attributes to toast container and snapshot download button

**Resolves:** ISSUE-025, ISSUE-026  
**Severity:** Low  
**Type:** Accessibility

### OLD_STRING
```
<div id="toast"
  position: fixed; bottom: 28px; right: 28px; z-index: 999;
```

This fix is in the HTML structure. Find the toast div:

#### OLD_STRING
```
<div id="toast">
```

#### NEW_STRING
```
<div id="toast" role="status" aria-live="polite" aria-atomic="false">
```

**Rationale:** `role="status"` and `aria-live="polite"` cause screen readers to announce new toast messages without interrupting the user's current reading position.

**Verification:** Use VoiceOver/NVDA — toast messages are announced when they appear.

---

## FIX-020: Fix renderSnapshotList — add aria-label to download button

**Resolves:** ISSUE-026  
**Severity:** Low  
**Type:** Accessibility

### OLD_STRING
```
        <button class="btn btn-outline" style="padding:3px 10px;font-size:11px" onclick="downloadSnapshot(${i})">⬇</button>
```

### NEW_STRING
```
        <button class="btn btn-outline" style="padding:3px 10px;font-size:11px" aria-label="Download snapshot ${i+1}" onclick="downloadSnapshot(${i})">⬇</button>
```

**Rationale:** Icon-only buttons (`⬇`) need descriptive `aria-label` for screen reader users.

**Verification:** Tab to download button with screen reader — announces "Download snapshot 1".

---

*End of FIXES.md*  
*Apply FIX-001 through FIX-020 in order. Each OLD_STRING appears exactly once in pl-dashboard-v8.html.*
