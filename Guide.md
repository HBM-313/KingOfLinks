# KingOfLinks — Complete Structural Guide

> **!!! CRITICAL !!!**
> ALL content MUST come from LIVE PAGES. Never assume. Always ask if confused.
> If a live page has a structure not matching Types 1-4 below — **STOP AND ASK** the user.

---

## 1. Project Architecture

```
KingOfLinks/
├── modern.css                  ← Global stylesheet
├── index-2.html                ← Site index
├── sitemap.xml                 ← All live URLs
├── process.md                  ← Folder progress tracker
├── Handoff.md                  ← Session startup prompt
├── Audit.md                    ← Issue codes, special pages, known issues
├── Guide.md                    ← THIS FILE — structural encyclopedia
├── migration_audit.md          ← Historical audit data
├── _live_cache/                ← Raw windows-1256 .htm cache
├── _url_map.json               ← local .html → live .htm mapping
│
├── Abawalnabi/                 ← 1-level folder (CSS: ../modern.css)
│   ├── 1.html ... 13.html
│   └── Main116.html
├── AhlAlBait/                  ← 2-level folder (CSS: ../../modern.css)
│   ├── 1Ttheer/
│   │   ├── 1BM.html ... 45Other.html
│   │   └── Main58.html
│   ├── 2Moadah/ ...
│   └── 11Mwalat.html (root-level pages)
├── Mkhalfoon/                  ← 2-level folder
│   ├── 1Abubaker/
│   │   └── *.html
│   └── ...43IbnOmar/
└── ... (23 top-level content folders total)
```

### CSS Path Depth

| Folder Depth | CSS `<link>` href | Example Folders |
|--------------|-------------------|-----------------|
| 1 level | `../modern.css` | Abawalnabi, Abdulmtalib, Abutalib, Bahth, Daeefa, Fatima, Hywan, NabiMohd, RAG, RS, Rdod, Seerah, SwR, Threef, Tjseem |
| 2 levels | `../../modern.css` | AhlAlBait/*, Aqydatona/*, ImamAli/*, ImamHasan/*, ImamHussain/*, ImamMahdi/*, Mkhalfoon/* |
| 3 levels | `../../../modern.css` | (rare — check if any sub-subfolder pages exist) |

### Encoding

- **Live site**: Windows-1256, no charset headers
- **Local files**: UTF-8 (`<meta charset="utf-8"/>`)
- **Live cache** (`_live_cache/`): Raw windows-1256 bytes
- Arabic text garbles when decoded from windows-1256; **numbers always survive**
- Live site uses `.htm`; repo uses `.html`

---

## 2. Page Structure Type 1: STANDARD (Vast Majority)

This is the structure for ~99% of pages.

```html
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<title>TOPIC TITLE</title>
<link href="../modern.css" rel="stylesheet"/>
</head>
<body>
<div class="page-wrap">
  <nav class="page-nav">
    <a href="../index-2.html">العودةلصفحة البداية</a>
    <a href="MainNN.html">العودة لفهرس الرواة</a>
  </nav>
  <div class="page-title">
    <h2>TOPIC TITLE</h2>
    <span class="hadith-count">عدد الروايات: N</span>
  </div>
  <div class="article-body">

    <!-- Optional: page intro -->
    <div class="page-intro"><p>INTRO TEXT</p></div>

    <!-- Repeated N times: one per hadith/narration -->
    <div class="hadith-block">
      <div class="scholar-name">SCHOLAR PERSONAL NAME</div>
      <div class="book-info">
        <span class="book-title">BOOK TITLE</span>
        <span class="chapter-info">CHAPTER (optional)</span>
      </div>
      <div class="ref-info">
        <span><span class="ref-label">الجزء: </span><span class="ref-value">N</span></span>
        <span><span class="ref-label">الصفحة: </span><span class="ref-value">N</span></span>
      </div>
      <div class="hadith-text">
        <span class="hadith-number">N</span>  <!-- optional -->
        <p>HADITH NARRATION TEXT</p>
        <p><span class="editorial-note">النص طويل لذا استقطع منه موضع الشاهد</span></p>  <!-- optional -->
      </div>
      <div class="analysis-note">  <!-- optional, ONE per block, INSIDE hadith-block, AFTER hadith-text -->
        <p>ANALYSIS / AUTHENTICATION TEXT</p>
      </div>
    </div>

  </div>
</div>
</body>
</html>
```

**Example**: `Aqydatona/1Wodooa.html` — 21 standard hadith-blocks, each with scholar/book/ref/hadith-text.

---

## 3. Page Structure Type 2: Collection/Evidence Page

**Known instances**: `Aqydatona/8ZQ/24ZQ.html`

Structure differs from standard:
- **scholar-name** = `( N )` — the evidence number (1 through 12)
- **No book-info div** (no book-title, no chapter-info)
- **No ref-info div** (no juz/page)
- **hadith-text** = the hadith content + all variants (`وفي رواية :`)
- **analysis-note** = numbered source list (`المصادر :`) with `<br/>` between entries
- **page-intro** = general editorial intro before the evidence blocks
- **hadith-count** span = total evidence count (12)

```html
<div class="hadith-block">
  <div class="scholar-name">( 1 )</div>
  <div class="hadith-text"><p>قال النبي : من زار قبرى ... - وفي رواية : ...</p></div>
  <div class="analysis-note"><p>المصادر :<br/>1 - الشربيني - مغني المحتاج ... - الجزء : ( 1 ) - رقم الصفحة : ( 512 ).<br/>2 - النووي - ...</p></div>
</div>
```

> **If you encounter another page with this structure, ASK the user before proceeding.**

---

## 4. Page Structure Type 3: Hadith-Number-Only

**Known instances**: `Aqydatona/12Mutaah/11Albani.html`

Structure:
- **الصفحة** holds a hadith number (not a physical page number)
- **No الجزء** span (no volume)
- Scholar often: الألباني
- Book often: كتب تخريج الحديث النبوي الشريف (or similar)

```html
<div class="ref-info">
  <span><span class="ref-label">الصفحة: </span><span class="ref-value">1234</span></span>
</div>
```

In `inspect_folder.py` this passes because الصفحة is present. The value just happens to be a hadith number.

---

## 5. Page Structure Type 4: Non-Sunni Source Note

**Known instances**: `Aqydatona/17Laen/4.html` block 22

A block where the analysis-note contains:
```
هذا المصدر ليس من المصادر السنية فانتبه عزيزي القارئ
```

This is a **warning note**, NOT the scholar-name. The actual scholar must still be in the `scholar-name` div (e.g. `أحمد بن صديق المغربي`). The note goes in `analysis-note`.

If the note text ended up in `scholar-name`, that's a NOTE_AS_SN issue — fix by moving note to analysis-note and setting the real scholar from the live page.

---

## 6. UNKNOWN STRUCTURES — STOP AND ASK

If a live page has a structure that does NOT match Types 1-4 above:
- **DO NOT** force-fit it into an existing type
- **DO NOT** assume or guess the structure
- **STOP** and ask the user to describe the correct structure
- Report: the exact file, the exact live URL, and what looks different

---

## 7. Field Rules (Strict)

### scholar-name
- **Must contain**: scholar/author **personal name** only
- **Never**: a number, a topic, a verse, a book title, editorial note, `م`/`مم`/`ممم`
- **Must not absorb**: book title, chapter info, ref info, hadith number, hadith text

### book-title
- **Must contain**: book title only
- **Never**: scholar name, narrator chain, hadith text, combined scholar+book
- **Must not absorb**: chapter info, ref info, hadith number

### chapter-info
- **Must contain**: chapter/section/باب/كتاب/فصل path only
- **Never**: hadith text, `- NUMBER - text...` patterns
- If the live page separates chapter context, preserve it exactly

### book-info
- **Must contain**: book-level structural information only
- Stay distinct from chapter info if live page separates them
- **Must not absorb**: scholar name, hadith text, ref info

### ref-info
- **Must have**: both `الجزء:` and `الصفحة:` when both exist on live page
- At minimum must have `الصفحة:`
- **Must not absorb**: hadith text, scholar name

### hadith-number
- **Optional** — only extract when clearly a distinct identifier at start of hadith text
- Keep separate from hadith-text
- Do not invent a number when none exists
- If uncertain → **STOP AND ASK**

### hadith-text
- **Must contain**: actual hadith/narration content
- **Must exist** when content is present on the live page
- Preserve full wording and order exactly as live
- **Must not absorb**: metadata labels, scholar name, book title, ref info

### analysis-note
- **Optional** — max ONE per block
- **Must be INSIDE** the `hadith-block` div
- **Must be AFTER** `hadith-text`
- Floating notes → move into correct preceding block (or first block if before all)

---

## 8. Fix Patterns Reference

### COMBINED_BT: "Scholar - Book" or "Book - Chapter"

Split on first ` -`:
- If left part is a scholar name → move to `scholar-name`, right → `book-title`
- If left part is a book name → keep as `book-title`, right → `chapter-info`

**Chapter-detection keywords** (right side is chapter if it starts with):
`كتاب`, `باب`, `فصل`, `ذكر`, `شرح`, `حرف`, `تتمة`, `جماع`, `تفسير سورة`, `الباب`, `سورة`, `موضوع`

### BOOK_AS_SN

Scholar-name has collection name (e.g. صحيح البخاري):
1. Move collection to book-title
2. Set scholar-name from live page (personal name)
3. If book-title had sub-book text → merge as chapter-info

### HADITH_IN_CI

Chapter-info contains hadith text (matches `^-\s*\d+\s*-\s*.{10,}`):
1. Extract hadith number + text
2. Create proper `hadith-text` div
3. Keep only chapter context in chapter-info
4. **MUST verify against live page**

### UNWRAPPED_EDITORIAL

```html
<!-- WRONG -->
<p>النص طويل لذا استقطع منه موضع الشاهد</p>

<!-- CORRECT -->
<p><span class="editorial-note">النص طويل لذا استقطع منه موضع الشاهد</span></p>
```

### EDITORIAL_IN_SN

Real scholar is in `book-title`. Move editorial to `hadith-text`. Set `scholar-name` from `book-title`.

### FLOATING_NOTE

Move analysis-note inside preceding `hadith-block`, after `hadith-text`. If note comes before all blocks, move into first block.

### LOOSE_P / FOOTNOTES_SECTION

- LOOSE_P: Wrap in `<div class="page-intro">` if truly introductory; otherwise convert to proper hadith-block
- FOOTNOTES_SECTION: Convert to proper hadith-block. MUST fetch live page for data.

---

## 9. Scholar Disambiguation Tables

### الطبراني — Volume determines book

| Volume | Book Title |
|--------|-----------|
| ج1–2 | المعجم الصغير |
| ج3–10 | المعجم الأوسط |
| ج11+ | المعجم الكبير |

### ابن حجر العسقلاني — Context determines book

| Context | Book Title |
|---------|-----------|
| Rijal/narrator criticism | تقريب التهذيب / تهذيب التهذيب / لسان الميزان |
| Hadith commentary | فتح الباري شرح صحيح البخاري |
| Companion biographies | الإصابة في تمييز الصحابة |
| Hadith verification | التلخيص الحبير في تخريج أحاديث الرافعي الكبير |

### الذهبي — Context determines book

| Context | Book Title |
|---------|-----------|
| Narrator criticism | ميزان الاعتدال في نقد الرجال |
| Scholar biographies | سير أعلام النبلاء |
| Brief narrator entries | الكاشف في معرفة من له رواية |

### البيهقي — Context determines book

| Context | Book Title |
|---------|-----------|
| Fiqh/legal topics | السنن الكبرى |
| Prophet's life/miracles | دلائل النبوة |
| Faith/creed | شعب الإيمان |

### الطبري vs المحب الطبري (TWO different scholars!)

- **الطبري** (d. 310H): محمد بن جرير → تفسير الطبري (جامع البيان), تاريخ الأمم والملوك
- **المحب الطبري** (d. 694H): أحمد بن عبد الله → ذخائر العقبى في مناقب ذوي القربى, الرياض النضرة

> If `book-title` = `ذخائر العقبى في مناقب ذوي القربى`, scholar **MUST** be `المحب الطبري`.

### Scholar → Book Mapping (Common)

| Scholar | Default Book | Notes |
|---------|-------------|-------|
| ابن قدامة | المغني | الشرح الكبير when chapter mentions it |
| الطحاوي | شرح مشكل الآثار | شرح معاني الآثار in fiqh context |
| الآجري | الشريعة | |
| البكري الدمياطي | إعانة الطالبين | |
| اليعقوبي | تاريخ اليعقوبي | |
| ابن عبد البر | الاستيعاب في معرفة الأصحاب | |

---

## 10. Approved Typo Fixes

Apply these on encounter:

| Wrong | Correct |
|-------|---------|
| تقسير | تفسير |
| ابن قدامه | ابن قدامة |
| ابن ابي شيبة | ابن أبي شيبة |
| Scholar `الرازي` + book `تقسير ابن أبي حاتم` | Scholar = `ابن أبي حاتم`, Book = `تفسير القرآن العظيم` |

---

## 11. Folder-Specific Patterns

### Threef — Book-organized (EXCEPTION)
Files `1Bkhari.html` through `27Taleefat.html` each represent one book's narrations.
- `scholar-name` correctly holds the **book name** (e.g. صحيح البخاري)
- This is **intentional** — NOT a BOOK_AS_SN error
- `book-title` holds chapter headers

### Mkhalfoon — Deep subfolders
- 43 subfolders (1Abubaker through 43IbnOmar)
- CSS path: `../../modern.css`
- Structure otherwise identical to standard

### ImamAli — Many subfolders, mixed sources
- 27+ subfolders
- Both Sunni and Shia sources appear
- Same field rules apply for both

### Daeefa — Shia weak hadiths
- `scholar-name` = Shia scholar, `book-title` = Shia book (الكافي, بحار الأنوار, etc.)
- Narrator chains sometimes land in `book-title` → fix needed

---

## 12. CSS Class Reference

| Class | Element | Purpose |
|-------|---------|---------|
| `.page-wrap` | `div` | Main page container (max-width: 860px) |
| `.page-nav` | `nav` | Navigation bar (maroon background) |
| `.page-title` | `div` | Title section with `<h2>` |
| `.hadith-count` | `span` | Gold badge showing narration count |
| `.article-body` | `div` | Main content area |
| `.page-intro` | `div` | Introductory paragraph(s) before hadith blocks |
| `.hadith-block` | `div` | One hadith/narration container |
| `.scholar-name` | `div` | Scholar personal name (dark background, gold accent) |
| `.book-info` | `div` | Book information container |
| `.book-title` | `span` | Book title (bold italic) |
| `.chapter-info` | `span` | Chapter/section path (muted color) |
| `.ref-info` | `div` | Reference information (volume/page) |
| `.ref-label` | `span` | Reference label (الجزء: / الصفحة:) |
| `.ref-value` | `span` | Reference value (number, bold) |
| `.hadith-text` | `div` | Hadith narration content |
| `.hadith-number` | `span` | Hadith number badge (maroon pill) |
| `.editorial-note` | `span` | Short editorial marker (purple, italic, 0.82rem) |
| `.analysis-note` | `div` | Analysis/authentication note (0.7rem, maroon border-right) |
| `.footnotes-section` | `div` | Legacy footnotes (should be converted) |

---

## 13. Helper Python Functions

```python
from bs4 import BeautifulSoup

def add_page(soup, block, page_val):
    """Add الصفحة ref to a block that's missing it."""
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
    """Fix volume value in a block's ref-info."""
    ref = block.find('div', class_='ref-info')
    if not ref: return False
    for sp in ref.find_all('span'):
        lbl = sp.find('span', class_='ref-label')
        val = sp.find('span', class_='ref-value')
        if lbl and val and 'الجزء' in lbl.get_text():
            val.string = str(new_juz); return True
    return False

def wrap_editorial(soup, p_tag):
    """Wrap editorial text in proper span."""
    span = soup.new_tag('span', attrs={'class': 'editorial-note'})
    text = p_tag.get_text(strip=True).strip('[]').strip()
    p_tag.clear()
    span.string = text
    p_tag.append(span)
```

---

## 14. Data Injection Warning

**NEVER copy data from one file to another file's blocks.**

Each file corresponds to exactly one live page. Data from `FolderA/1.htm` must only be applied to `FolderA/1.html`. Applying volume/page data from the wrong live page produces silently incorrect results.

Before applying ANY live data:
1. Verify scholar matches
2. Verify book matches
3. Verify volume matches
4. Verify hadith number matches (when present)

If mismatch → **FLAG, DO NOT APPLY**.

---

## 15. Live Page Block Format (Clean-Text Mapping)

When a live page is fetched, each hadith-block appears as:

```
Scholar — Book Title — Chapter/section context
الجزء : ( N ) - رقم الصفحة : ( N )

[ النص طويل لذا استقطع منه موضع الشاهد ]

- .... hadith text ...
```

**Mapping**:

| Clean-text part | HTML field |
|-----------------|-----------|
| First line before first ` - ` | `div.scholar-name` |
| Second part (book name) | `span.book-title` |
| Third part (chapter/section) | `span.chapter-info` |
| `الجزء : ( N )` | `ref-label` الجزء + `ref-value` N |
| `رقم الصفحة : ( N )` | `ref-label` الصفحة + `ref-value` N |
| `[ النص طويل... ]` + narration | `div.hadith-text` > `<p>` |

**Block separator on live page**: `---` (three hyphens)

**Note**: Live pages use `رقم الصفحة :` (with رقم). HTML uses `الصفحة:` (without رقم). Both map to the same ref-label.
