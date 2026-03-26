---
trigger: always_on
---

You are working inside the current local KingOfLinks project workspace.

PRIMARY MUST- DO NOT VIOLATE
Your highest-priority mission is to systematically walk through the ENTIRE project using the live URLs from sitemap.xml as the source of truth for content.

You must:
- read sitemap.xml
- fetch each live .htm URL from it
- compare that live page against the matching local file
- make the local file match the live content exactly in content and completeness
- preserve the LOCAL implemented structure
- preserve the LOCAL folder structure
- work page by page, one by one
- skip nothing
- miss nothing
- silently ignore nothing

LIVE CONTENT = source of truth for content
LOCAL PROJECT = source of truth for structure

Do not rush.
Do not batch loosely.
Do not “roughly match”.
Do not move on until the current page is fully verified.

==================================================
PROJECT UNDERSTANDING
==================================================

This is a hadith-content preservation and normalization project.

The local project already has an intended HTML structure and folder structure.
Your job is NOT to redesign the project.
Your job is to preserve the local implementation structure while making the local content exactly match the live page.

This is a content-preservation project first.
Visual similarity is secondary.
Data accuracy and completeness are the highest priority.

==================================================
MANDATORY STARTUP BEHAVIOR
==================================================

Before changing anything:

1. Detect the CURRENT repo state first.
   - Do not assume an older handoff commit is still the current state.
   - Read git status, current branch, and latest commit.
   - Treat previous handoff commit references as historical guidance only.

2. Read and use:
   - sitemap.xml
   - the current local HTML files
   - any existing audit/helper scripts already present in the repo

3. Build a processing checklist from sitemap.xml.

4. Create or update:
   migration_audit.md

5. Process every sitemap page in strict order, one by one.

==================================================
SITEMAP RULE
==================================================

Use every live URL in sitemap.xml as the master checklist.

This includes:
- root-level pages
- nested folder pages
- subfolder pages
- MainXX.htm style nested pages
- all relevant .htm content pages listed in the sitemap

Do not skip any folder.
Do not skip any subfolder.
Do not skip any page because it looks repetitive.

If the sitemap contains pages in nested paths, preserve that folder structure locally.

==================================================
FETCH RULE — CRITICAL
==================================================

DO NOT use WebFetch / browser fetch tooling for kingoflinks.net.

For kingoflinks.net, always use Python urllib.

Use this exact live-fetch approach:

```python
import urllib.request
import re

def fetch_live(path):
    """
    path example: 'AhlAlBait/6Thqlain/22Ajori.htm'
    """
    url = f"http://kingoflinks.net/{path}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read()
    text = html.decode('windows-1256', errors='replace')
    return url, text

def extract_page_numbers(text):
    return re.findall(r'\(\s*(\d+)\s*\)', text)

def extract_blocks(text):
    return [b.strip() for b in text.split('---') if b.strip()]

IMPORTANT:

live site uses .htm
repo uses .html
Arabic can be garbled after decode
numeric values remain reliable and are valid for alignment:
volume number
page number
hadith number

If Arabic content is too garbled to safely reconstruct text, do NOT invent.
Flag the page and request user inspection/input for that page only.

==================================================
PAGE-TO-LOCAL MATCHING RULE

For each sitemap URL:

Determine the exact corresponding local file.
Open the local file.
Fetch the exact live page.
Compare live block order against local hadith-block order.
Match blocks using:
block position
scholar
book
volume
page
hadith number when present

Before applying any live data to any local block, verify that:

scholar matches
book matches
volume matches
hadith number matches when present

If any of those mismatch:

STOP for that block
FLAG it
DO NOT APPLY guessed values

NEVER apply data from one live page to a different local file.
NEVER inject page/volume data into blocks from the wrong source page.

==================================================
TASK LOCK RULE

Work only on the current:

page
file
block
issue set

Do not move to the next page until the current one is:

fully completed
fully correct
fully verified
fully logged

No placeholders.
No “fix later”.
No unresolved carry-over.
No approximate completion.

==================================================
CORRECT TARGET STRUCTURE

Use this structure whenever the page is a hadith-style content page:

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

Preserve the local folder structure and local page template structure.
If the live content does not fit perfectly, adapt it into the closest valid local structure WITHOUT losing anything.

==================================================
STRICT FIELD OWNERSHIP RULES

Scholar name:

must be the scholar/author personal name only
never a topic
never a book title
never a verse
never a number
never editorial note text

Book title:

must be the book title only
never scholar name
never narrator chain
never hadith text
never chapter path

Chapter info:

must contain only chapter / section / باب / كتاب / فصل path/context
must not absorb hadith text
must not absorb page/ref values

Ref info:

citation/reference data only
must contain both:
الجزء
الصفحة
unless the live page truly uses a hadith-numbered convention instead of page
if live uses hadith number instead of page, verify carefully before mapping

Hadith number:

optional
only extract if clearly present as a distinct identifier
keep separate from hadith text
do not invent one

Hadith text:

must contain actual hadith/narration content only
must always be present when content exists
must not absorb metadata fields
preserve full wording and order exactly

Analysis note:

optional
max one per block
must be inside the same hadith-block
must come after hadith-text
==================================================
KNOWN HIGH-RISK ERROR PATTERNS

Detect and fix these patterns carefully:

BOOK_AS_SN
scholar-name contains a book/collection title instead of a scholar
SN_EQ_BT
scholar-name equals book-title
COMBINED_BT
book-title combines scholar + book or book + chapter
HADITH_IN_CI
hadith text incorrectly placed inside chapter-info
EDITORIAL_IN_SN
editorial note text placed in scholar-name
FLOATING_NOTE
analysis-note outside hadith-block
LOOSE_P
loose paragraphs floating directly in article-body
FOOTNOTES_SECTION
footnotes section not converted into proper hadith-block structure
MISSING scholar-name div entirely
scholar stored only in book-title
truncated book-title fragments
partial values like:
ا
تا
كتا
شر
ك
scholar-name contains topic text, Quran verse, or surah header
book-title contains narrator chain text
editorial note not wrapped safely inside hadith text
page/volume data accidentally copied from the wrong live file
==================================================
APPROVED FIX LOGIC

Apply these fix rules when verified:

If scholar-name contains topic text and book-title contains the scholar:
move scholar to scholar-name and set correct book from live/context.
If scholar-name is a number:
move that number to hadith-number when verified.
If scholar-name is a single broken letter and book-title holds the scholar:
restore scholar/book ownership correctly.
If book-title contains scholar + book:
split them.
If book-title contains narrator chain:
move narrator chain to hadith-text and restore book title.
If chapter-info contains hadith text:
move hadith text into hadith-text and keep chapter-info as chapter context only.
If editorial note is in scholar-name:
move note into hadith-text and restore scholar correctly.
If analysis-note floats outside a block:
move it into the correct preceding block, or first block if it belongs before all.
If a block is missing scholar-name entirely:
insert it before book-info and repair book-title from context/live verification.
==================================================
CONTEXTUAL MAPPING RULES

Use these only when verified by file context or live page:

الطبراني volume rule:
ج1–2 => المعجم الصغير
ج3–10 => المعجم الأوسط
ج11+ => المعجم الكبير
If book title is:
ذخائر العقبى في مناقب ذوي القربى
then scholar must be:
المحب الطبري
not الطبري
Multi-book scholars must be resolved using:
same-file context
neighboring blocks
verified live data
volume logic where confirmed

If not safely verifiable:

do not guess
flag for manual review
==================================================
NO DATA LOSS RULE

Never:

drop content
compress content
summarize content
paraphrase content
rewrite content for style
silently leave fields empty because parsing failed
mark a page done if field ownership is unclear

Never remove a <p> unless you are certain it is structural noise and not real content.

If hadith text exists on live page, hadith-text must exist locally after the fix.

==================================================
PAGE COMPLETION RULE

A page is NOT complete unless all relevant page content is correctly mapped and verified for:

Scholar name
Book title
Chapter info
Ref info
Hadith Text
Hadith number when present
analysis note when present

Even if the page looks visually acceptable, it is NOT complete if:

any field is wrong
any field is incomplete
any field is merged wrongly
hadith-text is missing
ref info is incomplete
content was skipped
==================================================
WORKFLOW

PHASE 1 — INVENTORY

Parse sitemap.xml
Build full checklist of live URLs
Map each live URL to a local file path
Record all mappings in migration_audit.md

PHASE 2 — PAGE-BY-PAGE EXECUTION
For each page:

set status = IN PROGRESS
fetch live page
inspect local file
compare block-by-block
fix local file
verify every block
save only after verification
set status = DONE or BLOCKED

PHASE 3 — RE-VERIFY
After each page edit:

verify no content was lost
verify no field drift happened
verify no wrong-page data was injected
verify local HTML remains valid
verify local folder structure unchanged

PHASE 4 — FINAL SWEEP
After all sitemap pages are processed:

re-run audit across entire project
produce final summary:
completed pages
blocked pages
ambiguous pages
missing local counterparts
manual-review pages
unresolved fetch/content issues
==================================================
AUDIT FILE FORMAT

Maintain migration_audit.md continuously.

For every page record:

live URL
local file path
status: pending / in progress / done / blocked
exact blocks affected
issues found
changes made
verification result
blocker details if any
==================================================
BLOCKER RULE

If any issue prevents accurate mapping, STOP for that page and report:

CURRENT TASK
exact LIVE URL
exact local file path
exact block number(s)
exact field(s) affected
exact reason this cannot be safely completed
what user inspe