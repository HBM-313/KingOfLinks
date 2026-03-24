# KingOfLinks — Structural Audit Report

> Generated after full inspection of all HTML files, the SQLite database (13,249 hadiths), and the Python parser.

---

## 1. HTML Block Structure (What it Should Be)

Every `hadith-block` in every HTML file should follow this exact pattern:

```html
<div class="hadith-block">
  <div class="scholar-name">اسم العالم</div>         <!-- Scholar's personal name -->
  <div class="book-info">
    <span class="book-title">اسم الكتاب</span>       <!-- Book title only -->
    <span class="chapter-info">باب / كتاب / فصل</span> <!-- Chapter / section (optional) -->
  </div>
  <div class="ref-info">
    <span><span class="ref-label">الجزء: </span><span class="ref-value">N</span></span>
    <span><span class="ref-label">الصفحة: </span><span class="ref-value">N</span></span>
  </div>
  <div class="hadith-text">
    <span class="hadith-number">N</span>              <!-- Hadith number (optional) -->
    <p>نص الحديث</p>
  </div>
</div>
```

---

## 2. Confirmed Field Definitions

| Field | CSS Class | Should Contain | Maps to DB Column |
|---|---|---|---|
| Scholar name | `div.scholar-name` | Personal name of the scholar/narrator (e.g. **ابن حجر العسقلاني**) | `source_name` |
| Book title | `span.book-title` | Title of the book only (e.g. **فتح الباري شرح صحيح البخاري**) | `book_name` |
| Chapter info | `span.chapter-info` | Chapter/section path within the book | _(part of book context)_ |
| Volume | `div.ref-info` > `ref-value` after `الجزء` | Integer volume number | `volume` |
| Page | `div.ref-info` > `ref-value` after `الصفحة` | Page number | `page` |
| Hadith text | `div.hadith-text` | The actual narration text | `hadith_text` |
| Hadith number | `span.hadith-number` | Numeric ID within the book | `hadith_number` |

---

## 3. All Identified Data Quality Problems

### Problem A — `scholar-name` contains a TOPIC DESCRIPTION instead of a name
**Scale: ~1,127 records in DB**

The `div.scholar-name` is filled with a descriptive topic phrase instead of an actual scholar name. These are parenthesised topic headers that were mistakenly placed in the scholar field during the HTML generation.

**Examples found in HTML files:**
```html
<!-- WRONG -->
<div class="scholar-name">ابن تيمية يقر برواية الشاب الأمرد ويصححه</div>
<div class="book-info"><span class="book-title">ابن تيمية</span></div>

<!-- CORRECT should be -->
<div class="scholar-name">ابن تيمية</div>
<div class="book-info"><span class="book-title">درء تعارض العقل والنقل</span></div>
```

**Pattern in DB:** `source_name` values starting with `( ` and containing long topic text like:
- `( أحاديث وروايات في تحريف القرآن )`
- `( أبو حنيفة النعمان )`
- `( أبو بكر لا يعرف الأحكام الشرعية )`

These are **page topics**, not scholar names. The scholar name ended up in `book-title` instead.

---

### Problem B — `scholar-name` contains a HADITH NUMBER
**Scale: ~124 records in DB**

Hadith sequence numbers (like `3743`, `629`, `الحديث : ( 178 )`) appear in `div.scholar-name` instead of in `span.hadith-number` inside `div.hadith-text`.

**Example:**
```html
<!-- WRONG -->
<div class="scholar-name">‏3743</div>
<div class="book-info">
  <span class="book-title">حدثنا : ‏ ‏سليمان بن حرب...</span>  <!-- narrator chain in wrong place -->
</div>

<!-- CORRECT should be -->
<div class="scholar-name">البخاري</div>
<div class="book-info"><span class="book-title">صحيح البخاري</span> <span class="chapter-info">- كتاب فضائل الصحابة</span></div>
<div class="hadith-text">
  <span class="hadith-number">3743</span>
  <p>حدثنا : سليمان بن حرب...</p>
</div>
```

---

### Problem C — `scholar-name` is a SINGLE LETTER (`ا`)
**Scale: scattered across multiple files**

Appears when the block was split mid-sentence during HTML generation. The `ا` is the first letter of the next scholar's name that got cut off.

**Example from files:**
```html
<div class="scholar-name">ا</div>
<div class="book-info">
  <span class="book-title">أبو يعلى ابن الفراء</span>  <!-- scholar name in book field -->
  <span class="chapter-info">- ابطال التأويلات...</span>
</div>
```

Here the **real scholar** is `أبو يعلى ابن الفراء` and the **real book** is `ابطال التأويلات لأخبار الصفات`. Both fields are swapped.

---

### Problem D — `scholar-name` contains EDITORIAL NOTES
**Scale: scattered**

Editorial/source notes appear in scholar-name:
```html
<!-- WRONG -->
<div class="scholar-name">[النص طويل لذا استقطع منه موضع الشاهد ]</div>
<div class="book-info"><span class="book-title">صحيح البخاري</span></div>
```

The note `[النص طويل لذا استقطع منه موضع الشاهد ]` belongs inside `div.hadith-text` as a `<p>` tag, not in scholar-name. The scholar is missing entirely from this block.

---

### Problem E — `scholar-name` contains a QURANIC VERSE
**Scale: isolated cases**

HTML block was split at the wrong `<hr>` and Quranic verse text ended up in scholar-name:
```html
<!-- WRONG -->
<div class="scholar-name">سورة : { وَاللَّيْلِ إِذَا يَغْشَى @ وَالنَّهَارِ إِذَا تَجَلَّى @ ( الليل : 1</div>
<div class="book-info"><span class="book-title">2 ) }</span></div>
```
This is a broken split — the verse should be inside `hadith-text` and there should be a proper scholar/book header.

---

### Problem F — `book-title` contains the SCHOLAR NAME (swapped fields)
**Scale: very common**

Scholar name ends up in `span.book-title` while `div.scholar-name` is wrong, empty, or has only a single letter.

**Example:**
```html
<!-- WRONG -->
<div class="scholar-name">ا</div>
<div class="book-info">
  <span class="book-title">أبو يعلى ابن الفراء</span>
  <span class="chapter-info">- ابطال التأويلات لأخبار الصفات - فصل ثان</span>
</div>

<!-- CORRECT -->
<div class="scholar-name">أبو يعلى ابن الفراء</div>
<div class="book-info">
  <span class="book-title">ابطال التأويلات لأخبار الصفات</span>
  <span class="chapter-info">- فصل ثان يتعلق بليلة الإسراء</span>
</div>
```

---

### Problem G — `book-title` contains NARRATOR CHAIN TEXT
**Scale: moderate**

A full `حدثنا / أخبرنا` narrator chain appears inside `span.book-title` instead of inside `div.hadith-text`.

**Example:**
```html
<!-- WRONG -->
<div class="scholar-name">الكليني</div>
<div class="book-info">
  <span class="book-title">محمد بن يحيى، عن سعد بن عبد الله ،عن إبراهيم بن محمد الثقفي، عن علي بن المعلى...</span>
</div>

<!-- CORRECT -->
<div class="scholar-name">الكليني</div>
<div class="book-info">
  <span class="book-title">الكافي</span>
  <span class="chapter-info">- كتاب الحجة - باب مولد النبي (ص)</span>
</div>
<div class="hadith-text">
  <p>محمد بن يحيى، عن سعد بن عبد الله ،عن إبراهيم بن محمد الثقفي...</p>
</div>
```

---

### Problem H — `book-title` contains COMBINED Scholar + Book (no separator standard)
**Scale: common**

Multiple separator styles are used to combine scholar and book in one field:

```html
<!-- Variations all found in files: -->
<span class="book-title">السيد الخوئي -كتاب الطهارة</span>
<span class="book-title">صحيح البخاري -كتاب فضائل الصحابة</span>
<span class="book-title">صحيح مسلم-كتاب الإيمان</span>
<span class="book-title">صحيح مسلم-كتابالرضاع- باب :التحريم بخمس رضعات</span>
```

**Correct split:** Everything before the `-` goes into `scholar-name`, everything after is `book-title` + `chapter-info`.

---

### Problem I — `book-title` contains a QURANIC VERSE REFERENCE as book name
**Scale: isolated**

```html
<!-- WRONG -->
<div class="scholar-name">صحيح البخاري</div>
<div class="book-info">
  <span class="book-title">سورة المائدة : 117</span>
  <span class="chapter-info">- باب : { كُنتُ عَلَيْهِمْ شَهِيدًا... }</span>
</div>

<!-- CORRECT -->
<div class="scholar-name">البخاري</div>
<div class="book-info">
  <span class="book-title">صحيح البخاري</span>
  <span class="chapter-info">- تفسير سورة المائدة (117) - باب : { كُنتُ عَلَيْهِمْ شَهِيدًا... }</span>
</div>
```

The Quran verse reference is a chapter location, not the book title.

---

### Problem J — `book-title` is EMPTY or just a partial letter
**Scale: 4,253 records with empty book_name in DB (32%)**

Many blocks have `div.scholar-name` correctly filled but `span.book-title` is missing or just `"ا"`. The book title needs to be added.

---

## 4. Special Folder Patterns

### `Threef/` — Content organized by Scholar/Book, not topic
Files `1Bkhari.html` through `27Taleefat.html` each represent one book/scholar's narrations. In these files:
- `div.scholar-name` correctly holds the book name (e.g. `صحيح البخاري`)
- But `span.book-title` often holds chapter headers or narrator chains
- The scholar's personal name (e.g. محمد بن إسماعيل البخاري) is never shown — only the book title appears in `scholar-name`

### `Daeefa/` — Shia weak hadiths
Same structure as all other folders. `scholar-name` = Shia scholar, `book-title` = the Shia book (الكافي, بحار الأنوار, etc.). Issues: narrator chains land in `book-title`.

### `Mkhalfoon/` — Deep subfolder nesting (2 levels)
Files like `Mkhalfoon/1Abubaker/4Fltah.html`. CSS path: `../../modern.css`. Structure is otherwise identical.

### `ImamAli/`, `ImamHussain/`, etc. — Mix of Sunni and Shia sources
Both Sunni books (صحيح البخاري, مسند أحمد) and Shia books (الكافي, بحار الأنوار) appear. The same `scholar-name` / `book-title` rules apply for both.

---

## 5. Database Impact Summary

| Issue | Affected DB Column | Count |
|---|---|---|
| Empty `source_name` | `source_name` | 450 |
| `source_name` = topic description | `source_name` | ~1,127 |
| `source_name` = hadith number | `source_name` | 124 |
| Empty `book_name` | `book_name` | 4,253 |
| `book_name` = scholar name (swapped) | `book_name` | significant |
| `book_name` = narrator chain | `book_name` | moderate |
| `book_name` = combined scholar+book | `book_name` | common |

---

## 6. Normalization Goals (Next Step)

When cleaning/standardizing, apply these rules to every `hadith-block`:

1. **`div.scholar-name`** → Must be a **person's name only** (النووي، البخاري، ابن حجر العسقلاني). No numbers, no topic text, no verse text, no editorial notes.

2. **`span.book-title`** → Must be a **book title only** (صحيح البخاري، الكافي، بحار الأنوار). No scholar name, no narrator chain, no chapter path.

3. **`span.chapter-info`** → All chapter/section/باب/كتاب paths go here. Can be multiple spans.

4. **`div.hadith-text` > `span.hadith-number`** → All numeric hadith identifiers (e.g. `3743`) go here.

5. **Splitting combined fields** — When `span.book-title` contains `Scholar - Book`, split on `-` and place the scholar in `div.scholar-name`.

6. **`[النص طويل...]` editorial note** → Move to first `<p>` in `div.hadith-text`.

---

## 6b. Multi-Book Scholar Disambiguation

Several scholars authored multiple books. The correct book title depends on **file/folder context** and **volume number**. Known mappings:

### الطبراني — Volume determines which معجم:
| Volume range | Book title |
|---|---|
| ج1–2 | المعجم الصغير |
| ج3–10 | المعجم الأوسط |
| ج11+ | المعجم الكبير |

### ابن حجر العسقلاني — Context determines book:
| File context | Book title |
|---|---|
| Rijal/narrator criticism files | تقريب التهذيب **or** تهذيب التهذيب **or** لسان الميزان |
| Hadith commentary context | فتح الباري شرح صحيح البخاري |
| Companion biographies | الإصابة في تمييز الصحابة |
| General | الإصابة في تمييز الصحابة (default) |

### الذهبي — Context determines book:
| File context | Book title |
|---|---|
| Rijal/narrator criticism | ميزان الاعتدال في نقد الرجال |
| Companion/scholar biographies | سير أعلام النبلاء |
| Brief narrator entries | الكاشف في معرفة من له رواية |
| Default | سير أعلام النبلاء |

### البيهقي — Context determines book:
| File context | Book title |
|---|---|
| Fiqh/legal topics | السنن الكبرى |
| Prophet's life/miracles | دلائل النبوة |
| Faith/creed | شعب الإيمان |
| Default | السنن الكبرى |

### الطبري — Name ambiguity (TWO different scholars):
- **الطبري** (d. 310H): محمد بن جرير — books: تفسير الطبري (جامع البيان), تاريخ الأمم والملوك
- **المحب الطبري** (d. 694H): أحمد بن عبد الله — books: ذخائر العقبى في مناقب ذوي القربى, الرياض النضرة في مناقب العشرة
- When `bt` = 'ذخائر العقبى', scholar **must** be **المحب الطبري**, not الطبري.
- **Confirmed fix**: `ImamAli/1AlAyat/34Serran.html` b12 corrected from `الطبري` to `المحب الطبري`.

---

## 6c. Patterns Discovered During Automated Cleanup (Sessions 5–6)

### Pattern K — Missing scholar-name div entirely (structural absence)
**Distinct from Problem F:** The `<div class="scholar-name">` element is completely absent from the block (not just empty). The `span.book-title` holds the scholar name as its entire content.

```html
<!-- WRONG — div entirely missing -->
<div class="hadith-block">
  <div class="book-info">
    <span class="book-title">الطبراني</span>    <!-- scholar name stored here -->
  </div>
  ...
</div>

<!-- CORRECT -->
<div class="hadith-block">
  <div class="scholar-name">الطبراني</div>
  <div class="book-info">
    <span class="book-title">المعجم الكبير</span>
  </div>
  ...
</div>
```
**Fix:** Insert new `<div class="scholar-name">` before `<div class="book-info">`, set book-title from global mapping.

### Pattern L — scholar_eq_book (both fields contain the same scholar name)
After inserting a missing scholar-name div (Pattern K), both `scholar-name` and `book-title` contain the same value. This happens when the only available data was the scholar name — there was no separate book title stored.

**Fix:** Apply book title from global scholar→book mapping (see §6b), using in-file context first (other blocks in same file with same scholar), then volume-number logic (الطبراني), then global default.

### Pattern M — Truncated book-title fragments
`span.book-title` contains only a partial word: `'ا'`, `'تا'`, `'كتا'`, `'شر'`, `'ك'`. These are the first letter(s) of a book title that was truncated during HTML generation.

**Fix:** Infer book title from scholar + file context. If the fragment matches the start of a known book title (e.g. `'كتا'` → كتاب السنة or كتاب الصلاة), use that. Otherwise flag for live-data verification.

### Pattern N — Quran surah name in scholar-name (variant of Problem E)
`div.scholar-name` contains a surah name only (e.g. `'البقرة'`, `'آل عمران'`) while `span.book-title` contains the Quran verse text. This differs from Problem E (long verse text in sn) — here only the surah name appears.

**Root cause:** The block's first line was a Quran verse context header; the surah name was extracted as the "scholar."

**Fix:** Scholar should be the actual hadith scholar whose citation follows. If the block is purely a verse header with a citation, the scholar and book are both unknown without live data.

**Open instance:** `ImamAli/1AlAyat/34Serran.html` b1 — sn=`البقرة`, bt=Quran verse, ref=ج1/ص708. Live page appears to show ابن رشد but text was garbled. **Flagged for manual review.**

### Pattern O — Combined content in scholar-name (Problem H variant in sn field)
Scholar-name contains combined `Scholar - Book - Chapter` text:
```html
<div class="scholar-name">ابن عساكر -تاريخ دمشق- حرف : ا</div>
```
**Fix:** Split on ` -`: first part → scholar-name, second part → book-title, third part → chapter-info.

---

## 6d. Missing Page Numbers (Pattern P)

**Scale: 624 blocks across 171 files** (as of session 6)

Blocks have `الجزء:` (volume) but no `الصفحة:` (page). The page number exists on the live site but was omitted from the local HTML.

**Live site URL pattern:** `http://kingoflinks.net/{folder}/{path}.htm` (note `.htm` not `.html`)

**Fetch constraint:** The web_fetch tool only allows URLs provided by the user or appearing in search results. Fetching 171 files requires the user to provide URLs in batches.

**Arabic number encoding:** Live pages return garbled Arabic text (encoding issues in the markdown extraction). Numbers remain readable but Arabic labels are corrupted. Use numeric patterns only for extraction.

**Format variations found on live site:**
- Simple page: `ص123`
- Span: `ص100 / 101`  
- Multi-page: `ص274 / 176 / 419`
- Range: `ص140 إلى 149` (stored as `140 - 149`)

**رقم الحديث vs صفحة:** Some blocks on the live site use `رقم الحديث:` (hadith number) instead of `الصفحة:`. When fixing, check which label type is used per block on the live site.

---

## 7. Known Good Examples (Reference)

The following blocks are correctly structured and can serve as templates:

**Sunni book reference (correct):**
```html
<div class="hadith-block">
  <div class="scholar-name">ابن حجر العسقلاني</div>
  <div class="book-info">
    <span class="book-title">فتح الباري شرح صحيح البخاري</span>
    <span class="chapter-info">- كتاب الحدود - باب : رجم الحبلي من الزنا إذا أحصنت</span>
  </div>
  <div class="ref-info">
    <span><span class="ref-label">الجزء: </span><span class="ref-value">12</span></span>
    <span><span class="ref-label">الصفحة: </span><span class="ref-value">129</span></span>
  </div>
  <div class="hadith-text">
    <p>النص طويل لذا استقطع منه موضع الشاهد</p>
    <p>- .... قوله : ( فوالله ما كانت بيعة أبي بكر الا فلتة )...</p>
  </div>
</div>
```

**Shia book reference (correct):**
```html
<div class="hadith-block">
  <div class="scholar-name">الشهيد الثاني</div>
  <div class="book-info">
    <span class="book-title">شرح اللمعة</span>
  </div>
  <div class="ref-info">
    <span><span class="ref-label">الجزء: </span><span class="ref-value">3</span></span>
    <span><span class="ref-label">الصفحة: </span><span class="ref-value">96</span></span>
  </div>
  <div class="hadith-text">
    <p>- ... علي بن أبي حمزة البطائني وهو من الكذابين...</p>
  </div>
</div>
```

**With hadith number (correct):**
```html
<div class="hadith-block">
  <div class="scholar-name">الدارقطني</div>
  <div class="book-info">
    <span class="book-title">رؤية الله</span>
    <span class="chapter-info">- ذكر الرواية عن أم الطفيل امرأة أبي بن كعب</span>
  </div>
  <div class="ref-info">
    <span><span class="ref-label">الجزء: </span><span class="ref-value">1</span></span>
    <span><span class="ref-label">الصفحة: </span><span class="ref-value">358</span></span>
  </div>
  <div class="hadith-text">
    <span class="hadith-number">286</span>
    <p>286 - حدثنا : محمد بن اسماعيل الفارسي...</p>
  </div>
</div>
```

---

## 8. Open Issues — Require Manual Review

The following issues could NOT be resolved automatically. Each is flagged with the exact file, block, and reason.

### 8a. Unresolvable scholar-name blocks

| File (live URL) | Block | Issue | Reason |
|---|---|---|---|
| http://kingoflinks.net/ImamAli/1AlAyat/34Serran.htm | b1 | sn=`البقرة` (SURAH_IN_SN) | Live page showed garbled Arabic; first block appears to reference ابن رشد ج1/ص708 but cannot confirm. Page already set. |
| http://kingoflinks.net/ImamAli/1AlAyat/34Serran.htm | b12 | sn=`الطبري` but book=`ذخائر العقبى` | ذخائر العقبى was written by **المحب الطبري** (d.694H), not الطبري the historian (d.310H). Scholar name likely wrong. |

### 8b. Missing page numbers still requiring live URL fetches

624 blocks across 171 files need صفحة values from the live site. Full list in session audit output. Waiting for user to provide URLs in batches.

---

## 9. Session Progress Log

| Session | Commits | Issues Fixed | Issues Remaining |
|---|---|---|---|
| Sessions 1–4 | Multiple | loose_p, frag_note, bad_scholar in 5 folders | All other folders |
| Session 5 | b3ff4b4, ffa682b, b250f93, 9a302cb | 122 loose_p, 508 loose_p, 133 scholars, 1344 missing scholar divs | missing_page, scholar_eq_book, empty_scholar |
| Session 6 | ea4cb88, caf0d12 | 1076 scholar_eq_book, 64 empty scholars, partial pages | 624 missing_page, 2 open manual-review |


---

## 10. Clean-Text Block Parsing Logic

When a live page is fetched as clean text (not garbled markdown), each hadith-block appears in this exact pattern:

```
Scholar — Book Title — Chapter/section context
الجزء : ( N ) - رقم الصفحة : ( N )

[ النص طويل لذا استقطع منه موضع الشاهد ]

- .... hadith text ...
```

**Mapping to HTML fields:**

| Clean-text part | HTML field |
|---|---|
| First line before first ` - ` | `div.scholar-name` |
| Second part (book name) | `span.book-title` |
| Third part (chapter/section/verse reference) | `span.chapter-info` |
| `الجزء : ( N )` | `ref-label` الجزء + `ref-value` N |
| `رقم الصفحة : ( N )` | `ref-label` الصفحة + `ref-value` N |
| `[ النص طويل... ]` + narration | `div.hadith-text` > `<p>` |

**Separator between blocks on live page:** ` --- ` (three hyphens)

**Confirmed example** from `34Serran.htm` b1:
```
ابن كثير - تفسير ابن كثير - تفسير سورة البقرة : 272
تفسير قوله تعالى : { لَّيْسَ عَلَيْكَ هُدَاهُمْ ... }
الجزء : ( 1 ) - رقم الصفحة : ( 708 )
[ النص طويل لذا استقطع منه موضع الشاهد ]
- .... وقال ابن أبي حاتم : ...
```
→ scholar=`ابن كثير`, book=`تفسير ابن كثير`, chapter=`تفسير سورة البقرة : 272 - تفسير قوله تعالى...`, ج=1, ص=708

**Note on `رقم الصفحة` label:** Live pages use `رقم الصفحة :` (with رقم). HTML blocks use `الصفحة:` (without رقم). Both map to the same `ref-label` = `الصفحة:` in HTML. Some blocks use `رقم الحديث:` instead — these are hadith-numbered sources, stored in `span.hadith-number`, not `ref-info`.


---

## 11. Scholar → Book Mapping (Confirmed)

When `scholar_eq_book` occurs (sn=bt), or when bt is empty, use this confirmed mapping:

| Scholar | Correct Book Title | Notes |
|---|---|---|
| ابن قدامة | المغني | Default when no chapter context |
| ابن قدامة | الشرح الكبير | When chapter-info mentions الشرح الكبير |
| الطحاوي | شرح مشكل الآثار | When context is hadith analysis |
| الطحاوي | شرح معاني الآثار | When context is fiqh |
| الآجري | الشريعة | Default |
| الشربيني | السراج المنير شرح الجامع الصغير | When ج=4 |
| البكري الدمياطي | إعانة الطالبين | Default |
| اليعقوبي | تاريخ اليعقوبي | Default |
| ابن عبد البر | الاستيعاب في معرفة الأصحاب | Companion biographies |
| الصنعاني | تفسير عبد الرزاق | Tafsir context |
| الصنعاني | المصنف | Hadith collection context |

---

## 12. الطبراني Volume→Book Rule (Confirmed)

| Local ج value | Correct book | Action |
|---|---|---|
| ج1–2 | المعجم الصغير | Keep volume, fix bt |
| ج3–10 | المعجم الأوسط | Keep volume, fix bt |
| ج11+ | المعجم الكبير | Keep volume, fix bt |

**Example fixed:** `Mkhalfoon/24Waleed/4Saher.html` b7 had local ج2/bt=المعجم الصغير → live showed ج8/ص234 → corrected to ج8/bt=المعجم الأوسط.

When local volume contradicts the الطبراني rule, trust live page volume over local.

---

## 13. Typo Fixes Found

| Wrong | Correct | Location |
|---|---|---|
| تقسير ابن أبي حاتم | تفسير القرآن العظيم | 18Khoms/2,3,4 b19,b9,b12 — scholar should be ابن أبي حاتم not الرازي |
| ابن قدامه | ابن قدامة | Multiple files |
| ابن ابي شيبة | ابن أبي شيبة | Multiple files |

**Note on تفسير ابن أبي حاتم:** The book is correctly titled `تفسير القرآن العظيم`. The scholar field sometimes shows `الرازي` (his family name), but should be `ابن أبي حاتم` (عبد الرحمن بن أبي حاتم الرازي). Always use `ابن أبي حاتم` as scholar name.

---

## 14. Hadith-Text Must Always Be Present

**CRITICAL RULE (added session 7):** The `hadith-text` div must ALWAYS be present when the live page shows narration content. A block with scholar/book/ref but no `hadith-text` is a content loss error — not a formatting issue.

**Rule:** Hadith text always appears **after** page numbers in clean-text format:
```
الجزء : ( N ) - رقم الصفحة : ( N )
[ النص طويل... ]
- .... hadith text
```

If `hadith-text` is missing from a local block, check live page and restore the full narration with proper `<span class="hadith-number">` + `<p>` structure.

**Fixed examples:**
- `ImamHussain/4Syed/16IbnAsaker.html` b5: hadith 3250 narrator chain restored
- `ImamHussain/4Syed/16IbnAsaker.html` b6: hadith 3840 narrator chain restored
- `ImamHussain/4Syed/16IbnAsaker.html` b9: two أنس بن مالك and حميد بن أنس paragraphs restored

---

## 15. Data Injection Error — Critical Warning

**NEVER apply page/volume data from one file to blocks in a different file.**

Session 7 caught a critical error: page data from `ImamAli/1AlAyat/1Ttheer/19IbnAsaker.html` was accidentally applied to `ImamHussain/4Syed/16IbnAsaker.html` b8-b11, producing completely wrong volume+page values (ج13/208 etc. instead of the correct ترجمة pages).

**Prevention rule:** Before applying any live-page data to a block, ALWAYS verify:
1. The local block's scholar/book matches what the live page shows for that block
2. The volume number matches
3. The hadith number (if present) matches

If any field mismatches, DO NOT apply — flag as open issue instead.

---

## 16. Session Progress Log (Updated)

| Session | Commits | Fixes Applied | Missing Pages After |
|---|---|---|---|
| Sessions 1–4 | Multiple | loose_p, frag_note, structural fixes in 4 folders | — |
| Session 5 | b3ff4b4–9a302cb | 1,876 structural fixes | 624 |
| Session 6 | ea4cb88–caf0d12 | 1,076 scholar_eq_book, 64 empty scholars | 618 |
| Session 7 | 50e6a10–4907dcb | 34Serran b1/b10/b12/b19/b20, 70 المحب الطبري | 596 |
| Session 8 | 652bd00–a7f7713 | Batch 1: 22 pages + 6 vols + 12 structural | 596→ |
| Session 9 (sitemap) | 0b1e05c–a5f855f | 57 pages, 8 vols, 20+ structural, hadith-text restores | 561 |
| Session 10 | 93fb789 | 64 pages + 30 structural (6 large files) | 497 |

**Current state (Session 10 end):** missing_page=497, empty_scholar=1, scholar_eq_book=0

