# P&L Dashboard — User Guide

A practical guide for using the dashboard day-to-day.

---

## Quick start

### Step 1 — Open the app

Go to: **https://apatel85.github.io/pl-dashboard/pl-dashboard-v8.html**

Bookmark it. This is the only URL you'll ever need.

### Step 2 — Install it as an app (recommended)

Treating it like a real app means it works offline, has its own icon, and
launches in a clean window without browser tabs.

**On Windows / Mac / Linux (Chrome, Edge, Brave):**
1. With the dashboard open, look for an **Install** icon in the address bar
   (a little monitor with a down-arrow, or a "+" sign).
2. Click it → confirm. The app appears in your Start menu / Applications.

**On Android (Chrome, Edge, Samsung Internet, Brave):**
1. Tap the browser's **⋮** menu.
2. Tap **Add to Home Screen** or **Install app**.
3. Confirm. The app icon appears on your home screen.

**On iPhone / iPad (Safari):**
1. Tap the **Share** button (square with up-arrow) at the bottom of Safari.
2. Scroll down and tap **Add to Home Screen**.
3. Tap **Add**. The app icon appears on your home screen.

After installing, **always launch the app from the icon**, not from a
browser tab. This keeps your data safe and makes the experience smoother.

---

## How your data is stored

| Where | What | When |
|---|---|---|
| **Your device** (IndexedDB) | Every transaction, category, and setting | Saved instantly with every edit |
| **Browser localStorage** (your device) | Up to 5 recent automatic snapshots, app settings | Every few seconds while you work |
| **A file on your computer** (Layer 2 — optional) | A live `.csv` or `.xlsx` you choose | Updated automatically every 30 minutes |
| **Google Sheets** (Layer 3 — optional) | A full mirror in your own Google Drive | Auto-synced if you enable it (recommended) |

**Important:** Your financial data **never goes to our servers**. The app
runs entirely in your browser. The only third parties involved are:
- **Google** (only if you enable Sheets sync — only to your own account)
- **Supabase** (only for the license check on app start — no transaction data)

---

## What works without internet

Once the app is installed (or you've visited the URL once while online),
**everything except Google Sheets sync works offline**:

| Feature | Online | Offline |
|---|---|---|
| Add / edit / delete transactions | ✅ | ✅ |
| Import CSV or Excel files | ✅ | ✅ |
| Charts, dashboards, monthly P&L | ✅ | ✅ |
| Categories | ✅ | ✅ |
| Export to CSV / Excel / JSON | ✅ | ✅ |
| Layer 1 backup (snapshots) | ✅ | ✅ |
| Layer 2 backup (linked local file) | ✅ | ✅ |
| Layer 3 backup (Google Sheets) | ✅ | ⏳ Queued — syncs automatically when you reconnect |

**When you're offline:** A small "Offline" notice appears. Keep working
normally — all changes are saved to your device. When the internet comes
back, the app **automatically** pushes your changes to Google Sheets. You
don't need to remember anything or click any buttons.

**One thing to know:** if you close the app while offline before
reconnecting, your changes still aren't lost — they're in your local
database. Next time you open the app while online, they sync.

---

## Multi-device setup

Yes, you can use the app on your phone, tablet, and laptop with all the
same data. Here's how:

### One-time setup (per device, ~1 minute each)

1. Install the app on each device (Quick start, above).
2. On the **first** device:
   - Open the app → **Backup** tab → **Connect Google Sheets**.
   - Sign in with your Google account.
   - Choose **Create New Sheet** (or **Link Existing Sheet** if you
     already made one elsewhere).
   - Check the **Auto-sync to Google Sheets** box.
3. On **each additional device**:
   - Open the app → **Backup** tab → **Connect Google Sheets**.
   - Sign in with the **same Google account**.
   - Choose **Link Existing Sheet** and pick the Sheet you just created.
   - Check the **Auto-sync to Google Sheets** box.

### Daily flow

- Edit data on any device → it syncs to Sheets automatically within ~3 seconds.
- Switch to another device → it pulls the latest data within ~60 seconds,
  or instantly when you bring the app to the foreground.
- No buttons to press. It just works.

### Manual sync (if you ever need it)

The **Push** and **Pull** buttons are always available in the Backup tab.
Use them when you want immediate confirmation that sync happened.

---

## Best practices

1. **Always use the installed app icon, not a browser tab.** Browsers
   sometimes clean up data from random tabs. Installed apps are protected.

2. **Enable Auto-sync to Google Sheets on every device.** It's the
   simplest way to have a safety net and to use the app across devices.

3. **Use the same Google account everywhere.** If you sign into different
   Google accounts on different devices, they sync to different Sheets and
   the data won't match up.

4. **Set up Layer 2 (linked local file) on your main computer.** Backup tab
   → **Link Local File** → pick a folder. The app saves a CSV or Excel
   copy automatically every 30 minutes. If anything ever goes wrong with
   your browser, you have a real file.

5. **Export a JSON backup once a month.** Settings tab → **Export JSON**.
   Save it somewhere safe (Dropbox, iCloud, USB drive). This is your
   "everything in one file" emergency restore.

6. **Don't edit the same transaction on two devices in the same minute.**
   If you do, the most recent edit wins — the other gets overwritten when
   sync runs. Edit on one device at a time, let it sync, then switch.

7. **Open the app at least once a week on iOS.** Apple deletes data from
   web apps that haven't been opened for 7 days. Once-a-week use keeps
   your data safe. (Auto-sync to Sheets makes this less critical, since
   Sheets is the backup of last resort.)

8. **Check Layer 1 snapshot count.** Backup tab shows recent snapshots.
   If you ever make a wrong import or mass-delete, click **Restore** on
   the last good snapshot — your data comes back exactly as it was.

9. **Use the search/filter on the Transactions tab.** With more than a
   few hundred transactions, scrolling is painful. The filter is fast.

---

## Things to avoid

These are the patterns that cause problems. Avoid them.

❌ **Don't open the app in "Private Browsing" / "Incognito" mode.**
Private mode disables long-term storage. Anything you enter will vanish
when you close the window. You'll see a "Storage Unavailable" message if
this happens — switch to a normal window.

❌ **Don't clear "site data" for `apatel85.github.io` in your browser.**
This deletes all your local transactions. The Sheets backup will still
have them if you enabled it, but Layer 1 snapshots will be gone.

❌ **Don't have two devices simultaneously editing the same transaction.**
The app uses "last-write-wins" — whichever sync happens later overwrites
the earlier one. For collaboration, agree on who edits when.

❌ **Don't paste suspicious CSV files from unknown sources.** The app
sanitizes against most attacks, but a malicious file could try to confuse
you about what your data shows. If you didn't make the file yourself, open
it in Excel first to inspect.

❌ **Don't disable Sheets sync after relying on it.** If you turn off
auto-sync on a device and then make changes only there, those changes
won't appear on your other devices until you turn sync back on or
manually click Push.

❌ **Don't delete the linked Google Sheet from Google Drive while the app
is syncing.** Click **Unlink** in the Backup tab first, then delete.

❌ **Don't manually edit the linked Google Sheet's structure** (renaming
columns, deleting the header row, changing column order). The app expects
a specific layout. Editing values inside cells is fine — the app reads
that back on the next pull.

❌ **Don't import the same CSV twice.** Each row gets a unique ID at
import time, so duplicates aren't detected automatically. You'll just end
up with double entries. If you re-import, **clear the previous import
first** via Settings → **Clear All Data** (with caution, see below).

❌ **Don't tap "Clear All Data" without a backup.** The app double-prompts
you, but it's still permanent. Before clearing: Export JSON, or confirm
Sheets has your latest data, or take a fresh snapshot.

---

## Troubleshooting

### "I don't see my data on my other device."

1. Confirm both devices show the **same Google account** in the Backup tab.
2. Confirm both devices show **Connected** under Google Sheets and have
   the same Sheet name.
3. On the device that has the data, click **Push** manually.
4. On the device that's missing data, click **Pull** manually.
5. If still missing: open the linked Google Sheet directly in a browser —
   the data should be there. If not, sync isn't running on the device that
   has the data.

### "Auto-sync isn't running."

1. Backup tab — confirm the **Auto-sync to Google Sheets** checkbox is on.
2. Confirm you're signed in (Backup tab should show "Connected to Google
   Sheets" in green).
3. If signed out, click **Connect Google Sheets** again and re-enable the
   checkbox.

### "I'm offline but worried I'll lose changes."

You won't. Every edit is saved to your device's IndexedDB the moment you
make it. When you reconnect to the internet, the app automatically syncs.
You'll see a small "Back online — syncing…" notification.

If you want extra reassurance, click **Backup tab → Snapshot Now** before
going offline. That makes an explicit save you can roll back to.

### "Charts look broken / blank."

- Refresh the app (Cmd+R or Ctrl+R, or pull-to-refresh on mobile).
- If still broken: Settings tab → **Export JSON** (to save your data) →
  close and reopen the app.

### "I got a 'Storage Unavailable' error page."

Your browser is blocking the database. Causes:
- You opened the app in Private/Incognito mode (switch to normal window).
- Your browser is full (clear some space, then reopen).
- Firefox sometimes blocks IndexedDB on Windows — try Chrome or Edge.

### "I see a 'New version available — refresh to update' message."

A new app update was published. Save any in-progress work, refresh, and
you'll get the latest version. Your data is unaffected.

### "Sheets sync fails with 401 error."

Your Google sign-in expired. Backup tab → click **Sign in to Google**
again. Auto-sync will resume automatically.

---

## Privacy & security

- **Where is my data?** On your device, in your browser's IndexedDB. If
  you enable Sheets sync, also in your own Google Sheet in your own Drive.
  Nowhere else.

- **Who can see my data?**
  - On your device: anyone with access to your unlocked device and your
    browser profile.
  - In Google Sheets: anyone you share the Sheet with (you control this).
  - The app developer: never. We don't have a backend that receives
    transaction data.

- **What does the license check send?** Only your email and license key,
  to verify you're authorized to use the app. No transaction data.

- **Should I trust the auto-sync?** The OAuth flow is Google's standard
  consent screen. You'll see exactly which permissions the app is asking
  for. The app only requests permission for the specific Sheet it creates
  — not your whole Drive.

- **What if my laptop is stolen?** Your transactions are on the laptop's
  disk (encrypted if you have disk encryption enabled — which you should).
  Your linked Google Sheet is still safe in your own Google account.
  Sign out of Google on the stolen device remotely from your Google
  account settings.

---

## Backup recovery (worst-case scenarios)

If your data goes wrong, you can recover from any of these in order:

1. **Layer 1 — Browser snapshot.** Backup tab → click **Restore** on the
   most recent good snapshot. Instant.

2. **Layer 2 — Linked local file.** Backup tab → re-link the file on disk
   → Settings tab → **Import**. Restores from a few minutes ago at most.

3. **Layer 3 — Google Sheets.** Backup tab → click **Pull**. Restores
   whatever was last synced (usually seconds-old).

4. **JSON export.** Settings tab → **Import JSON** → pick your last manual
   export. Restores to whenever you exported.

5. **Disaster.** If all of the above are gone: rebuild from your bank
   statements / receipts / Quickbooks export.

---

## One-page cheat sheet

- **Open:** `https://apatel85.github.io/pl-dashboard/pl-dashboard-v8.html`
- **Install:** browser address bar Install icon, or Share → Add to Home
  Screen
- **First device:** Backup → Connect Google Sheets → Create New Sheet →
  enable Auto-sync
- **Other devices:** Backup → Connect Google Sheets → Link Existing Sheet
  → enable Auto-sync
- **Offline:** keep working — syncs automatically when online
- **Worried about losing data:** Settings → Export JSON, save the file
- **Recover from a mistake:** Backup → Snapshots → Restore
- **Need help:** check Troubleshooting section above
