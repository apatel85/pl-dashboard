> 📁 Moved to `review/ISSUES_LOG.md` (was at root)

# ISSUES_LOG.md — pl-dashboard-v8.html

**Generated:** 2026-05-13
**Last updated:** 2026-05-19 — most issues resolved, see Status column.
**Reviewed by:** Claude Sonnet 4.6
**Method:** Static analysis + logic simulation + stress testing per REVIEW_PLAN.md
**File:** pl-dashboard-v8.html (4,190 lines)

---

## Summary Table

| Issue | Severity | Type | Short Title | Status |
|---|---|---|---|---|
| ISSUE-001 | Critical | Security | XSS: renderRecentEntries — date/category/description unescaped | ✅ Resolved (FIX-001) |
| ISSUE-002 | Critical | Security | XSS: renderRevTable — category/description unescaped | ✅ Resolved (FIX-001) |
| ISSUE-003 | Critical | Security | XSS: renderExpTable — category/description unescaped | ✅ Resolved (FIX-001) |
| ISSUE-004 | Critical | Security | XSS: openMappingModal — CSV headers raw in innerHTML | ✅ Resolved (FIX-002) |
| ISSUE-005 | Critical | Security | XSS: openMappingModal — CSV data cells raw in innerHTML | ✅ Resolved (FIX-002) |
| ISSUE-006 | Critical | Security | XSS: catPillHTML — name rendered raw, `safe` var unused | ✅ Resolved (FIX-003) |
| ISSUE-007 | Critical | Security | No Content-Security-Policy meta tag | ✅ Resolved (FIX-004) |
| ISSUE-008 | High | Security | CSV formula injection not sanitized on export | ✅ Resolved (FIX-005) |
| ISSUE-009 | High | Security | No SRI integrity attribute on Chart.js and XLSX.js CDN scripts | ✅ Resolved (FIX-006 — libs inlined, no CDN) |
| ISSUE-010 | High | Performance | renderRevTable renders ALL rows with no pagination | ✅ Resolved (FIX-007) |
| ISSUE-011 | High | Performance | renderExpTable renders ALL rows with no pagination | ✅ Resolved (FIX-008) |
| ISSUE-012 | High | Data-loss | Snapshot localStorage overflow with >10k transactions | ✅ Resolved (FIX-009) |
| ISSUE-013 | Medium | Functional | Accounting-negative amounts `(99.00)` not parsed | ✅ Resolved (FIX-010) |
| ISSUE-014 | Medium | Functional | Ambiguous DD/MM/YYYY date format | ✅ Resolved (FIX-011) |
| ISSUE-015 | High | Security | XSS: toast() uses innerHTML with msg parameter | ✅ Resolved (FIX-012) |
| ISSUE-016 | Medium | Data-loss | Float arithmetic drift in KPI sums | ✅ Resolved (FIX-013) |
| ISSUE-017 | Medium | Functional | RFC 4180 escaped quotes not handled in parseCSV | ✅ Resolved (FIX-014) |
| ISSUE-018 | Medium | Functional | EU number format 1.234,56 silently miscoerces | ✅ Resolved (FIX-010) |
| ISSUE-019 | Medium | Functional | Monthly table col-4 mismatch (net vs gross) | ✅ Resolved (FIX-015) |
| ISSUE-020 | Medium | UX | inlineEdit error path: console.warn only, no user toast | ✅ Resolved (FIX-016) |
| ISSUE-021 | Medium | UX | Clear All Data uses single confirmation | ✅ Resolved (FIX-017) |
| ISSUE-022 | Medium | Data-loss | IndexedDB DB_VERSION=1 with no upgrade path | ⚠️ Open — schema is still v1; revisit before any future schema change |
| ISSUE-023 | Medium | Functional | No user-facing fallback if IndexedDB unavailable | ✅ Resolved (FIX-018) |
| ISSUE-024 | Medium | Performance | 100k row memory footprint ~61.7 MB | ⚠️ Open — acceptable for target scale; revisit if 1M-row use cases emerge |
| ISSUE-025 | Low | Accessibility | Toast container missing role and aria-live | ✅ Resolved (FIX-019) |
| ISSUE-026 | Low | Accessibility | Icon-only buttons missing aria-label | ✅ Resolved (FIX-020) |
| ISSUE-027 | Info | Security | Supabase anon key hardcoded (verify RLS) | ℹ️ Info — no action; RLS verified, intended pattern |
| ISSUE-028 | Info | Code-quality | Multiple functions >80 LOC | ℹ️ Info — no action; tracked for future refactor |
| ISSUE-029 | Info | Code-quality | Magic strings repeated throughout | ℹ️ Info — no action; tracked for future refactor |
| ISSUE-030 | Info | Code-quality | Duplicate rendering patterns | ℹ️ Info — no action; tracked for future refactor |

**Severity counts:** Critical: 7 | High: 5 | Medium: 9 | Low: 2 | Info: 4
**Status counts:** Resolved: 21 | Open: 2 | Info — no action: 7
**Total issues: 30**

*Full details for each issue (evidence, steps to reproduce, line numbers) are documented in the original ISSUES_LOG.md. See `review/FIXES.md` for the auto-applyable patches.*
