#!/usr/bin/env python3
"""
build-offline.py — Generate a fully self-contained offline version of pl-dashboard-v8.html

What it does:
  1. Reads pl-dashboard-v8.html (the online version).
  2. Downloads or reuses Chart.js + XLSX.js from npm (CDN may be blocked).
  3. Inlines both libraries directly into the HTML <head>.
  4. Strips the Google Fonts @import (falls back to system fonts offline).
  5. Tightens the Content-Security-Policy (no longer needs cdnjs.cloudflare.com).
  6. Writes pl-dashboard-v8-offline.html.

Run from repo root:
  python3 build-offline.py

Output:
  pl-dashboard-v8-offline.html — single self-contained file, works offline.

Requirements:
  - Python 3.7+
  - npm (only the first time, to fetch libraries)
"""

import re
import os
import sys
import subprocess
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SOURCE = REPO_ROOT / "pl-dashboard-v8.html"
OUTPUT = REPO_ROOT / "pl-dashboard-v8-offline.html"
VENDOR = REPO_ROOT / "vendor"

CHART_PKG = "chart.js@4.4.1"
CHART_PATH_IN_TARBALL = "package/dist/chart.umd.js"
CHART_LOCAL = VENDOR / "chart.umd.js"

XLSX_PKG = "xlsx@0.18.5"
XLSX_PATH_IN_TARBALL = "package/dist/xlsx.full.min.js"
XLSX_LOCAL = VENDOR / "xlsx.full.min.js"


def fetch_from_npm(pkg, path_in_tarball, dest):
    """Use npm pack to download package, extract one file, save to dest."""
    if dest.exists():
        print(f"[cache] {dest.name} already present, skipping download")
        return
    print(f"[npm]   fetching {pkg}...")
    VENDOR.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tdpath = Path(td)
        result = subprocess.run(
            ["npm", "pack", pkg, "--silent"],
            cwd=tdpath, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"npm pack failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        tarball = next(tdpath.glob("*.tgz"))
        with tarfile.open(tarball, "r:gz") as tf:
            member = tf.getmember(path_in_tarball)
            f = tf.extractfile(member)
            dest.write_bytes(f.read())
    print(f"[ok]    saved {dest.name} ({dest.stat().st_size:,} bytes)")


def build():
    if not SOURCE.exists():
        print(f"error: {SOURCE} not found", file=sys.stderr)
        sys.exit(1)

    fetch_from_npm(CHART_PKG, CHART_PATH_IN_TARBALL, CHART_LOCAL)
    fetch_from_npm(XLSX_PKG, XLSX_PATH_IN_TARBALL, XLSX_LOCAL)

    html = SOURCE.read_text(encoding="utf-8")
    chart_js = CHART_LOCAL.read_text(encoding="utf-8")
    xlsx_js = XLSX_LOCAL.read_text(encoding="utf-8")

    # 1. Replace the two external CDN script tags with inline blocks.
    chart_tag_re = re.compile(
        r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/Chart\.js/[^"]+"[^>]*></script>'
    )
    xlsx_tag_re = re.compile(
        r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/xlsx/[^"]+"[^>]*></script>'
    )
    if not chart_tag_re.search(html):
        print("error: Chart.js script tag not found", file=sys.stderr); sys.exit(1)
    if not xlsx_tag_re.search(html):
        print("error: XLSX script tag not found", file=sys.stderr); sys.exit(1)

    chart_block = "<script>/* Chart.js 4.4.1 (inlined for offline use) */\n" + chart_js + "\n</script>"
    xlsx_block  = "<script>/* SheetJS xlsx 0.18.5 (inlined for offline use) */\n" + xlsx_js + "\n</script>"
    html = chart_tag_re.sub(lambda m: chart_block, html, count=1)
    html = xlsx_tag_re.sub(lambda m: xlsx_block, html, count=1)

    # 2. Strip Google Fonts @import — falls back to system fonts when offline.
    html = re.sub(
        r"@import url\('https://fonts\.googleapis\.com[^']+'\);",
        "/* Google Fonts @import removed — offline build uses system fonts */",
        html
    )

    # 3. Tighten CSP: no external scripts/styles/fonts needed now.
    new_csp = (
        '<meta http-equiv="Content-Security-Policy" content="'
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://accounts.google.com https://apis.google.com; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
        "img-src 'self' data:; "
        "connect-src 'self' https://iknfvddnevudpjtyxkbh.supabase.co https://sheets.googleapis.com https://accounts.google.com; "
        "frame-src 'none'; "
        'object-src \'none\';">'
    )
    html = re.sub(
        r'<meta http-equiv="Content-Security-Policy"[^>]*>',
        new_csp, html, count=1
    )

    # 4. Add an offline-build banner in <title>.
    html = html.replace(
        "<title>P&L Dashboard — Business Finance Tracker</title>",
        "<title>P&L Dashboard (Offline) — Business Finance Tracker</title>",
        1
    )

    OUTPUT.write_text(html, encoding="utf-8")
    size_kb = OUTPUT.stat().st_size / 1024
    print(f"[done]  wrote {OUTPUT.name} ({size_kb:,.1f} KB)")
    print("        Open this file directly in Chrome/Edge — works without internet.")


if __name__ == "__main__":
    build()
