# KingOfLinks — Session Handoff Prompt

> **!!! CRITICAL — READ THIS FIRST !!!**
> ALL content MUST come from LIVE PAGES. Never assume, never invent, never guess.
> If confused or something is new — **STOP AND ASK** the user.
> If a live page has a structure you haven't seen before — **STOP AND ASK** the user.
> Never use WebFetch / web_fetch for `kingoflinks.net`. Use Python `urllib` only.

---

## 1. Environment

- **Repo**: https://github.com/HBM-313/KingOfLinks.git
- **Branch**: `Verdentai` (base: `main`)
- **Worktree**: `C:\xampp\htdocs\AlQanas2\KingOfLinks\.worktrees\Verdentai`
- **Platform**: Windows 10 / PowerShell
- **Live site**: `http://kingoflinks.net/` (uses `.htm`; repo uses `.html`)
- **Encoding**: Windows-1256 (Arabic garbles on decode; **numbers always survive**)
- **CSS**: `modern.css` at repo root; pages link via relative path (`../`, `../../`, `../../../`)
- **Total pages**: ~1,994 HTML files across 23 folders

---

## 2. Startup Checklist (MANDATORY — do these 5 steps before ANY work)

1. `git status` + `git log --oneline -5` — know current state
2. Read `process.md` — folder completion progress
3. Read `Audit.md` — known issues, special pages, issue codes
4. Read `Guide.md` — page structures (Types 1-4), field rules, fix patterns
5. Create scripts from code blocks below (§4, §5, §6)

---

## 3. Live Fetch Function

```python
import urllib.request
import re

def fetch_live(path):
    """
    Fetch a live page from kingoflinks.net.
    path = folder/filename WITHOUT leading slash (e.g. 'Abutalib/9.htm')
    Repo uses .html — live site uses .htm
    Arabic text garbles (Windows-1256). Numbers ALWAYS survive.
    Returns: (url, raw_text)
    """
    url = f"http://kingoflinks.net/{path}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read()
    text = html.decode('windows-1256', errors='replace')
    return url, text

def extract_page_numbers(text):
    """Extract all ( N ) style numbers from a garbled live page."""
    return re.findall(r'\(\s*(\d+)\s*\)', text)

def extract_blocks(text):
    """Split live page into block sections by the --- separator."""
    return [b.strip() for b in text.split('---') if b.strip()]
```

### Live Cache

- `_live_cache/` folder mirrors live site structure (raw windows-1256 bytes as `.htm`)
- `_url_map.json` maps local `.html` paths to live `.htm` paths
- To use cache: read raw bytes, decode with `windows-1256`
- If cache is missing for a page, fetch live

### Matching live blocks to local blocks

Live blocks appear in the same order as local `hadith-block` elements. Match by:
- block position
- volume number
- page number
- hadith number (when present)

```python
# Extract (juz, page) pairs from live text
refs = re.findall(r'\(\s*(\d+)\s*\)[^\(]{1,60}\(\s*(\d+)\s*\)', content)
```

**Before applying any live data** to a local block, verify the local block's scholar, book, and volume match what the live page shows. If anything mismatches: **FLAG IT, DO NOT APPLY**.

---

## 4. Script: `inspect_folder.py`

Create this at repo root. Run: `python -X utf8 inspect_folder.py FolderName`

```python
from bs4 import BeautifulSoup, Tag
import os, re, sys

EDITORIAL = 'النص طويل لذا استقطع منه موضع الشاهد'
CI_HADITH = re.compile(r'^-\s*\d+\s*-\s*.{10,}')
NUMBER_ONLY = re.compile(r'^\s*[\d\u0660-\u0669]+\s*$')
GARBLED = re.compile(r'^م{1,3}$')
BOOK_NAMES = {'صحيح البخاري','صحيح مسلم','السنن الكبرى','المعجم الكبير','المعجم الأوسط',
              'المعجم الصغير','المستدرك على الصحيحين','مسند الامام أحمد بن حنبل',
              'صحيح ابن حبان','سير أعلام النبلاء','البداية والنهاية','تاريخ دمشق','كتاب السنة'}

folder = sys.argv[1] if len(sys.argv) > 1 else '.'
all_clean = True

for root, dirs, files in sorted(os.walk(folder)):
    for fn in sorted(files):
        if not fn.endswith('.html'): continue
        fp = os.path.join(root, fn)
        with open(fp, encoding='utf-8', errors='replace') as f:
            soup = BeautifulSoup(f, 'html.parser')
        issues = []
        ab = soup.find(class_='article-body')
        if ab:
            for child in ab.children:
                if isinstance(child, Tag):
                    if 'analysis-note' in (child.get('class') or []):
                        issues.append('FLOATING_NOTE')
                    if child.name == 'p':
                        issues.append(f'LOOSE_P: {child.get_text(strip=True)[:50]}')
        if soup.find('div', class_='footnotes-section'):
            issues.append('FOOTNOTES_SECTION')
        for i, blk in enumerate(soup.find_all('div', class_='hadith-block')):
            bn = f'b{i+1}'
            sn = blk.find('div', class_='scholar-name')
            bt = blk.find('span', class_='book-title')
            ref = blk.find('div', class_='ref-info')
            ht = blk.find('div', class_='hadith-text')
            sn_t = sn.get_text(strip=True) if sn else ''
            bt_t = bt.get_text(strip=True) if bt else ''
            if ref:
                labels = [s.get_text(strip=True) for s in ref.find_all('span', class_='ref-label')]
                if not any('الصفحة' in l for l in labels): issues.append(f'{bn} MISSING_PAGE')
            if not sn_t: issues.append(f'{bn} EMPTY_SN')
            elif NUMBER_ONLY.match(sn_t): issues.append(f'{bn} NUMBER_IN_SN: {sn_t}')
            elif GARBLED.match(sn_t): issues.append(f'{bn} GARBLED_SN: {sn_t}')
            elif sn_t in BOOK_NAMES: issues.append(f'{bn} BOOK_AS_SN: {sn_t}')
            elif EDITORIAL in sn_t: issues.append(f'{bn} EDITORIAL_IN_SN')
            if sn_t and sn_t == bt_t: issues.append(f'{bn} SN_EQ_BT: {sn_t}')
            if bt_t and ' -' in bt_t: issues.append(f'{bn} COMBINED_BT: {bt_t[:60]}')
            for ci in blk.find_all('span', class_='chapter-info'):
                if CI_HADITH.match(ci.get_text(strip=True)):
                    issues.append(f'{bn} HADITH_IN_CI: {ci.get_text(strip=True)[:50]}')
            if ht:
                for p in ht.find_all('p'):
                    if EDITORIAL in p.get_text(strip=True) and not p.find('span', class_='editorial-note'):
                        issues.append(f'{bn} UNWRAPPED_EDITORIAL')
            if len(blk.find_all('div', class_='analysis-note')) > 1:
                issues.append(f'{bn} FRAG_ANALYSIS')
            if len(blk.find_all('div', class_='scholar-name')) > 1:
                issues.append(f'{bn} DUP_SN')
        rel = os.path.relpath(fp, folder)
        if issues:
            all_clean = False
            print(f'⚠️  {rel}:')
            for iss in issues: print(f'   → {iss}')
        else:
            print(f'✅ {rel}')

print(f"\n{'✅ ALL CLEAN' if all_clean else '❌ ISSUES REMAIN'}")
```

---

## 5. Script: `verify_content.py`

Compares local HTML blocks against live page refs. Run: `python -X utf8 verify_content.py FolderName`

```python
from bs4 import BeautifulSoup
import os, re, json, sys, urllib.request

SPECIAL_PAGES = {'Aqydatona/8ZQ/24ZQ.html'}

def fetch_live(path):
    url = f"http://kingoflinks.net/{path}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read()
    return html.decode('windows-1256', errors='replace')

def get_live_text(local_path, url_map, cache_dir):
    """Try cache first, then fetch live."""
    htm_path = url_map.get(local_path)
    if not htm_path:
        htm_path = local_path.replace('.html', '.htm')
    cache_file = os.path.join(cache_dir, htm_path)
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return f.read().decode('windows-1256', errors='replace')
    return fetch_live(htm_path)

folder = sys.argv[1] if len(sys.argv) > 1 else '.'
url_map = {}
if os.path.exists('_url_map.json'):
    with open('_url_map.json', 'r', encoding='utf-8') as f:
        url_map = json.load(f)

results = []
for root, dirs, files in sorted(os.walk(folder)):
    for fn in sorted(files):
        if not fn.endswith('.html') or fn.startswith('Main'): continue
        fp = os.path.join(root, fn)
        rel = os.path.relpath(fp, '.').replace('\\', '/')
        result = {'file': rel, 'status': 'pending', 'issues': []}

        # SPECIAL_PAGES: use hadith-count for expected block count, skip live ref comparison
        if rel in SPECIAL_PAGES:
            with open(fp, encoding='utf-8', errors='replace') as f:
                soup = BeautifulSoup(f, 'html.parser')
            hc = soup.find('span', class_='hadith-count')
            blocks = soup.find_all('div', class_='hadith-block')
            if hc:
                m = re.search(r'(\d+)', hc.get_text())
                expected = int(m.group(1)) if m else 0
                if len(blocks) != expected:
                    result['issues'].append(f'BLOCK_COUNT: expected {expected}, got {len(blocks)}')
            for i, blk in enumerate(blocks):
                ht = blk.find('div', class_='hadith-text')
                if not ht or not ht.get_text(strip=True):
                    result['issues'].append(f'b{i+1} EMPTY_HADITH_TEXT')
            result['status'] = 'OK' if not result['issues'] else 'ISSUES'
            results.append(result)
            continue

        try:
            with open(fp, encoding='utf-8', errors='replace') as f:
                soup = BeautifulSoup(f, 'html.parser')
            blocks = soup.find_all('div', class_='hadith-block')
            live_text = get_live_text(rel, url_map, '_live_cache')

            # Extract live ref pairs (juz, page)
            live_refs = re.findall(r'\(\s*(\d+)\s*\)[^\(]{1,60}\(\s*(\d+)\s*\)', live_text)

            # Extract local ref pairs
            local_refs = []
            for blk in blocks:
                ref = blk.find('div', class_='ref-info')
                if ref:
                    vals = [v.get_text(strip=True) for v in ref.find_all('span', class_='ref-value')]
                    if len(vals) >= 2:
                        local_refs.append((vals[0], vals[1]))
                    elif len(vals) == 1:
                        local_refs.append(('', vals[0]))

            # Compare block counts
            if len(blocks) < len(live_refs):
                result['issues'].append(f'MISSING_BLOCKS: local={len(blocks)}, live_refs={len(live_refs)}')
            elif len(blocks) > len(live_refs) + 2:
                result['issues'].append(f'EXTRA_BLOCKS: local={len(blocks)}, live_refs={len(live_refs)}')

            # Compare ref values
            for i, (lj, lp) in enumerate(live_refs):
                if i < len(local_refs):
                    lcj, lcp = local_refs[i]
                    if lcp and lp != lcp.split('/')[0].strip():
                        result['issues'].append(f'b{i+1} REF_MISMATCH: live=({lj},{lp}) local=({lcj},{lcp})')

            result['status'] = 'OK' if not result['issues'] else 'ISSUES'
        except Exception as e:
            result['status'] = 'ERROR'
            result['issues'].append(str(e))

        results.append(result)

ok = sum(1 for r in results if r['status'] == 'OK')
issues = sum(1 for r in results if r['status'] == 'ISSUES')
errors = sum(1 for r in results if r['status'] == 'ERROR')

print(f"\n{'='*60}")
print(f"Results: {ok} OK, {issues} ISSUES, {errors} ERRORS (total {len(results)})")
for r in results:
    if r['status'] != 'OK':
        print(f"\n⚠️  {r['file']} [{r['status']}]")
        for iss in r['issues']:
            print(f'   → {iss}')
if not issues and not errors:
    print('✅ ALL CLEAN')
```

---

## 6. Script Lifecycle Rule

> **Delete ALL `.py` files when done with a session.**
> Recreate them from this document at the start of the next session.
> The only permanent files are `.html`, `.css`, `.md`, and data files.

---

## 7. Non-Negotiable Rules

1. DO NOT MISS ANY CONTENT.
2. DO NOT SKIP ANY CONTENT.
3. DO NOT REMOVE ANY CONTENT unless explicitly instructed.
4. DO NOT INVENT, GUESS, OR FILL GAPS WITH ASSUMPTIONS.
5. DO NOT REWRITE, SUMMARIZE, SIMPLIFY, MERGE, CLEAN, OR COMPRESS CONTENT.
6. DO NOT CHANGE THE MEANING, ORDER, HIERARCHY, OR FIELD OWNERSHIP.
7. DO NOT PROCEED WITH PARTIAL, APPROXIMATE, OR "GOOD ENOUGH" RESULTS.
8. DO NOT CONTINUE TO THE NEXT TASK UNTIL THE CURRENT ONE IS FULLY PERFECT.
9. IF UNSURE, STOP AND ASK THE USER.
10. IF THE ALTERNATIVE IS A WEAK SETUP, PLACEHOLDER, OR GARBAGE — STOP AND ASK.
11. CONTENT ACCURACY AND COMPLETENESS ARE THE HIGHEST PRIORITY.
12. `hadith-text` must always be present when content is present.
13. Never remove a `<p>` unless 100% certain it is structural noise.
14. If a fix depends on unclear live data, FETCH THE LIVE PAGE FIRST.
15. Do not continue past a blocker.
16. Do not apply guessed mappings.
17. Do not use data from the wrong page, wrong file, or wrong block.
18. Perfection on the current task is mandatory before moving forward.
19. **ALL content must come from live pages** — live page is the source of truth.
20. **Work one page at a time** — no batch assumptions.
21. **If a live page has a structure you haven't seen, ASK the user.**
22. **Never use WebFetch / web_fetch for `kingoflinks.net`** — Python `urllib` only.

---

## 8. Workflow Per Folder

1. Fetch/verify live cache exists for each page in folder
2. Run `inspect_folder.py FolderName` — note all structural issues
3. For EACH page, one at a time:
   a. Fetch the live page (cache or live)
   b. Compare local vs live, block by block
   c. Fix all fields to match live exactly (see `Guide.md` for field rules)
   d. If the page has a structure you haven't seen → **STOP AND ASK**
4. Re-run `inspect_folder.py` — confirm zero issues
5. Run `verify_content.py FolderName` — confirm block counts and refs match
6. Commit: `git add FolderName/ && git commit -m "Verify+Fix FolderName: description (N files)"`
7. Delete all `.py` scripts when done with the session

---

## 9. Task Lock Rule

Work on only the current flag / task / page / file / folder.

Do not continue to the next one until the current one is:
- fully completed
- fully correct
- fully verified

No partial completion, no temporary placeholders, no "fix later", no unresolved carry-over.

---

## 10. Current Progress

| Status | Folders |
|--------|---------|
| ✅ Done | Abawalnabi, Abdulmtalib, Abutalib, AhlAlBait (+7 subs), Aqydatona (+9 subs) |
| ❌ Remaining | Bahth, Bhooth, Daeefa, Fatima, Hywan, ImamAli, ImamHasan, ImamHussain, ImamMahdi, Mkhalfoon, NabiMohd, RAG, RS, Rdod, Seerah, SwR, Threef, Tjseem |

See `process.md` for full detail with subfolder checklists.

---

## 11. Commit Convention

```
Verify+Fix FolderName: description (N files, issues fixed)
```

Examples:
- `Verify+Fix Aqydatona: COMBINED_BT, BOOK_AS_SN, HADITH_IN_CI across 9 files`
- `Verify+Fix AhlAlBait: content matched against live pages (202 files)`

---

## 12. Response Format After Each Task

```text
CURRENT TASK: [exact file / block / folder]
LIVE URL: [exact URL fetched]
LOCAL TARGET: [exact file path]

FIELD MAPPING:
- Scholar name: [value]
- Book title: [value]
- Chapter info: [value]
- Ref info: [ج N / ص N]
- Hadith number: [value or "not present"]
- Hadith Text: [present / restored / corrected]

BLOCKERS: [exact blockers or "none"]
```

---

## 13. Problem Escalation

When hitting a blocker, STOP and report ALL of:

1. CURRENT TASK
2. Exact LIVE URL
3. Exact page/link where issue exists
4. Exact LOCAL TARGET file
5. Exact HTML / parsing / structure problem
6. Which field(s) are affected
7. Why this blocks accurate implementation
8. What you need from the user

**DO NOT CONTINUE PAST A BLOCKER. DO NOT GUESS.**

---

## 14. Done Rule

A task is only done when:
- It fully matches live content
- Checked for omissions and structural accuracy
- Scholar name, Book title, Chapter info, Ref info, Hadith Text all correct
- Hadith number correct when present
- No known unresolved issues
- Folder audit is clean (inspect_folder.py + verify_content.py)
- Changes committed

---

## 15. Failsafe

If there is ANY risk of:
- missed content, wrong field mapping, merged metadata
- lost hadith text, lost hadith number
- weak parser assumptions, data from wrong page
- incomplete matching, incorrect structure

**STOP and ask the user.**

Priority: Perfection > Progress. No skipped content. No guessed mapping. No data loss.

---

## 16. Data Files (Brief)

| File/Folder | Purpose |
|-------------|---------|
| `_live_cache/` | Raw windows-1256 `.htm` files mirroring live site |
| `_url_map.json` | Maps local `.html` → live `.htm` paths |
| `process.md` | Authoritative folder completion tracker |
| `Audit.md` | Issue codes, special pages, per-folder known issues |
| `Guide.md` | Page structures, field rules, fix patterns, CSS reference |
| `migration_audit.md` | Historical migration audit data |
