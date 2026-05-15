# PATCH_CANDIDATES.md — Surgical fix patches for pl-dashboard-v8.html

**Date:** 2026-05-15  
**Format:** OLD_STRING / NEW_STRING patches, ordered top-to-bottom by line number  
**Apply with:** Claude Code Edit tool — find OLD_STRING, replace with NEW_STRING  
**All patches are non-overlapping and safe to apply independently**

> Do NOT include in this file: T2-4 (dbQuery refactor) or T3-1 (integer arithmetic) — those require planned PRs with full testing.

---

## PATCH-001 — Escape version string in settings-update-status

**Resolves:** NEW-013  
**Line:** ~4825  
**Time:** 2 min  

**OLD_STRING:**
```
document.getElementById('settings-update-status').innerHTML=`<span style="color:var(--green);font-weight:600">🔔 v${remoteVerData.latest_version} available!</span> <a href="#" onclick="openChangelog();return false" style="color:var(--teal)">See what's new →</a>`;}
```

**NEW_STRING:**
```
document.getElementById('settings-update-status').innerHTML=`<span style="color:var(--green);font-weight:600">🔔 v${escapeHtml(remoteVerData.latest_version)} available!</span> <a href="#" onclick="openChangelog();return false" style="color:var(--teal)">See what's new →</a>`;}
```

---

## PATCH-002 — Escape version.json data in showUpdateBanner

**Resolves:** NEW-001  
**Line:** ~4843  
**Time:** 3 min  

**OLD_STRING:**
```
function showUpdateBanner(data){const notes=(data.release_notes||[])[0]?.summary||'Improvements and bug fixes.';document.getElementById('update-banner-text').innerHTML=`<strong>v${data.latest_version}</strong> is available &nbsp;·&nbsp; ${notes}`;
```

**NEW_STRING:**
```
function showUpdateBanner(data){const notes=escapeHtml((data.release_notes||[])[0]?.summary||'Improvements and bug fixes.');document.getElementById('update-banner-text').innerHTML=`<strong>v${escapeHtml(data.latest_version)}</strong> is available &nbsp;·&nbsp; ${notes}`;
```

---

## PATCH-003 — Escape all fields in openChangelog

**Resolves:** NEW-002  
**Line:** ~4880  
**Time:** 10 min  

**OLD_STRING:**
```
  document.getElementById('changelog-body').innerHTML=releases.map((rel,i)=>`<div class="release-block"><div class="release-version"><span class="ver-tag ${rel.version===latest?'latest':'old'}">${rel.version===latest?'● Latest':'●'} v${rel.version}</span><span class="ver-date">${rel.date||''}</span></div><div class="ver-title">${rel.title||''}</div><ul class="release-changes" style="margin-top:8px">${(rel.changes||[]).map(c=>`<li><span class="change-type ${c.type||'imp'}">${c.type==='new'?'New':c.type==='fix'?'Fix':'Imp'}</span><span>${c.text}</span></li>`).join('')}</ul></div>${i<releases.length-1?'<hr style="border:none;border-top:1px solid var(--border);margin:0 0 20px">':''}`).join('');
```

**NEW_STRING:**
```
  document.getElementById('changelog-body').innerHTML=releases.map((rel,i)=>{const rv=escapeHtml(rel.version||'');const rd=escapeHtml(rel.date||'');const rt=escapeHtml(rel.title||'');const isLatest=rel.version===latest;return`<div class="release-block"><div class="release-version"><span class="ver-tag ${isLatest?'latest':'old'}">${isLatest?'● Latest':'●'} v${rv}</span><span class="ver-date">${rd}</span></div><div class="ver-title">${rt}</div><ul class="release-changes" style="margin-top:8px">${(rel.changes||[]).map(c=>`<li><span class="change-type ${escapeHtml(c.type||'imp')}">${c.type==='new'?'New':c.type==='fix'?'Fix':'Imp'}</span><span>${escapeHtml(c.text||'')}</span></li>`).join('')}</ul></div>${i<releases.length-1?'<hr style="border:none;border-top:1px solid var(--border);margin:0 0 20px">':''}`;}).join('');
```

---

## PATCH-004 — Escape email in showAccessDenied

**Resolves:** NEW-004  
**Lines:** ~5188–5201  
**Time:** 5 min  

**OLD_STRING:**
```
function showAccessDenied(email, reason) {
  document.getElementById('auth-signin-panel').style.display = 'none';
  document.getElementById('auth-denied-panel').style.display = 'block';
  const msgs = {
    not_found: `No license was found for <strong>${email}</strong>.<br><br>
      If you purchased this dashboard, make sure you're signing in with the same Google account
      you used at checkout. If you used a different email at purchase, contact support.`,
    suspended: `Your license for <strong>${email}</strong> has been suspended.<br><br>
      Please contact support if you believe this is an error.`,
    expired:   `Your license for <strong>${email}</strong> has expired.<br><br>
      Please renew your subscription to continue accessing the dashboard.`
  };
  document.getElementById('auth-denied-msg').innerHTML = msgs[reason] || `Access denied for ${email}.`;
```

**NEW_STRING:**
```
function showAccessDenied(email, reason) {
  document.getElementById('auth-signin-panel').style.display = 'none';
  document.getElementById('auth-denied-panel').style.display = 'block';
  const safeEmail = escapeHtml(email);
  const msgs = {
    not_found: `No license was found for <strong>${safeEmail}</strong>.<br><br>
      If you purchased this dashboard, make sure you're signing in with the same Google account
      you used at checkout. If you used a different email at purchase, contact support.`,
    suspended: `Your license for <strong>${safeEmail}</strong> has been suspended.<br><br>
      Please contact support if you believe this is an error.`,
    expired:   `Your license for <strong>${safeEmail}</strong> has expired.<br><br>
      Please renew your subscription to continue accessing the dashboard.`
  };
  document.getElementById('auth-denied-msg').innerHTML = msgs[reason] || `Access denied for ${safeEmail}.`;
```

---

## PATCH-005 — Escape user.name and user.plan in showAuthSuccess

**Resolves:** NEW-003  
**Lines:** ~5207–5209  
**Time:** 3 min  

**OLD_STRING:**
```
  document.getElementById('auth-success-msg').innerHTML =
    `Welcome back, <strong>${user.name.split(' ')[0]}</strong>! &nbsp;·&nbsp; ` +
    `<span style="color:#0ecfbe">${user.plan.charAt(0).toUpperCase()+user.plan.slice(1)} license</span>`;
```

**NEW_STRING:**
```
  document.getElementById('auth-success-msg').innerHTML =
    `Welcome back, <strong>${escapeHtml(user.name.split(' ')[0])}</strong>! &nbsp;·&nbsp; ` +
    `<span style="color:#0ecfbe">${escapeHtml(user.plan.charAt(0).toUpperCase()+user.plan.slice(1))} license</span>`;
```

---

## PATCH-006 — Escape sheetInfo.name and dateStr in auth-restore-details

**Resolves:** NEW-005  
**Lines:** ~5360–5373  
**Time:** 5 min  

**OLD_STRING:**
```
  document.getElementById('auth-restore-details').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <div>
        <div style="font-size:10px;font-weight:600;color:#6b7394;letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px">Transactions</div>
        <div style="font-size:20px;font-weight:700;color:#0ecfbe">${sheetInfo.rowCount.toLocaleString()}</div>
      </div>
      <div>
        <div style="font-size:10px;font-weight:600;color:#6b7394;letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px">Last Backed Up</div>
        <div style="font-size:12px;font-weight:600;color:#e8eaf0;margin-top:4px">${dateStr}</div>
      </div>
    </div>
    <div style="margin-top:10px;padding-top:10px;border-top:1px solid #2a3045;font-size:11px;color:#6b7394">
      📄 ${sheetInfo.name}
    </div>
  `;
```

**NEW_STRING:**
```
  document.getElementById('auth-restore-details').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <div>
        <div style="font-size:10px;font-weight:600;color:#6b7394;letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px">Transactions</div>
        <div style="font-size:20px;font-weight:700;color:#0ecfbe">${escapeHtml(String(sheetInfo.rowCount.toLocaleString()))}</div>
      </div>
      <div>
        <div style="font-size:10px;font-weight:600;color:#6b7394;letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px">Last Backed Up</div>
        <div style="font-size:12px;font-weight:600;color:#e8eaf0;margin-top:4px">${escapeHtml(dateStr)}</div>
      </div>
    </div>
    <div style="margin-top:10px;padding-top:10px;border-top:1px solid #2a3045;font-size:11px;color:#6b7394">
      📄 ${escapeHtml(sheetInfo.name)}
    </div>
  `;
```

---

## PATCH-007 — Escape file name in updateSyncUI

**Resolves:** NEW-010 (first occurrence)  
**Line:** ~4688  
**Time:** 2 min  

**OLD_STRING:**
```
  document.getElementById('sync-file-label').innerHTML=name?`Linked file: <strong>${name}</strong>`:'No file linked';
```

**NEW_STRING:**
```
  document.getElementById('sync-file-label').innerHTML=name?`Linked file: <strong>${escapeHtml(name)}</strong>`:'No file linked';
```

---

## PATCH-008 — Escape savedFile name in init

**Resolves:** NEW-010 (second occurrence)  
**Line:** ~5743  
**Time:** 2 min  

**OLD_STRING:**
```
    if (el) el.innerHTML = `Previously linked: <strong>${savedFile}</strong> — click "Link File" to reconnect`;
```

**NEW_STRING:**
```
    if (el) el.innerHTML = `Previously linked: <strong>${escapeHtml(savedFile)}</strong> — click "Link File" to reconnect`;
```

---

## PATCH-009 — Add csvSanitize to exportXLSX

**Resolves:** NEW-007  
**Line:** ~4720  
**Time:** 3 min  

**OLD_STRING:**
```
const txData=all.map(t=>({Date:t.date,Type:t.type,Category:t.category||'',Description:t.description||'',Amount:t.amount,Month:t.month,Year:t.year}));
```

**NEW_STRING:**
```
const txData=all.map(t=>({Date:t.date,Type:t.type,Category:csvSanitize(t.category||''),Description:csvSanitize(t.description||''),Amount:t.amount,Month:t.month,Year:t.year}));
```

---

## PATCH-010 — Escape CATEGORIES in entry form option build

**Resolves:** NEW-008 (first occurrence)  
**Line:** ~6040–6041  
**Time:** 3 min  

**OLD_STRING:**
```
      sel.innerHTML = '<option value="">— Select —</option>' +
        CATEGORIES.map(c => `<option value="${c}"${c===current?' selected':''}>${c}</option>`).join('');
```

**NEW_STRING:**
```
      sel.innerHTML = '<option value="">— Select —</option>' +
        CATEGORIES.map(c => `<option value="${escapeHtml(c)}"${c===current?' selected':''}>${escapeHtml(c)}</option>`).join('');
```

---

## PATCH-011 — Escape CATEGORIES in filter dropdowns

**Resolves:** NEW-008 (second occurrence)  
**Line:** ~6049  
**Time:** 2 min  

**OLD_STRING:**
```
      el.innerHTML = base + CATEGORIES.map(c => `<option value="${c}"${c===cur?' selected':''}>${c}</option>`).join('');
```

**NEW_STRING:**
```
      el.innerHTML = base + CATEGORIES.map(c => `<option value="${escapeHtml(c)}"${c===cur?' selected':''}>${escapeHtml(c)}</option>`).join('');
```

---

## PATCH-012 — Fix SW CACHE_VERSION to match APP_VERSION

**Resolves:** NEW-015  
**File:** service-worker.js:17  
**Time:** 1 min  
**Note:** This triggers cache invalidation for all users — desired behavior for a version bump.

**OLD_STRING:**
```
const CACHE_VERSION = 'pl-dashboard-v8.5.0';
```

**NEW_STRING:**
```
const CACHE_VERSION = 'pl-dashboard-v8.3.0';
```

---

## NOT INCLUDED HERE (architectural — plan as separate PRs)

| Fix | Reason excluded |
|---|---|
| Monthly table column fix (NEW-006) | Requires deciding Gross Profit formula; touches table HTML + JS render |
| renderRevTable/Exp dbQuery refactor (NEW-009) | Multi-function change to IndexedDB engine |
| Float → integer cents (ISSUE-016) | Data migration required; high blast radius |
| role=dialog on modals (NEW-011) | HTML structural change across 3 modal elements + focus-trap JS |
