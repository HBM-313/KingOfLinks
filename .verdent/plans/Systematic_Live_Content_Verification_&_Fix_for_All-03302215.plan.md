## Plan Comparison

Three approaches were evaluated:

| Aspect | Plan A (Granular Scripts) | Plan B (Library Modules) | Plan C (Resumable Pipeline) |
|--------|--------------------------|--------------------------|----------------------------|
| **Script count** | 8+ scripts | 7 modules | 5 scripts |
| **Live block parsing** | Font-color walking (RED tags) | Font-color + color scheme | HR-tag splitting |
| **Fix classification** | Binary (auto/manual) | 4 fix types (A-D) | 5-tier system |
| **Manual review** | audit.md logging | HTML diff files | Console queue printer |
| **Resumability** | None explicit | None explicit | Progress JSON tracker |
| **Pros** | Most granular separation | Best block alignment algo, audit trail markers | Simplest, crash-safe |
| **Cons** | Too many scripts to manage | Over-engineered for garbled text | HR splitting may miss edge cases |

**Recommendation:** Hybrid approach — Plan C's simplicity and resumability + Plan B's numeric_signature alignment + Plan A's final sweep verification. Use HR-splitting as primary with font-color fallback.

---

## Phase 0: Setup & Inventory

### Step 0.1: Create `build_inventory.py`
Parse `sitemap.xml` → produce `_url_map.json` mapping every live URL to local file path.

- Extract all `<loc>` URLs from sitemap
- Filter out `Main*.htm` (navigation pages) and root `index.htm`
- URL-decode paths (handle `%20` → space)
- Map `.htm` → `.html`, preserve folder structure
- Check `exists_locally` for each mapping
- Output: `_url_map.json` + initial `migration_audit.md` table

**Targets:** `sitemap.xml` → NEW `build_inventory.py` → NEW `_url_map.json` + NEW `migration_audit.md`

### Step 0.2: Fetch & Cache All Live Pages
Create `fetch_all.py` — fetch every content URL → store raw bytes in `_live_cache/`.

- Use existing `fetch_live()` pattern from `fetch_detail.py`
- 0.5s delay between fetches (~17 min for ~2000 pages)
- Store as raw bytes (NOT decoded) in `_live_cache/{folder}/{file}.htm`
- Skip already-cached files (resume-safe)
- Track progress in `_verify_progress.json` (save every 10 files)
- Run: `python -X utf8 fetch_all.py`

**Targets:** NEW `fetch_all.py`, NEW `_live_cache/**/*.htm`

### Step 0.3: Reset Progress Tracking
- Reset `process.md`: all `[x]` → `[ ]`
- Add "content-verified" note to distinguish from structural-only checks

---

## Phase 1: Audit (Per-Folder)

### Step 1.1: Create `verify_content.py`
Comparison engine: for each page, compare live blocks vs local blocks.

```
For each file in _url_map.json (grouped by folder):
  1. Read cached live page (open 'rb' → decode 'windows-1256')
  2. Parse local .html with BeautifulSoup
  3. Count live blocks (HR-split, fallback to الجزء count)
  4. Count local hadith-blocks
  5. Extract numeric signatures from both:
     - Live: (juz, page, hadith_num) per block
     - Local: ref-value spans + hadith-number spans
  6. Compare: block count + numeric alignment
  7. Classify:
     - OK: counts match, numbers align
     - REF_MISMATCH: counts match, numbers differ
     - MISSING_BLOCKS: live > local
     - EXTRA_BLOCKS: local > live (flag, never delete)
     - NEEDS_MANUAL: can't align
  8. Check hadith-text non-empty for each local block
  9. Write results to migration_audit.md + _audit_results.json
```

**Arabic readability heuristic** (for deciding auto-fix vs manual):
```python
def is_arabic_readable(text):
    replacements = text.count('\ufffd')
    arabic = len(re.findall(r'[\u0600-\u06ff]', text))
    return replacements < 10 and arabic > 20
```

**Targets:** NEW `verify_content.py`, UPDATED `migration_audit.md`

### Step 1.2: Run Audit on ALL Folders
```powershell
python -X utf8 verify_content.py
```
Output: per-folder summary showing OK / REF_MISMATCH / MISSING_BLOCKS / NEEDS_MANUAL counts.

---

## Phase 2: Fix Content Gaps (Per-Folder, Alphabetical)

### Step 2.1: Create `fix_content_gaps.py`
Tiered fix logic per classification:

| Tier | Issue | Action |
|------|-------|--------|
| TIER-1 | `MISSING_BLOCKS` (live > local) | Insert skeleton hadith-blocks with numbers from live; flag Arabic text as `NEEDS_ARABIC_PASTE` if garbled |
| TIER-2 | `EXTRA_BLOCKS` (local > live) | FLAG only, never auto-delete |
| TIER-3 | `REF_MISMATCH` | Auto-correct juz/page ref values from live (after scholar/book match verification) |
| TIER-4 | `MISSING_HADITH_TEXT` | Auto-fill if Arabic is readable from live cache; else flag `NEEDS_ARABIC_PASTE` |
| TIER-5 | `OK` | No action, mark VERIFIED |

**Safety rules:**
- NEVER apply data from one file's live page to a different file's blocks
- Verify live_url matches expected URL before ANY write
- Write with `str(soup)` (NOT `soup.prettify()`)
- Add `<!-- content-verified-from-live -->` comment as audit trail

### Step 2.2: Per-Folder Execution Workflow
For each folder (alphabetical order):

1. `python -X utf8 verify_content.py --folder <FolderName>` → identify gaps
2. `python -X utf8 fix_content_gaps.py --folder <FolderName>` → apply safe fixes
3. `python -X utf8 verify_content.py --folder <FolderName>` → re-verify
4. `python -X utf8 inspect_folder.py <FolderName>` → confirm no structural regressions
5. Manual review for NEEDS_MANUAL / NEEDS_ARABIC_PASTE pages
6. `git add <folder>/ migration_audit.md && git commit -m "Verify+Fix <Folder>: content matched against live pages"`
7. **DO NOT move to next folder until current is fully clean**

**Large folders (ImamAli: 670 files, Mkhalfoon: 434 files):** commit by subfolder.

---

## Phase 3: Final Sweep

### Step 3.1: Full Re-Verification
After all folders processed:
```powershell
python -X utf8 verify_content.py --all
```
Confirm every page in `_url_map.json` has status `VERIFIED` or documented `BLOCKED` with reason.

### Step 3.2: Structural Regression Check
```powershell
foreach ($f in @('Abawalnabi','Abdulmtalib','Abutalib','AhlAlBait','Aqydatona','Bhooth','Daeefa','Fatima','Hywan','ImamAli','ImamHasan','ImamHussain','ImamMahdi','Mkhalfoon','NabiMohd','RAG','RS','Seerah','SwR','Threef','Tjseem')) {
    python -X utf8 inspect_folder.py $f 2>&1 | Select-String "ALL CLEAN|ISSUES"
}
```

### Step 3.3: Final Audit Summary
Update `migration_audit.md` with:
- Total pages: verified / blocked / manual-review
- Per-folder breakdown
- List of all BLOCKED pages with exact reasons

---

## Verification / DoD

| Criterion | Verification Method |
|-----------|-------------------|
| Every sitemap URL has a local file | `_url_map.json` `exists_locally` check |
| Block count matches live for every file | `verify_content.py` output: all OK or documented |
| Every ref-info has both الجزء and الصفحة | `inspect_folder.py` MISSING_PAGE check |
| Every hadith-text non-empty when live has content | `verify_content.py` MISSING_HADITH_TEXT check |
| No structural regressions | `inspect_folder.py` ALL CLEAN per folder |
| All progress tracked | `migration_audit.md` complete |
| No data from wrong page applied | Fix script URL verification assertions |

## Step → Targets → Verification Traceability

| Step | Targets | Verification |
|------|---------|-------------|
| 0.1 | `build_inventory.py`, `_url_map.json`, `migration_audit.md` | All sitemap URLs mapped, exists_locally checked |
| 0.2 | `fetch_all.py`, `_live_cache/**/*.htm` | Cache count == content URL count |
| 1.1 | `verify_content.py` | Runs without error on sample folder |
| 2.1 | `fix_content_gaps.py` | Tier classification matches audit results |
| 2.2 | Per-folder HTML fixes | `verify_content.py` + `inspect_folder.py` both clean |
| 3.1 | Full sweep | All pages VERIFIED or BLOCKED |
| 3.3 | `migration_audit.md` | Complete summary with zero undocumented pages |
