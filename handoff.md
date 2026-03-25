# KingOfLinks — STRICT HADITH CONTENT MATCH + CLEANUP + DATA MIGRATION HANDOFF FOR CLAUDE CODE

Paste this entire prompt into Claude Code (terminal) to continue the cleanup.

---

## SETUP

GitHub repo: https://github.com/HBM-313/KingOfLinks.git  
GitHub token: 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

```bash
cd /home/claude
git clone https://[REDACTED_GITHUB_TOKEN]@github.com/HBM-313/KingOfLinks.git
cd KingOfLinks
git config user.email "cleanup@kingoflinks.net"
git config user.name "KingOfLinks Cleanup"
```

Last commit: `742d342`

Live site: `http://kingoflinks.net/`
- Repo uses `.html`
- Live site uses `.htm`

Live site encoding:
- Windows-1256
- No charset headers
- Arabic text may appear garbled
- Numbers always survive and are reliable for matching:
  - page number
  - hadith number
  - volume number

---

## PRIMARY OBJECTIVE

Match the LIVE URL content to the LOCAL PROJECT with maximum fidelity, completeness, and structural accuracy, and normalize all `hadith-block` elements into the correct structure without losing, rewriting, misclassifying, weakening, or silently dropping any data.

This is a CONTENT-PRESERVATION project first.  
Visual matching is secondary.  
Data accuracy and completeness are the highest priority.

---

## FETCHING LIVE PAGES — CRITICAL

DO NOT use the WebFetch tool for `kingoflinks.net`.

Claude Code WebFetch fails for constructed URLs and is not reliable for this site workflow.

ALWAYS use Python `urllib` via the Bash tool instead.

### Standard fetch function — paste this at the start of every session:

```python
import urllib.request
import re

def fetch_live(path):
    """
    Fetch a live page from kingoflinks.net via Python (NOT WebFetch).
    path = folder/filename WITHOUT leading slash.
    Repo files use .html — live site uses .htm  (e.g. 'Abutalib/9.htm')
    Arabic text will be garbled (Windows-1256 encoding issue).
    Numbers ALWAYS survive and are readable — use them for matching.
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

### Usage:

```python
# Fetch a page
url, content = fetch_live("Abutalib/9.htm")
print(content[:3000])

# Extract all numbers from the page
numbers = extract_page_numbers(content)
print(numbers[:30])

# Split into blocks
blocks = extract_blocks(content)
for i, b in enumerate(blocks):
    print(f"\n--- Block {i+1} ---\n{b[:200]}")
```

### Matching live blocks to local blocks:

Live page blocks appear in the same order as local `hadith-block` elements.

Match by:
- block position
- volume number
- page number
- hadith number, when present

```python
refs = re.findall(r'\(\s*(\d+)\s*\)[^\(]{1,60}\(\s*(\d+)\s*\)', content)
# refs = [(juz, page), (juz, page), ...]
```

### NEVER do this:

Do not use WebFetch / web_fetch on `kingoflinks.net`.

### Mandatory verification before applying live data:

Before writing any number or field to a local block, confirm the local block's:
- scholar
- book
- volume

matches what the live page shows for THAT block.

If anything mismatches:
- FLAG IT
- DO NOT APPLY

NEVER apply data from one file's live page to a different file's blocks.

---

## NON-NEGOTIABLE RULES

1. DO NOT MISS ANY CONTENT.
2. DO NOT SKIP ANY CONTENT.
3. DO NOT REMOVE ANY CONTENT unless explicitly instructed.
4. DO NOT INVENT, GUESS, OR FILL GAPS WITH ASSUMPTIONS.
5. DO NOT REWRITE, SUMMARIZE, SIMPLIFY, MERGE, CLEAN, OR COMPRESS CONTENT unless explicitly instructed.
6. DO NOT CHANGE THE MEANING, ORDER, HIERARCHY, OR FIELD OWNERSHIP.
7. DO NOT PROCEED WITH PARTIAL, APPROXIMATE, OR “GOOD ENOUGH” RESULTS.
8. DO NOT CONTINUE TO THE NEXT TASK, FLAG, STEP, PAGE, SECTION, RECORD, OR FOLDER UNTIL THE CURRENT ONE IS FULLY PERFECT.
9. IF UNSURE, STOP AND ASK THE USER INSTEAD OF GUESSING.
10. IF THE ALTERNATIVE IS A WEAK SETUP, PLACEHOLDER, OR GARBAGE SETUP, STOP AND ASK FOR HELP.
11. CONTENT ACCURACY AND COMPLETENESS ARE THE HIGHEST PRIORITY.
12. hadith-text must always be present when content is present.
13. Never remove a `<p>` unless you are 100% certain it is a structural artifact and not actual hadith content.
14. If a fix depends on unknown or unclear live data, FETCH THE LIVE PAGE FIRST.
15. Do not continue past a blocker.
16. Do not apply guessed mappings.
17. Do not use data from the wrong page, wrong file, or wrong block.
18. Perfection on the current task is mandatory before moving forward.

---

## TASK LOCK RULE

Work on only the current:
- flag
- task
- page
- section
- record group
- file
- folder

Do not continue to the next one until the current one is:
- fully completed
- fully correct
- fully verified

No:
- partial completion
- temporary placeholders
- “fix later”
- unresolved carry-over

---

## CORE CONTENT PRIORITY — HIGHEST IMPORTANCE

The following fields are the essence of the project and must be preserved, matched, extracted, mapped, and verified with extreme care on every relevant page:

- Scholar name
- Book title
- Chapter info
- Book info
- Ref info
- Hadith Text

Conditional field:
- Hadith number

These are not optional details, except that Hadith number is only extracted when it is actually present as a distinct identifier in the source.

If any of the following is missing, misplaced, merged wrongly, misclassified, altered, or unclear, then the task is NOT complete:
- Scholar name
- Book title
- Chapter info
- Book info
- Ref info
- Hadith Text

If Hadith number is present in the source but is not extracted correctly, or remains wrongly merged into Hadith Text, the task is also NOT complete.

---

## CORRECT hadith-block STRUCTURE

```html
<div class="hadith-block">
  <div class="scholar-name">اسم العالم</div>
  <div class="book-info">
    <span class="book-title">اسم الكتاب</span>
    <span class="chapter-info">باب / كتاب / فصل</span>   <!-- optional -->
  </div>
  <div class="ref-info">
    <span><span class="ref-label">الجزء: </span><span class="ref-value">N</span></span>
    <span><span class="ref-label">الصفحة: </span><span class="ref-value">N</span></span>
  </div>
  <div class="hadith-text">
    <span class="hadith-number">N</span>   <!-- optional -->
    <p>نص الحديث</p>
  </div>
  <div class="analysis-note">   <!-- optional, ONE per block, INSIDE hadith-block -->
    <p>التحليل الموضوعي :</p>
    <p>- نقطة</p>
  </div>
</div>
```

---

## FIELD RULES — STRICT

### Scholar name
- Must contain the scholar / author personal name only
- Never:
  - a number
  - a topic
  - a verse
  - a book title
  - editorial note
  - `م`
  - `مم`
  - `ممم`
- Must not absorb:
  - book title
  - chapter info
  - book info
  - ref info
  - hadith number
  - hadith text

### Book title
- Must contain the book title only
- Must not absorb:
  - scholar name
  - chapter info
  - book info
  - ref info
  - hadith number
  - hadith text
- Never:
  - narrator chain
  - combined scholar+book
  - hadith text
  - generic placeholder title

### Chapter info
- Must contain chapter / section / bab path only
- Must not absorb:
  - hadith text
  - book title
  - ref info
  - hadith number
- Never place `- NUMBER - text...` inside chapter-info
- If the live page separates chapter context, preserve it exactly

### Book info
- Must contain book-level structural information only
- May include volume or book-level context when clearly part of book info
- Must stay distinct from chapter info if the live page separates them
- Must not absorb:
  - scholar name
  - hadith text
  - ref info
  - hadith number

### Ref info
- Must contain citation / reference information only
- Must have BOTH:
  - `الجزء:`
  - `الصفحة:`
- May include:
  - source references
  - page numbers
  - volume/page notation
  - reference labels
  - source lines
- Must not absorb hadith text
- Must not absorb scholar name
- Must not absorb book title or chapter info unless the live page explicitly structures it that way and it is verified carefully

### Hadith number
- Optional
- Must only be extracted when it is actually present as a distinct hadith identifier
- Must contain the hadith number / identifier only
- Must be kept separate from Hadith Text
- Must not absorb ref info or other metadata unless the live page explicitly uses one combined identifier structure and that is verified
- Do not invent a hadith number when none is provided
- Do not force a number into this field if uncertain

### Hadith Text
- Must contain the actual hadith content only
- Must exist if content is present
- Must not absorb:
  - metadata labels
  - scholar name
  - book title
  - chapter info
  - book info
  - ref info
  - hadith number when it is clearly separate
- Preserve full wording and order exactly as shown on the live page
- Do not shorten it
- Do not normalize away meaningful characters
- Do not remove line breaks unless explicitly instructed and only if safe

### Analysis note
- Optional
- ONE per block only
- Must be INSIDE the `hadith-block`
- Must be AFTER `hadith-text`
- Floating analysis-notes must be moved into the correct preceding block
- If a note appears before all blocks, move it into the first block

---

## IMPORTANT HADITH NUMBER RULE

Hadith number is not always present.

But when it is present, it is typically included at the beginning of the hadith text block before the sentence starts.

In that case:
- extract it into a separate `Hadith number` field
- remove it from `Hadith Text`

Example:

If source shows:
`1234 Imam X said ...`

and `1234` is clearly the hadith identifier, then map:
- `hadith_number: 1234`
- `hadith_text: Imam X said ...`

If no such identifier exists:
- `hadith_number: null / empty`
- `hadith_text: [full hadith text as shown]`

If uncertain whether the leading number is a hadith identifier or part of the wording:
- STOP
- ASK THE USER

---

## PAGE COMPLETION RULE

A page is NOT complete unless all relevant content on that page has been extracted and the following are correct:
- Scholar name
- Book title
- Chapter info
- Book info
- Ref info
- Hadith Text
- Hadith number, when present

Even if the page looks visually correct, it is still NOT complete if any of these fields are:
- wrong
- incomplete
- merged incorrectly
- shifted into the wrong field
- missing

---

## NO DATA LOSS RULE

During extraction, transformation, restructuring, migration, parsing, cleanup, or mapping:
- No content may disappear
- No content may be silently dropped
- No field may be left empty because parsing failed without reporting it
- No page may be treated as complete if extraction confidence is low
- No record may be marked done if there is uncertainty in field ownership

---

## NO FALSE CLEANUP RULE

You are forbidden from:
- auto-correcting names without evidence
- standardizing references without approval
- fixing spelling automatically unless listed in the approved typo list below
- rewriting awkward text
- removing repeated labels unless explicitly instructed
- removing “ugly” markup artifacts unless verified safe
- converting ambiguous text into assumed categories
- flattening structured content into one blob because it is easier

---

## EXTRACTION SAFETY RULE

The source site may contain:
- inconsistent HTML
- mixed text nodes
- repeated layouts
- different templates
- weak markup
- page-specific variations

Because of this:
- inspect each page individually
- do not assume one parser or selector works safely for all pages
- verify extraction against the visible live page
- use page-specific handling when needed
- prefer correctness over automation convenience
- do not assume repeated pages are identical without checking

If pages differ in HTML structure:
- detect the variation
- report the variation
- explain exactly which pages / templates differ
- explain whether the variation affects accurate extraction
- ask the user before forcing a weak universal parser

If unsure whether text belongs to:
- Scholar name
- Book title
- Chapter info
- Book info
- Ref info
- Hadith number
- Hadith Text

then STOP and ask the user.

Never guess field ownership.

---

## PROJECT GOAL

Normalize all `hadith-block` elements across all HTML files to a consistent, correct structure.

One folder at a time:
1. Inspect
2. Fix
3. Verify clean
4. Commit
5. Push

---

## WORKFLOW PER FOLDER

1. List all `.html` files in folder
2. Run inspection script across the folder
3. Note all issues
4. Ask user if anything is unclear
5. For any block needing live data:
   - ALWAYS fetch the live page first using `fetch_live()`
6. Apply fixes
7. Re-run inspection
8. Confirm zero remaining issues
9. `git add` + commit + push

---

## CURRENT ISSUE COUNTS (as of commit 742d342)

| Issue | Count | Notes |
|---|---:|---|
| `missing_page` | 0 | ✅ |
| `empty_sn` | 0 | ✅ |
| `scholar_eq_book` | 5 | See list below |
| `floating_notes` | 10 | In 2 files |
| `footnotes_section` | 33 files | Need conversion to hadith-blocks |
| `combined_bt` | 634 | `Scholar -Book` or `Book -Chapter` in bt span |
| `unwrapped_editorial` | 3,427 | `النص طويل` not wrapped in `<span class="editorial-note">` |
| `hadith_in_ci` | 1,616 | Hadith text sitting inside chapter-info span |

---

## KNOWN SPECIFIC ISSUES TO FIX NEXT

### scholar_eq_book (5 instances)

| File | Block | sn=bt | Fix |
|---|---|---|---|
| `Abutalib/9.html` | b1 | `القرآن الكريم` | Structural wreck — fetch live page first |
| `ImamAli/18Syed/10ZKH.html` | b1 | `الزرندي الحنفي` | Book title is in first `<p>` of hadith-text: `نظم درر السمطين...` — set bt to that, remove that `<p>` |
| `ImamAli/18Syed/7IbnAsaker.html` | b1 | `ابن عساكر` | ci already has `تاريخ دمشق` — set bt = `تاريخ دمشق` |
| `ImamAli/18Syed/8IbnQane.html` | b1 | `ابن قانع` | First `<p>` = `- معجم` (truncated) — set bt = `معجم الصحابة`, remove that `<p>` |
| `SwR/11Dbor.html` | b9 | `النووي` | ci has `المجموع شرح المهذب` — set bt = `المجموع شرح المهذب` |

### Floating analysis-notes (10 instances in 2 files)

| File | Count | Action |
|---|---:|---|
| `Abutalib/9.html` | 1 | Move inside preceding hadith-block, or first block if before all |
| `AhlAlBait/6Thqlain/5Albani.html` | 9 | Move each inside its preceding hadith-block |

---

## INSPECTION SCRIPT TEMPLATE

```python
from bs4 import BeautifulSoup, Tag
import os, re

EDITORIAL = 'النص طويل لذا استقطع منه موضع الشاهد'
CI_HADITH = re.compile(r'^-\s*\d+\s*-\s*.{10,}')
NUMBER_ONLY = re.compile(r'^\s*[\d\u0660-\u0669]+\s*$')
GARBLED = re.compile(r'^م{1,3}$')
BOOK_NAMES = {'صحيح البخاري','صحيح مسلم','السنن الكبرى','المعجم الكبير','المعجم الأوسط',
              'المعجم الصغير','المستدرك على الصحيحين','مسند الامام أحمد بن حنبل',
              'صحيح ابن حبان','سير أعلام النبلاء','البداية والنهاية','تاريخ دمشق','كتاب السنة'}

folder = 'FOLDER_NAME'
for fn in sorted(os.listdir(folder)):
    if not fn.endswith('.html'): continue
    with open(f'{folder}/{fn}', encoding='utf-8', errors='replace') as f:
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
    print(f"{'✅' if not issues else '⚠️ '} {fn}" + ('' if not issues else ':'))
    for iss in issues: print(f'   → {iss}')
```

---

## FIX PATTERNS REFERENCE

### Combined bt: `Scholar -Book` or `Book -Chapter`
Split on first ` -`

- Left → `scholar-name`, or new `book-title` if bt contains `Book -Chapter`
- Right → `book-title`, or new `chapter-info`

Split keywords for chapter detection:
- `كتاب`
- `باب`
- `فصل`
- `ذكر`
- `شرح`
- `حرف`
- `تتمة`
- `جماع`
- `تفسير سورة`
- `الباب`
- `سورة`
- `موضوع`

### Unwrapped editorial note

```html
<!-- WRONG -->
<p>النص طويل لذا استقطع منه موضع الشاهد</p>

<!-- CORRECT -->
<p><span class="editorial-note">النص طويل لذا استقطع منه موضع الشاهد</span></p>
```

### Editorial in scholar-name
Real scholar is in `book-title`.
Move editorial to `hadith-text`.
Set `scholar-name` from `book-title`.

### Hadith in chapter-info
Look for `chapter-info` matching:
`^-\s*\d+\s*-\s*.{10,}`

Extract hadith number + text and create a proper `hadith-text` div.

MUST verify against live page before applying.

### Floating analysis-note
Move inside preceding `hadith-block`, after `hadith-text`.
If note comes before all blocks, move into first block.

### footnotes-section
Convert to proper `hadith-block`.
MUST fetch live page to get scholar / book / ref / hadith data.

### الطبراني volume rule
- ج1–2 → `المعجم الصغير`
- ج3–10 → `المعجم الأوسط`
- ج11+ → `المعجم الكبير`

### المحب الطبري rule
If `book-title` = `ذخائر العقبى في مناقب ذوي القربى`
then `scholar-name` MUST be `المحب الطبري`

### Approved typos to fix on encounter
- `تقسير` → `تفسير`
- `ابن قدامه` → `ابن قدامة`
- `ابن ابي شيبة` → `ابن أبي شيبة`
- Scholar `الرازي` + book `تقسير ابن أبي حاتم` → scholar = `ابن أبي حاتم`, book = `تفسير القرآن العظيم`

---

## HELPER FUNCTIONS

```python
from bs4 import BeautifulSoup

def add_page(soup, block, page_val):
    ref = block.find('div', class_='ref-info')
    if not ref: return False
    labels = [s.get_text(strip=True) for s in ref.find_all('span', class_='ref-label')]
    if any('الصفحة' in l for l in labels): return False
    sp = soup.new_tag('span')
    lbl = soup.new_tag('span', attrs={'class': 'ref-label'}); lbl.string = 'الصفحة: '
    val = soup.new_tag('span', attrs={'class': 'ref-value'}); val.string = str(page_val)
    sp.append(lbl); sp.append(val); ref.append(sp)
    return True

def fix_vol(block, new_juz):
    ref = block.find('div', class_='ref-info')
    if not ref: return False
    for sp in ref.find_all('span'):
        lbl = sp.find('span', class_='ref-label')
        val = sp.find('span', class_='ref-value')
        if lbl and val and 'الجزء' in lbl.get_text():
            val.string = str(new_juz); return True
    return False

def wrap_editorial(soup, p_tag):
    span = soup.new_tag('span', attrs={'class': 'editorial-note'})
    text = p_tag.get_text(strip=True)
    text = text.strip('[]').strip()
    p_tag.clear()
    span.string = text
    p_tag.append(span)
```

---

## END-OF-FOLDER CHECKLIST

Run this after every folder before committing:

```python
from bs4 import BeautifulSoup, Tag
import os, re

EDITORIAL = 'النص طويل لذا استقطع منه موضع الشاهد'
CI_HADITH = re.compile(r'^-\s*\d+\s*-\s*.{10,}')

folder = 'FOLDER_NAME'
all_clean = True
for fn in sorted(os.listdir(folder)):
    if not fn.endswith('.html'): continue
    with open(f'{folder}/{fn}', encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f, 'html.parser')
    issues = []
    ab = soup.find(class_='article-body')
    if ab:
        for child in ab.children:
            if isinstance(child, Tag):
                if 'analysis-note' in (child.get('class') or []): issues.append('FLOATING_NOTE')
                if child.name == 'p': issues.append('LOOSE_P')
    if soup.find('div', class_='footnotes-section'): issues.append('FOOTNOTES_SECTION')
    for i, blk in enumerate(soup.find_all('div', class_='hadith-block')):
        sn = blk.find('div', class_='scholar-name')
        bt = blk.find('span', class_='book-title')
        ref = blk.find('div', class_='ref-info')
        ht = blk.find('div', class_='hadith-text')
        sn_t = sn.get_text(strip=True) if sn else ''
        bt_t = bt.get_text(strip=True) if bt else ''
        if ref:
            labels = [s.get_text(strip=True) for s in ref.find_all('span', class_='ref-label')]
            if not any('الصفحة' in l for l in labels): issues.append(f'b{i+1} MISSING_PAGE')
        if not sn_t: issues.append(f'b{i+1} EMPTY_SN')
        if sn_t and sn_t == bt_t: issues.append(f'b{i+1} SN_EQ_BT')
        if bt_t and ' -' in bt_t: issues.append(f'b{i+1} COMBINED_BT')
        for ci in blk.find_all('span', class_='chapter-info'):
            if CI_HADITH.match(ci.get_text(strip=True)): issues.append(f'b{i+1} HADITH_IN_CI')
        if ht:
            for p in ht.find_all('p'):
                if EDITORIAL in p.get_text(strip=True) and not p.find('span', class_='editorial-note'):
                    issues.append(f'b{i+1} UNWRAPPED_EDITORIAL')
        if len(blk.find_all('div', class_='analysis-note')) > 1: issues.append(f'b{i+1} FRAG_ANALYSIS')
        if len(blk.find_all('div', class_='scholar-name')) > 1: issues.append(f'b{i+1} DUP_SN')
    if issues:
        all_clean = False
        print(f'⚠️  {fn}:')
        for iss in issues: print(f'   → {iss}')
    else:
        print(f'✅ {fn}')
print(f"\n{'✅ ALL CLEAN' if all_clean else '❌ ISSUES REMAIN'}")
```

---

## FOLDER PROCESSING ORDER

| # | Folder | ~Files | Status |
|---|---|---:|---|
| ✅ 1 | Abawalnabi | 13 | Done — commit 742d342 |
| ▶ 2 | Abdulmtalib | 11 | START HERE |
| 3 | Abutalib | 8 | has 1 floating note + scholar_eq_book b1 |
| 4 | AhlAlBait | 203 | has 9 floating notes in 5Albani.html |
| 5 | Hywan | ~91 | |
| 6 | Threef | ~150 | |
| 7 | Daeefa | ~233 | |
| 8 | NabiMohd | ~206 | |
| 9 | Seerah | ~506 | |
| 10 | Tjseem | ~229 | |
| 11 | Fatima | ~37 | |
| 12 | RAG | ~67 | |
| 13 | Aqydatona | ~1,145 | |
| 14 | SwR | ~462 | has scholar_eq_book b9 |
| 15 | ImamHasan | ~169 | |
| 16 | ImamHussain | ~436 | |
| 17 | ImamMahdi | ~344 | |
| 18 | Bhooth | ~661 | |
| 19 | RS | ~84 | |
| 20 | ImamAli | ~3,695 | has 3 scholar_eq_book in 18Syed/ |
| 21 | Mkhalfoon | ~3,227 | |

---

## MANDATORY URL + TRACEABILITY RULE

Always provide:
- exact live URL being used
- exact page / link being processed
- exact local file / component / script / sheet / output target
- exact block or source segment being extracted
- exact field mapping result

Always tell the user the exact page/link where there is a problem so the user can inspect it manually before guiding you.

Do not describe problems vaguely.

---

## PROBLEM ESCALATION RULE

Whenever you hit a blocker, mismatch, unclear structure, broken link, parser issue, or uncertain mapping, STOP and report ALL of the following before doing anything else:

1. CURRENT TASK
2. exact LIVE URL
3. exact page or link where the issue exists
4. exact LOCAL TARGET
5. exact HTML / parsing / mapping / structure problem
6. which field(s) are affected
7. why this blocks accurate implementation
8. what you need from the user to proceed correctly

DO NOT CONTINUE PAST A BLOCKER.
DO NOT GUESS.
DO NOT CREATE A WEAK WORKAROUND JUST TO KEEP MOVING.

---

## DONE RULE

A task is only done when:
- it fully matches the live content
- it has been checked for omissions
- it has been checked for structural accuracy
- it has been checked for page-specific correctness
- Scholar name is correct
- Book title is correct
- Chapter info is correct
- Ref info is complete with both `الجزء` and `الصفحة`
- Hadith Text is correct and present
- Hadith number is correct when present
- there are no known unresolved issues
- the folder audit is clean
- the changes are committed
- the changes are pushed

---

## RESPONSE FORMAT AFTER EACH TASK

```text
CURRENT TASK:
[exact file / block / folder]

LIVE URL:
[exact URL fetched]

LOCAL TARGET:
[exact file path]

MATCHED EXACTLY:
- [what was confirmed correct]

FIELD MAPPING:
- Scholar name: [value / status]
- Book title: [value / status]
- Chapter info: [value / status]
- Book info: [value / status]
- Ref info: [ج N / ص N or status]
- Hadith number: [value / status, or "not present on this page/record"]
- Hadith Text: [present / restored / unchanged / corrected]

STILL MISSING:
- [exact items]

BLOCKERS:
- [exact blockers]

DONE CHECK:
- [ ] Scholar name correct
- [ ] Book title correct
- [ ] Chapter info correct
- [ ] Book info correct
- [ ] Ref info complete (both الجزء and الصفحة)
- [ ] Hadith text present
- [ ] Hadith number correct when present
- [ ] No skipped content
- [ ] No guessed mapping
- [ ] Folder audit clean
- [ ] Committed
- [ ] Pushed
```

---

## FAILSAFE

If there is ANY risk of:
- missed content
- wrong field mapping
- merged metadata
- lost hadith text
- lost hadith number when present
- weak parser assumptions
- HTML-based extraction error
- incorrect structure
- incomplete matching
- data from the wrong live page applied to the wrong block

STOP and ask the user instead of continuing.

FINAL PRIORITY:
Perfection on the current task is mandatory.  
Progress is secondary.  
No skipped content.  
No guessed mapping.  
No data loss.  
The core fields — Scholar name, Book title, Chapter info, Book info, Ref info, and Hadith Text — are the essence of the project, and Hadith number must also be extracted correctly whenever it is present as a leading identifier.
