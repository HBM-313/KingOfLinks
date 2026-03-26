---
trigger: always_on
---

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