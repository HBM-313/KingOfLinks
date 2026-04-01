## Plan Comparison

| Aspect | Plan 1 (Claude) | Plan 2 (GPT-5) | Plan 3 (Gemini) |
|--------|-----------------|-----------------|-----------------|
| Script location | Audit.md only | Handoff.md + Guide.md | Handoff.md + Guide.md |
| Startup checklist | No explicit | 5-step mandatory | 5-step mandatory |
| Folder-specific | Brief | Most detailed (6 subsections) | CSS depth table |
| Unique strength | Data injection warning, end-of-folder script | Threef exception, per-page checklist | ASCII repo layout, detection regex |

**Selected**: Hybrid — scripts in `Handoff.md` (self-contained) + `Guide.md` (reference). Plan 2's startup checklist + Plan 1's data injection warning + Plan 3's architecture section.

---

## Content Allocation (No Duplication)

| Content | Handoff | Audit | Guide |
|---------|:-------:|:-----:|:-----:|
| Startup checklist + repo info | X | | |
| `fetch_live()` full code | X | | |
| `inspect_folder.py` full code | X | | ref |
| `verify_content.py` full code | X | | ref |
| Non-negotiable rules (18) | X | | |
| Workflow per folder | X | | |
| Response format / escalation | X | | |
| Folder completion table | summary | full | |
| Issue code definitions | | X | |
| SPECIAL_PAGES registry | | X | |
| Per-folder known issues | | X | |
| Verification procedures | | X | |
| Session progress log | | X | |
| Data files (`_live_cache`, `_url_map`) | brief | full | |
| Page structure types 1-4 | | | X |
| Field rules (strict) | | | X |
| Fix patterns + code examples | | | X |
| Scholar disambiguation tables | | | X |
| CSS class reference | | | X |
| Helper functions | | | X |

---

## Phase 1: Write `Handoff.md`

Self-contained session startup document. A new AI session pastes ONLY this and can begin.

### Sections:
1. **CRITICAL BANNER** — "ALL content is from live pages. Never assume. Always ask."
2. **Environment** — repo URL, branch, worktree path, platform, encoding
3. **Startup Checklist** (mandatory 5 steps)
   - `git status` + `git log --oneline -5`
   - Read `process.md` (folder progress)
   - Read `Audit.md` (known issues, special pages)
   - Read `Guide.md` (page structures)
   - Create scripts from code blocks below
4. **Live Fetch Function** — full `fetch_live()` code + cache lookup helper + `extract_page_numbers()`
5. **Script: `inspect_folder.py`** — full source (reconstructed from `handoff.md` L526-585 + inspect_folder.py as we had it)
6. **Script: `verify_content.py`** — full source (reconstructed with SPECIAL_PAGES support)
7. **Script Lifecycle Rule** — "Delete ALL .py files when done. Recreate from this doc next session."
8. **Non-Negotiable Rules** — all 18 rules from `handoff.md` L139-158, plus:
   - "ALL content must come from live pages"
   - "Work one page at a time"
   - "If confused or something new, STOP and ASK"
   - "If a live page has a structure you haven't seen, ASK the user"
   - "Never use WebFetch for kingoflinks.net"
9. **Workflow Per Folder** (9 steps)
   - Fetch/verify live cache for folder
   - Run `inspect_folder.py`
   - For each page: fetch live, compare block-by-block, fix
   - Run `inspect_folder.py` again
   - Run `verify_content.py`
   - Commit with descriptive message
   - Delete .py scripts
10. **Task Lock Rule** — from `handoff.md` L162-182
11. **Current Progress** — summary table (5 done, 18 remaining) + "See `process.md` for full detail"
12. **Commit Convention** — `"Verify+Fix FolderName: description (N files)"`
13. **Response Format** — field mapping template from `handoff.md` L835-878
14. **Problem Escalation** — 8-point report template from `handoff.md` L795-812
15. **Done Rule** — from `handoff.md` L815-832
16. **Failsafe** — from `handoff.md` L883-903

**Source files**: `handoff.md` (full), `.agents/rules/guide.md` (rules), `process.md` (progress)

---

## Phase 2: Write `Audit.md`

Project state, verification procedures, known issues.

### Sections:
1. **CRITICAL BANNER** — same as Handoff
2. **Project Status Summary** — total pages (~1994), completed folders (5), remaining (18), last commit
3. **Completed Folders** — full table with subfolder detail (from `process.md`)
4. **Remaining Folders** — table with subfolder listing
5. **Issue Code Registry** — full table of all 16+ issue codes:
   - BOOK_AS_SN, SN_EQ_BT, COMBINED_BT, HADITH_IN_CI, UNWRAPPED_EDITORIAL, FLOATING_NOTE, LOOSE_P, FOOTNOTES_SECTION, MISSING_PAGE, EMPTY_SN, NUMBER_IN_SN, EDITORIAL_IN_SN, NOTE_AS_SN, NESTED_SN_IN_BI, BT_IN_HT, FRAG_ANALYSIS, DUP_SN
   - Each with: code, meaning, detection pattern, fix approach
6. **Special Pages Registry** — table of pages that don't follow standard structure
   - `Aqydatona/8ZQ/24ZQ.html` — Type 2 (12 evidence blocks)
   - `Aqydatona/12Mutaah/11Albani.html` — Type 3 (hadith-number-only)
7. **Data Files**
   - `_live_cache/` — structure, encoding, purpose
   - `_url_map.json` — format, usage
   - `_audit_results.json` — schema
   - `process.md` — authoritative progress tracker
8. **Verification Procedures**
   - How to run `inspect_folder.py`
   - How to run `verify_content.py`
   - SPECIAL_PAGES handling
   - Manual per-page checklist (10 checkboxes)
   - End-of-folder checklist
9. **Per-Folder Known Issues** — from `Guide1.md` L228-420 (cleaned, no garbled Arabic)
10. **Session Progress Log** — template for logging what was done per session
11. **Known Blockers / Data Injection Warning** — never apply data from one file to another

**Source files**: `AUDIT.md` (full), `Guide1.md` L228-420 (per-folder issues), `handoff.md` (issue codes)

---

## Phase 3: Write `Guide.md`

Complete structural encyclopedia.

### Sections:
1. **CRITICAL BANNER** — same as Handoff
2. **Project Architecture**
   - ASCII repo layout tree
   - CSS path depth table (1-level: `../modern.css`, 2-level: `../../`, 3-level: `../../../`)
   - Encoding: Windows-1256, .htm vs .html
3. **Global Page Structure (Type 1: Standard)**
   - Full HTML template with ALL semantic classes
   - Annotated field-by-field explanation
   - Example: `Aqydatona/1Wodooa.html`
4. **Special Page: Type 2 — Collection/Evidence**
   - Structure: SN = `( N )`, no book-info/ref-info, hadith-text + analysis-note
   - Example: `Aqydatona/8ZQ/24ZQ.html`
   - Sources in analysis-note with `<br>` separators
5. **Special Page: Type 3 — Hadith-Number-Only**
   - Structure: الصفحة holds hadith number, no الجزء
   - Example: `Aqydatona/12Mutaah/11Albani.html`
6. **Special Page: Type 4 — Non-Sunni Source Note**
   - Structure: analysis-note with "هذا المصدر ليس من المصادر السنية..."
   - Example: `Aqydatona/17Laen/4.html` block 22
7. **UNKNOWN STRUCTURES — STOP AND ASK**
   - If a live page has a structure not matching Types 1-4, STOP
   - Ask the user to describe the structure
   - Never assume or force-fit
8. **Field Rules (Strict)** — all 8 fields with full rules from `handoff.md` L240-345
9. **Fix Patterns Reference** — from `handoff.md` L590-655
   - COMBINED_BT split logic + chapter-detection keywords
   - BOOK_AS_SN fix
   - HADITH_IN_CI move
   - UNWRAPPED_EDITORIAL wrap
   - FLOATING_NOTE move
   - LOOSE_P / FOOTNOTES_SECTION
   - EDITORIAL_IN_SN fix
10. **Scholar Disambiguation Tables** — from `AUDIT.md` L293-328
    - ابن حجر العسقلاني, الذهبي, البيهقي, الطبري vs المحب الطبري
    - الطبراني volume rule
11. **Approved Typo Fixes** — from `handoff.md` L651-655
12. **Folder-Specific Patterns**
    - Threef: BOOK_AS_SN is intentional (not an error)
    - Mkhalfoon: 3-level nesting
    - ImamAli: deep subfolders, mixed sources
13. **CSS Class Reference** — full table from `modern.css`
14. **Helper Python Functions** — `add_page()`, `fix_vol()`, `wrap_editorial()` from `handoff.md` L662-692
15. **Data Injection Warning** — never copy data from one file to another's blocks

**Source files**: `handoff.md` (field rules, fix patterns, helpers), `AUDIT.md` (disambiguation), `modern.css` (classes), example HTML files

---

## Phase 4: Cleanup

1. Delete old files: `handoff.md`, `Guide1.md`
   - Note: check if `AUDIT.md` exists (may have been deleted); if so, no need to delete
2. Keep: `process.md`, `migration_audit.md`, `.agents/rules/guide.md`
3. Verify cross-references between the 3 new docs are correct

---

## Verification / DoD

| Criterion | Method |
|-----------|--------|
| Handoff.md is self-contained | New session reading ONLY it can start work |
| Scripts compile | Python syntax check on embedded code |
| No content duplication | Each key concept in exactly one doc |
| All 4 page types documented | Guide.md has full examples |
| All 16+ issue codes listed | Audit.md has complete registry |
| SPECIAL_PAGES documented | Both Audit.md and verify_content.py |
| "Always ask" rule prominent | Banner in all 3 docs |
| Cross-references valid | Every "See X" points to real heading |

## Step -> Targets -> Verification

| Step | Targets | Verification |
|------|---------|-------------|
| Phase 1 | `Handoff.md` | Self-contained, scripts valid |
| Phase 2 | `Audit.md` | All issue codes, folder status |
| Phase 3 | `Guide.md` | All 4 page types, field rules |
| Phase 4 | Delete old docs | `handoff.md`, `Guide1.md` removed |
