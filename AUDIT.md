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



## 17. Live-verification findings — AhlAlBait batch 25 (2026-10-20)

This is an **additive live-source audit note**; historical audit metrics above must not be treated as present-day verification.

- Target pages: `AhlAlBait/3Mbahala/6IbnKatheer.html` (4 original source blocks), `7Syooti.html` (2), `8Tabari.html` (6).
- All three were missing an independent original Quranic `page-intro`. Its omission can escape a block-count audit.
- Full passage diffs showed omitted Quran wrappers `{ }`, sura/verse citations (`آل عمران : 61`; `آل عمران : 59 - 60 - 61`), diacritics, punctuation and small text fragments. A 95–99% similarity score is not sufficient, even if paragraphs appear to align.
- The three HTML files were revised and their committed contents re-read on `main` (commits `62ea6273`, `f66d7bcf`, `8febfe37`), followed by checklist update `33305cda` (recorded 75/210).
- **Residual defect requiring follow-up:** in `AhlAlBait/3Mbahala/8Tabari.html`, source/hadith number `2634` remained both inside a `hadith-number` element and at the beginning of a `<p>` element. Directly verify live original and remove only the redundant duplication, preserving the hadith number once in the correct field. The prior `[x]` does not supersede this documented issue.
- New regression checks: missing `page-intro` at page start; text extraction stripping `{ }`, `@`, Quran verse labels or combining paragraphs; number duplication across elements; original heading mistakenly placed in `hadith-text`; bibliographic information displaced into other fields; original source headings and sequential hadith-block boundaries.
- A clean automated audit or successful commit alone does **not** meet the DONE rule; source text, ownership, and block structure must all be verified, and the exact committed file must be re-read.

**Resolution 2026-10-20:** The previously noted duplicate number `2634` in `AhlAlBait/3Mbahala/8Tabari.html` has been corrected after direct comparison with the original `kingoflinks.net` page. It now appears only once in the HTML `hadith-number` field; the redundant number in the following paragraph was removed. HTML commit: `504dcd46`, re-fetched and checked from `main`. The earlier note is retained as historical evidence of the failure mode.


## Required Audit Sign-off: Complete Fix Only (2026-10-20)

**Zero tolerated known discrepancies at batch sign-off.** Audit all three layers separately against the *current* original: (1) complete meaningful content, (2) correct ownership in `page-intro`, `scholar-name`, `book-title`, `chapter-info`, `ref-info`, `hadith-number`, `hadith-text`, editorial and analysis fields, and (3) one-to-one ordered source-block boundaries. Restore all missing, altered, moved or duplicated text, including Quran punctuation, verse references, unusual characters and bibliographic markers. A partial repair or a matching count is never a pass. Commit repairs, read the final committed files back from `main`, and perform full post-commit checks before checklist sign-off. If any known discrepancy or verification gap remains, the batch is **not finished** and the next batch may not start.


## Live-source audit additions — recurring failure modes, batches 46–50 (2026-10-21)

Use this as a **per-page and per-block sign-off checklist**, alongside the earlier three-gate verification requirement:

- [ ] Match `sitemap.xml` original URL and decode original correctly (including `windows-1256` where applicable); verify entire original, not earlier reports.
- [ ] Check page heading, independent `page-intro` where present, navigation, all original source counts and boundaries in order.
- [ ] Require `scholar-name` as a standalone field, not nested under `book-info` (observed in `9Khleefa/3Muslim.html`, `7Hakim.html`).
- [ ] Validate complete `book-title` against the source; reject truncated titles (observed `ا` in `8Njoom.html`) or titles inferred from a chapter or scholar.
- [ ] Assign every source-specific book/chapter/section heading to `chapter-info`, not `hadith-text`. Verify every repeated heading separately (34 sources in `9Khleefa/4IbnHnbal.html`).
- [ ] Count each independent source block even where hadith numbers repeat (e.g. `1821` in `3Muslim.html`); require number ownership only in `hadith-number` without redundant opening-body duplication.
- [ ] Compare complete narration across original/local paragraph splits **within the same block**; then inspect for small missing words, punctuation and Quran text even if similarity is >99% (e.g. `وأنا أمان لأصحابي` in `8Njoom.html`).
- [ ] Preserve editorial-note brackets and classify source judgments independently under `analysis-note` (e.g. `نوع الحديث : صحيح`).
- [ ] Allow only certain, meaning-preserving repairs of clear accidental split words, e.g. `ر سول`→`رسول`, `ا لترمذي`→`الترمذي`, `ا لمستدرك`→`المستدرك`, `حد يث`→`حديث`, `ا لجزء`→`الجزء`; document them as typo normalizations, not source omissions. **Do not** normalize ambiguous/source-significant spelling, numerals, references or religious quotations without evidence.
- [ ] For `Main*.html`, audit each ordinal, destination, unique label, count, order and page total; `7SafinatNooh/Main61.html` was a concrete failure with 13 repeated labels and erroneous counts.
- [ ] If Sandbox expires or quota blocks creation, resume an available named session and repeat any interrupted original-source comparisons; technical failure is not a pass.
- [ ] Commit all repairs, re-fetch the latest committed contents (`main` or exact commit SHA, avoiding stale raw-cache responses), redo the three gates and only then mark `tjek.md` entries `[x]`.

**Audit principle:** A difference traceable solely to an indisputable stray space/word split may be corrected; otherwise the original is authoritative. Do not silently excuse other mismatches using the typographical exception.


## Narrator evaluation card audit (2026-10-21)

- [ ] When an original page has a narrator-assessment grid/table, count each original narrator cell and each assessor–verdict pair; compare them **cell by cell and in order** against `narrator-card` and `narrator-evaluation` elements. Preserve all independent remarks in `narrator-remark`.
- [ ] Verify structured field ownership: `narrator-name` = narrator only; `evaluation-scholar` = assessing scholar only; `evaluation-text` = exact original assessment only; separate source citations and hadiths retain their own fields. Never replace missing attributions by guesswork.
- [ ] Check shared `modern.css` and responsive layout: 3 columns desktop, 2 tablet, 1 mobile; original Arabic readable, all assessments immediately visible, no per-page inline styling duplicates.
- [ ] **Verify deployed assets**, not only repository files: live page must contain the intended `narrator-card` markup **and** live `/modern.css` must include `.narrator-grid` and corresponding styles. If deployment is stale, redeploy the right `main` commit and re-check the public site.
- [ ] Preserve full original bibliography, commentary and independent source boundaries alongside narrator cards. A passed card/UI audit does not replace full original-to-local three-gate page verification.
- [ ] Regression examples: `10Hrbhom/2Trmethee.html` 6 cards / 22 assessments and `3IbnMajah.html` 6 cards / 31 assessments, checked against the original tables (53 assessments total). These totals are specific to these pages, **not** a template count for future pages.


## Mandatory independent character-by-character original-text verification (2026-10-27)

**Completion gate — non-negotiable:** A page is NOT fully verified merely because the deployed HTML matches a locally reconstructed HTML file, because source counts match, or because GitHub matches deployment. The reconstruction itself MUST be independently checked against the actual corresponding `kingoflinks.net` original `.htm` page.

1. Retrieve the actual original URL identified in `sitemap.xml` (decode `windows-1256` correctly when applicable) and the FINAL committed GitHub `.html` version. Use original source HTML/text, not another local reconstruction, old audit, checklist tick, or cached raw GitHub response as the independent authority.
2. Identify **every** meaningful original text segment in DOM/source reading order: title / `page-intro`, ALL source headers, author, book, chapter, volume/page/page ranges, hadith numbers, full narration, Quranic content including diacritics and `{ }`, editorial notes, footnotes (`الحاشية`, `الحاشية رقم`), analyses, separators and any text outside `<p>` elements. Do not lose text split among nested elements or text nodes.
3. Map each original segment to the correct structural owner in the FINAL committed HTML; compare **character by character** for content, punctuation, digits, Arabic letters, Quranic diacritics, brackets, symbols, and editorial wording, **for every individual original text segment**, not only totals or representative samples. Separately confirm field ownership and independent source/block boundaries/order; equal words appearing in the wrong field do not pass.
4. Account explicitly for purely presentational HTML markup and documented harmless whitespace/entity normalisation. Do **not** silently erase real characters or meaningful spacing to force a match. Only fix unambiguous source typographical/spacing defects under the existing narrowly qualified project rule, documenting the exception. Any unexplained mismatch or original text without a mapped destination is a **failure** requiring correction and another complete comparison.
5. Perform the comparison against the **post-commit** file, not only the pre-commit candidate. Record a per-page evidence summary (number of original segments vs. verified mapped segments, original source blocks vs. local `hadith-block` count/order, exact comparison result, and every justified normalisation/exception). The production check is additional, **not a substitute** for independent original-to-final-content comparison.
6. Only after **zero unexplained original-to-committed-content mismatches**, correct ownership and source grouping, all corrections committed, and deployment aftercheck may the page be marked `[x]` in `tjek.md`. Never advance a batch with missing character-level verification; reopen earlier `[x]` pages if this evidence was not actually collected.

**Mandatory wording in status reports:** Distinguish “deployment matches reconstruction” from “every original text segment independently compared character by character to final committed HTML.” Never report full original fidelity or absolute no-missing-content verification unless the latter check was actually performed and passed.


## Seerah batch 13 — independent original-source aftercheck (2026-10-27)

Scope, against the corresponding `kingoflinks.net` `.htm` originals decoded as `windows-1256`, and the committed/deployed `.html` pages:
- `Seerah/1Zahf/OTH/18Other.html`: 8/8 independent source blocks; 8/8 complete narration texts found as contiguous matching sequences in the original after whitespace normalisation; 8/8 volume/page pairs equal; numbered hadith values present.
- `Seerah/2Mnafig12.html`: 3/3 source blocks; 3/3 matching narration texts; 3/3 volume/page pairs equal; hadith number 2779 preserved.
- `Seerah/3Hawdh.html`: 20/20 bibliographic source blocks; 20/20 matching narration texts; 20/20 volume/page pairs equal; all visible hadith numbers preserved. Original page counter says 21 narrations; this is not itself evidence for a 21st independent source block.
- All book-title and scholar strings checked for presence against original source; chapter strings checked against the original continuous body text. In `18Other.html` source block 5, chapter information spans TWO adjacent original header paragraphs; the joined structured chapter text consequently is not a single continuous original substring.
- Comparison method: independently re-fetched original body text, collapsed HTML-origin whitespace, compared **entire individual local narration strings** as exact contiguous Unicode substrings (not similarity scores), compared all numeric bibliography values character-for-character, and checked metadata. Editorial material embedded in narration strings is included in these checks.
- **Evidence limit:** This confirms text equality *after documented whitespace normalisation*, not raw source-byte equality, and does not certify a fully audited one-to-one character mapping for every original source header and navigational text node. An absolute claim of zero raw-character discrepancies requires a more granular source-node-to-field comparison. The current `[x]` marks predate that stricter level; do not treat this entry alone as proof that the full new mandatory gate is satisfied.


## Seerah batch 13 — mandatory paragraph, field and source-boundary re-verification (2026-10-27)

**Final result: PASS — all three pages, 31/31 independent original source sections.** This replaces the evidence limitation in the preliminary audit entry above; the preliminary report was not itself sufficient for approval.

Originals obtained freshly through Vercel Sandbox, using Python `urllib.request` with `User-Agent: Mozilla/5.0`, from the original `kingoflinks.net` `.htm` URLs; decoded as `windows-1256`. Corresponding `.html` files were re-fetched from the committed GitHub `main` ref **after** the corrections. The independent comparison operated on the original source HTML and the resulting committed HTML, not on the earlier audit or cached extracted narration snippets.

| Original → committed page | Original sections split at original `<hr>` boundaries | Local `hadith-block` | Final failures |
| --- | ---: | ---: | ---: |
| `Seerah/1Zahf/OTH/18Other.htm` → `Seerah/1Zahf/OTH/18Other.html` | 8 | 8 | 0 |
| `Seerah/2Mnafig12.htm` → `Seerah/2Mnafig12.html` | 3 | 3 | 0 |
| `Seerah/3Hawdh.htm` → `Seerah/3Hawdh.html` | 20 | 20 | 0 |

**Exact verification scope and procedure:** Each original source section, including its full narration and source-attached editorial text (including text nodes outside `<p>` elements), was reconstructed in DOM reading order, associated with its specific original bibliography paragraph, and compared character by character with the matching `hadith-text` in the same ordered committed `hadith-block`. Only HTML-origin whitespace/nonbreaking spaces and the leading bidirectional right-to-left format marker before some original numbered narrations were normalized. The original number-to-narration hyphens are now explicitly present in the committed HTML. Original source chapter/header paragraphs were also mapped individually against each block's `scholar-name`, `book-title` and `chapter-info`, permitting only documented cross-field source-header separator normalization. Each original bibliographic volume/page character value was matched with the corresponding committed `ref-value`, including the unusual original volume `0 8` (not silently changed to `8`). Original source order and all source boundaries match. Original heading text, heading parentheses, displayed narration counters, and top navigation labels were separately checked.

**Corrections committed:** Removed two repeated `أحمد بن حنبل - مسند الإمام أحمد بن حنبل` source headers from `hadith-text` in blocks 17 and 18 of `3Hawdh.html`, retaining their proper ownership in source metadata (commit `8d91f689f13289d7eb8cae22a57c6bf97812de51`). Restored original heading parentheses and the number-to-narration hyphen separator in all 28 numbered blocks (commits `c046d2d50e0c0a1de273772e105ad0000f4e518a`, `2a67d3d468ae71e6abd9ca74f839d79b4668e625`, `7157dda3d8917c45b1325d760e2955db0fc8d459`). Restored the original top navigation labels (commits `d95fa380be1efe7dd77fbe2546dbb9ccdd6b443f`, `6dd84b9b3f881926c4be7454b0e9a49a13724512`, `a08879bfbbb5d6660135cdd3cd28d46c4d40e483`).

**Final aftercheck:** independently re-fetched all three original pages and the final committed GitHub `main` pages; reran the source-split/field/paragraph/text/navigation/reference/heading comparison: `8/8 PASS`, `3/3 PASS`, `20/20 PASS`, with **zero remaining failures**. The `3Hawdh` original page reports `21` narrations but contains `20` distinct bibliographic source sections; both original counter and source boundaries are preserved. FrontPage bibliographic label typo `ا لجزء` is handled as an obvious display artifact, while its volume and page values are preserved. These are decoded DOM text comparisons with documented HTML whitespace/display normalization, not a claim of raw HTML source-byte identity.


## Seerah — batch 14: independent live-original verification (2026-10-27)

Verified against the actual original `.htm` pages at `kingoflinks.net`, fetched with Python `urllib.request` (Mozilla User-Agent), decoded as `windows-1256`, and compared with the reconstructed repository HTML before committing.

- `Seerah/4JO.html` ↔ `Seerah/4JO.htm`: 30 original bibliographic sources; 30 corresponding `hadith-block` elements, in source order.
- `Seerah/5Hwalt.html` ↔ `Seerah/5Hwalt.htm`: 24 original bibliographic sources; 24 corresponding `hadith-block` elements. Two original source boundaries occur without a standard two-blank-paragraph separator and were explicitly split at their distinct source headers (paragraph indexes 69 and 91, zero based).
- `Seerah/6Inhraf.html` ↔ `Seerah/6Inhraf.htm`: 10 original bibliographic sources; 10 corresponding `hadith-block` elements.

Full source-by-source comparisons were repeated after correcting the original-derived field ownership. Each source's complete narration/editorial paragraphs was compared as exact Unicode text after normalising HTML whitespace only; each source's full author/book/chapter header was reconstructed in the correct structural fields and checked against the original header; each volume and page value was checked individually; all blocks were checked in original order. The final independent check reported `4JO: 30/30 PASS`, `5Hwalt: 24/24 PASS`, `6Inhraf: 10/10 PASS`, with zero remaining paragraph, header, or reference mismatches.

The original page headings, narration counters, and visible original homepage navigation label have also been restored. Standard site design and existing CSS linkage are preserved. This is Unicode/DOM-level original-text verification, not raw HTML byte equality, since the original FrontPage markup is intentionally not reproduced.

Changes include correcting missing/truncated book titles, restoring source attribution and chapter ownership, restoring numbered narrations and missing narration passages, and preserving editorial text. Batch 14 was not permitted to advance until all three pages passed.



## Seerah — batch 15: original-source verification (2026-10-27)

- `Seerah/7LaYrown.html`: 11/11 independently identified original bibliographic source sections, in order; verified exact normalized Unicode paragraph text, full combined source headers, volume/page values, and source-field ownership. Two original source sections share a group that cannot be separated by two blank paragraphs; their boundary was explicitly restored at original paragraph index 38. PASS.
- `Seerah/8Ayat.html`: original is a Qur'an verse listing, not a hadith-block page. Replaced a near-empty local placeholder with all **148** nonempty original text paragraphs after the original four opening title/navigation/count paragraphs. Each paragraph's complete normalized Arabic text was compared, in its original order, against the reconstructed `quran-verse` paragraphs: 148/148 exact normalized-text matches. Preserved the original displayed verse count `عدد الآيات : ( 136 )` instead of changing it to the paragraph count; preserved the original page heading and top navigation labels. No independent hadith blocks are expected on this page.
- `Seerah/9Hodhyfa.html`: 10/10 original bibliographic source sections, each checked for full paragraph text, metadata/source division, reference volume/page, and source order. PASS.

All three corresponding `.htm` pages were freshly fetched from `kingoflinks.net` via Vercel Sandbox Python `urllib.request` with a Mozilla User-Agent and decoded correctly as `windows-1256`. The existing site CSS linkage and overall page-wrap/navigation styling are retained. Comparisons concern exact Unicode text after HTML-whitespace normalization rather than identical historical FrontPage source HTML bytes.


## Seerah — batch 16: original-source verification (2026-10-27)

The original `.htm` pages were freshly fetched directly from `kingoflinks.net` in a Vercel Sandbox with Python `urllib.request` and Mozilla User-Agent, then decoded as `windows-1256`. The corresponding `.html` pages were reconstructed without changing the site's existing `modern.css` dependency or general page layout.

- `Seerah/10Slook.html`: 13 distinct original bibliographic sources vs. 13 local `hadith-block` elements, original order and boundaries preserved. The original narration count is `14`, which is displayed unchanged and is not mistaken for a count of independently sourced blocks.
- `Seerah/11Ysalli.html`: 2/2 independently sourced blocks restored and checked.
- `Seerah/12Yalam.html`: 7/7 independently sourced blocks restored and checked.

For each of the 22 source blocks, all original narration/editorial paragraphs (including paragraph boundaries) were checked for exact equality of decoded Unicode text after HTML whitespace normalization; original complete source headers were checked against the concatenated structurally assigned `scholar-name`, `book-title`, and `chapter-info` fields; each volume and page value was checked against the `ref-value` fields; order and source boundaries matched. Hadith numbers were put in `hadith-number` without losing the original narration prefix, and the original headings and displayed counters were restored. Three missing scholar fields found by the final audit were corrected and independently rechecked. Final local results: `10Slook 13/13 PASS`, `11Ysalli 2/2 PASS`, `12Yalam 7/7 PASS`, with zero detected source text/header/reference mismatches.

These are comparisons of decoded DOM text with HTML whitespace normalization, not claims of identical historical FrontPage HTML bytes. Files are to be independently re-fetched from the committed `main` and matched against the verified working copies.


## Seerah — batch 17: live-original content, field ownership, and block verification (2026-10-27)

Original pages were freshly retrieved from `http://kingoflinks.net/Seerah/` through Vercel Sandbox Python `urllib.request` and decoded as `windows-1256`. Original source sections were identified by the bibliographic volume/page paragraphs and the original paragraph separators.

- `Seerah/13Ytboon.html` ↔ `13Ytboon.htm`: 4 original sources, 4 local `hadith-block` elements. Source fields and exact Arabic narration paragraphs reconstructed; author field of the fourth source (`ابن ماجه`) was restored on final review.
- `Seerah/14Yltqyan.html` ↔ `14Yltqyan.htm`: 2 original sources and 2 source blocks; preserved original Quran quotation and all reference data.
- `Seerah/15Sbab.html` ↔ `15Sbab.htm`: 2 original sources and 2 blocks; preserved original narration text and associated metadata.

Verification checks the complete original per-source decoded Arabic text in original order, paragraph boundaries, and combined scholarly source headers against `scholar-name`/`book-title`/`chapter-info`, and original page/volume numbers against `ref-value`, normalizing only HTML whitespace. The displayed original page headings and narration counts and the existing site `modern.css` linkage are retained. Original Microsoft FrontPage HTML source bytes are not claimed to be identical.


## Seerah — batch 18: original source, field, and block verification (2026-10-27)

All three current original `.htm` files were fetched directly from `http://kingoflinks.net/` using Vercel Sandbox Python `urllib.request` with a browser User-Agent and decoded as `windows-1256`. Corresponding `.html` files on GitHub `main` were corrected and independently re-fetched after committing. Comparisons check exact normalized Unicode paragraph content (normalizing only HTML whitespace, not changing wording or punctuation), the correct author/book/chapter/reference fields, and the source order/boundaries.

- `Seerah/16Shahadtain.html` ↔ `16Shahadtain.htm`: **2/2 original source blocks**. Both complete narrations exactly match original source text when the separately structured hadith numbers `392` and `67` are rejoined with ` - `. Restored original `حدثنا`, punctuation, references, original parenthesized title and narration count. Kept the documented unusual source spelling `م سند`. The first narration’s original chapter heading is in `chapter-info`, not `hadith-text`.
- `Seerah/17Mbayoon/1AbuAlGhadiah/1.html` ↔ `1.htm`: **25/25 distinct original bibliographic sources**, restoring the eight source blocks absent from the former 17-block local page. Original author/book/chapter lines, all references including `الهامش`, the original parenthesized page heading, the `( قاتل عمار )` internal heading, editorial markers, hadith-number fields, and 61 original source-text paragraphs are preserved in order. All 137 original nonempty paragraphs are accounted for across navigation, page heading/count, page-intro, source metadata, references and narration. Unusual original reference spacing `ا لجزء` is preserved.
- `Seerah/17Mbayoon/2AlBalawi/1.html` ↔ `1.htm`: **17/17 distinct original bibliographic sources**. The displayed original narration count is `22`, not the source block count. Original `1 - 2` section intro, page heading/counter, source metadata, reference numbers and 35 original source-text paragraphs are preserved. All 84 original nonempty paragraphs are accounted for.

A fresh independent post-commit source-by-source audit was run against the actual raw GitHub `main` HTML and the original freshly fetched `.htm` text. For all **44/44** blocks, the reconstructed author and book were checked against the original source header; chapter-info paragraphs and original in-header subdivisions were checked in original order; `ref-info` including volume, page ranges and marginal notes was checked for exact normalized text equality; and every `hadith-text` paragraph including individually structured numbers was checked for exact normalized Unicode equality with its original paragraph in the same source block. The original page headings, navigation, counters, standalone headings and original paragraph ordering were also checked. Results: **16Shahadtain 2/2 PASS; AbuAlGhadiah 25/25 PASS; AlBalawi 17/17 PASS**, with zero outstanding content/field/source-block mismatches in this audit. `modern.css` was not modified and the standard page wrappers remain.

Commits: `d2c6f787252e1930e169eb8a781b4f9b83149c1b` and `3843ce6344c3e6a27d199f77920f9301474c20ab` (Shahadtain); `63051411fe9af3ef0b284fdb8fbe466a0eae14cf` (AbuAlGhadiah); `c9882cbb04da3f7148313ab166e8dc3720229575` (AlBalawi); `2ddae2d06c2d7f12d22dfa15aab92e942f8174dd` (checklist 54/75).


## Seerah — batch 19: live-original Unicode, field ownership and block verification (2026-10-27)

Fetched each current original through Vercel Sandbox Python `urllib.request` directly from `http://kingoflinks.net/` and decoded as `windows-1256`. Original pages were mapped through `sitemap.xml`. A source reconstruction parsed the original `<p>` paragraphs and source boundaries using each bibliographic `الجزء / رقم الصفحة` line, treating consecutive blank original paragraphs as source delimiters. The complete original paragraph inventory was assigned to title, navigation, original count, intro, source fields, reference fields, and narration/editorial text, with no unassigned nonempty paragraphs. Structured hadith numbers preserve their original `N -` prefix on text rendering. Original unusual wording and punctuation were preserved, as were the shared site layout and `modern.css` link.

- `Seerah/17Mbayoon/2AlBalawi/2.html` ↔ `Seerah/17Mbayoon/2AlBalawi/2.htm`: **39/39 source blocks**; all 179 nonempty original paragraphs accounted for, including 75 narration/editorial paragraphs. The original displayed count `39` and structural intro `1 - 2` are retained.
- `Seerah/17Mbayoon/3AlJahJah/1.html` ↔ `Seerah/17Mbayoon/3AlJahJah/1.htm`: **2/2 source blocks**; all 14 original nonempty paragraphs accounted for, including four narration paragraphs. The original parenthesized heading and `1 - 2` intro no longer contaminate `scholar-name`.
- `Seerah/17Mbayoon/3AlJahJah/2.html` ↔ `Seerah/17Mbayoon/3AlJahJah/2.htm`: **13/13 source blocks**; all 67 original nonempty paragraphs accounted for, including 24 narration/editorial paragraphs. The original displayed count `20` is intentionally retained independently from the number of bibliographic sources.

**Independent post-commit audit**: Re-fetched the actual committed files from GitHub `main`. For each of all **54/54** source blocks, independently re-parsed the original source headers and compared the exact original author to `scholar-name`, the correct book title to `book-title`, all chapter segments to `chapter-info`, and the entire decoded reference paragraph (including its punctuation and numeric values) to `ref-info`; each original source's narration paragraphs were compared in original order and source ownership with rendered local `hadith-text`. Page headings, counters, and intro fields were checked as well. Every check passed with zero observed content, field ownership, or source block mismatches after normalizing only HTML whitespace. FrontPage source markup is not expected to match byte-for-byte.

HTML commits: `bca47998880763b36f57a5f309c5fcbe5343050b` (AlBalawi/2), `6e596dfbe1eb1173285495495f0b338fc48f4978` (AlJahJah/1), `58106ab02e4151cec1506d61bc9ac47011e7fb52` (AlJahJah/2). Checklist commit `7b51a49a4e453d615edc32c7cfb13aa37c975ba6`: **57/75** verified; next `Seerah/17Mbayoon/Main22.html`.


## Seerah — batch 20: original-source and menu verification (2026-10-27)

Source of truth: current original `kingoflinks.net` `.htm` pages matched with `sitemap.xml`, directly fetched using Vercel Sandbox Python `urllib.request` and correctly decoded as `windows-1256`. Complete meaningful Arabic text was preserved after normalizing only HTML whitespace in comparison; original source order, source metadata, reference strings, textual punctuation, numbers and editorial notes were checked. All three changed `.html` files were committed to GitHub `main` and independently fetched back for post-commit verification.

- `Seerah/17Mbayoon/Main22.html`: original menu page has **zero hadith blocks**, **three linked topics**, original link targets and labels, original explicit topic numbers **1, 3, 2** in the visual original table order, per-topic counters **25, 22, 61**, and total `عدد المصادر : ( 108 )`. Restored original heading `( هل رضي الله عن كل المبايعين تحت الشجرة ؟! )`, corrected navigation labels and preserved the shared menu-table styling. Post-commit independent comparison of all three menu targets, labels and counters PASS.
- `Seerah/18Yaref.html`: **8/8** separate original bibliographic source sections, all **32** nonempty original paragraphs accounted for in their appropriate page/source fields, including **9** complete narration/editorial paragraphs. The original title, displayed count, author and book attribution, chapter metadata, complete reference strings and hadith-number positions were reconstructed and independently rechecked from committed `main`. PASS.
- `Seerah/19Bsbsa.html`: **4/4** original source blocks, rather than three incomplete local blocks; all **22** nonempty original paragraphs accounted for, including **11** narration/editorial paragraphs. Original title, displayed narration count `6`, metadata, complete Arabic narration texts, hadith numbers and source boundaries were restored. Independent committed-`main` check PASS.

Both source pages underwent source-by-source field ownership checks: `scholar-name` equals the original author; `book-title` and `chapter-info` reconstitute the original full source header; `ref-info` equals the complete original reference paragraph; each structured `hadith-text` paragraph is exact Unicode text in its original source and order. Menu page verified separately, not treated as a hadith page. Original FrontPage markup is not expected to match byte-for-byte. No changes to `modern.css` were required.

HTML commits: `626cf47120d833476eb787f0ac4df452081524c2` (Main22), `71aa244d5aebd807ec8a1aa52c228871cdf0d5eb` (18Yaref), `7ba1bedecaefe12311d44bd76e97d6e1f6cdc11d` (19Bsbsa). Checklist commit: `6058294c7b35b953e249a0a380fc33fe8c026cf2`; **60/75** pages verified, next `Seerah/20Lho.html`.


## Seerah — batch 21: original source and paragraph verification (2026-10-28)

Fetched the current originals of `Seerah/20Lho.htm`, `Seerah/21Njoom.htm` and `Seerah/22Tarko.htm` directly via Vercel Sandbox Python `urllib.request` from `http://kingoflinks.net/`, based on `sitemap.xml`, and decoded as `windows-1256`. Complete decoded text, field ownership and per-source block boundaries were compared with reconstructed HTML files on GitHub `main`. Existing site layout, relative navigation and `modern.css` references were retained.

- `Seerah/20Lho.html`: **7/7** original source blocks; all **27** nonempty original paragraphs mapped and preserved, including **9** narration/editorial paragraphs. Original title, reported narration count `7`, book/chapter fields and references, including the `الحاشية` suffix, retained.
- `Seerah/21Njoom.html`: original page contains one separate opening source (the permanent committee's fatwa, including its question and answer) and **15** further bibliographic source sections. Former local page collapsed all of these into **one** block. Corrected to **16/16** original sources, preserving all **110** original nonempty paragraphs, including the fatwa's heading/question/answer and **58** narration/editorial paragraphs from the subsequent 15 sources. Original unusual words, titles, numerals, book metadata and exact reference strings retained, including volume/page ranges and source-specific subdivisions. Original display count `16` retained.
- `Seerah/22Tarko.html`: **2/2** original bibliographic sources; all **11** original nonempty paragraphs mapped and retained. Original heading, displayed count `2`, Quranic chapter headings and quotations, complete reference details and narration paragraphs retained.

**Independent aftercheck against actual committed `main` files:** Re-fetched all three files and verified exact normalized Unicode text and source order for **25/25** original source blocks; full original `scholar-name`, `book-title`, `chapter-info` and `ref-info` field attribution, body paragraph equality in every source, and page headings/narration counters. The opening nonstandard fatwa in `21Njoom` was separately verified with its own header, question and answer, rather than being misrepresented as a numeric `الجزء` source. Results: **7/7 PASS**, **16/16 PASS**, **2/2 PASS**. Whitespace normalization was limited to HTML rendering; no substantive content was omitted or rewritten.

HTML commits: `81c83fab0752e7998320a27bab362676447825a0` (20Lho), `56558a30c8a0f0aaa0dbc38688b4e9efd1c82b80` (21Njoom), `086ec2c4e94c74fc0893f06bc5a61ec2c12dbf41` (22Tarko). Checklist `846d42370f2e6a0955a2e9b2b1e86e27248866c2`: **63/75** pages verified; next `Seerah/23Tefatan.html`.


## Seerah — batch 22: live-original Unicode / source field / block audit (2026-10-28)

All three originals were identified through `sitemap.xml`, fetched from `http://kingoflinks.net/` using Vercel Sandbox Python `urllib.request` with normal browser User-Agent, and decoded as `windows-1256`. Source boundaries were reconstructed using original bibliographic reference paragraphs and the original paragraph separators, with chapter subdivisions and source-specific headings kept in correct source fields. The local `modern.css` linkage and standard layout were preserved.

- `Seerah/23Tefatan.html` ↔ `23Tefatan.htm`: **14/14 original source blocks**, all **69** nonempty original paragraphs accounted for. Original unusual heading `( الصحاب ة تتقاتل فيما بينها باليد والجريد والنعال )`, Quranic citations, source subdivisions, volume/page references, narration text and numbers retained.
- `Seerah/24Mkhnthon/1Heet.html` ↔ `1Heet.htm`: original **38/38** separate bibliographic sources restored from only 26 local blocks; all **203** nonempty original paragraphs preserved. Original `الصحابي : ( هيت )` and `مفهوم الصحابي` placed in page introductions, with source metadata and subsequent commentary in their correct block fields.
- `Seerah/24Mkhnthon/2Anjasha.html` ↔ `2Anjasha.htm`: **14/14** original source blocks restored from 13 local blocks, all **72** nonempty original paragraphs preserved. Original `الصحابي : ( أنجشة الأسود )` and `مفهوم الصحابي` remain separate page headings.

**Independent post-commit verification** fetched all three resulting HTML files from GitHub `main` after committing and re-parsed their source blocks. For each of the **66/66** original bibliographic sources, the decoded source author, book title, chapter subdivisions, complete reference text including original parenthesis spacing, and every narration/editorial paragraph were compared in exact original order. Page headings, original narration counters and page-intro fields were also verified. The first comparison used tag-to-space normalization, which falsely inserted spaces between adjacent inline reference spans on two references; a corrected tag-concatenating local comparison independently confirmed both references exactly matched the originals. All 66 source blocks passed; no outstanding content/field/block deviations were observed.

HTML commits: `e5502d77bf29b48da7d53749f97286cdd8d8c0a1` (23Tefatan), `b2555cf91111336e9754a377b60bf7f01a9ff9fe` (1Heet), `874f99df965bc038d25c8f0d8656be2d0948d1ff` (2Anjasha). Checklist: `418a68d6d2b82607a1cdcc8bab1a7bcd17cc13db` with Seerah **66/75**, next `Seerah/24Mkhnthon/3Mate.html`.


## Seerah — batch 23: original text, source ownership and block verification (2026-10-28)

Verified the three original `.htm` pages retrieved through `sitemap.xml` from `http://kingoflinks.net/` using Python `urllib.request` in Vercel Sandbox, decoded with `windows-1256`. Reconstructed the original source group boundaries at the original bibliographic reference paragraphs, including the unusual first reference spelling `ا لجزء`. All original nonempty paragraphs are assigned to original title, count, introductory headings, source headers, complete references, and narration text. Existing `modern.css` and standard page structure preserved.

- `Seerah/24Mkhnthon/3Mate.html`: **29/29** original source sections (formerly 20 local blocks), **132** original nonempty paragraphs. Original source heading `الصحابي : ( ماتع أو مانع أو ماثع )`, separate `مفهوم الصحابي`, entire chapter/ref subdivisions and textual paragraphs accounted for; original displayed narration count `28` retained separately from the number of sources.
- `Seerah/24Mkhnthon/4Hdem.html`: **9/9** original source blocks (formerly 8), all **45** nonempty original paragraphs preserved. Original `الصحابي : ( هدم أو هذم أو هرم )` and `مفهوم الصحابي` headings retained; full bibliographic source metadata preserved.
- `Seerah/24Mkhnthon/5Ana.html`: **8/8** original source blocks (formerly 7), all **43** nonempty original paragraphs preserved, including `الصحابي : ( أنه أو إنه )` and `مفهوم الصحابي`.

**Independent GitHub `main` aftercheck** re-fetched the actually committed HTML files, compared all **46/46** bibliographic source blocks to the corresponding original source sections and checked `scholar-name`, `book-title`, `chapter-info`, complete `ref-info` strings, and all source-owned `hadith-text` paragraphs in original order and exact decoded Unicode wording. Original page headings, displayed narration counters and pre-source headings were also matched. Every check PASS, with HTML whitespace normalized only for rendering. Original FrontPage markup is not required to match byte-for-byte.

HTML commits: `51ed8422edc0ee1f202372e78abedb95c84a19ef` (3Mate), `01587fe556d3bd800b137f54b30ccf03aaadefa1` (4Hdem), `d7d9fa3a60edfcfd9e9231bfbe26f353e908b3b2` (5Ana). Checklist `c9c9a1fd40126969c06f1c6f6920816a01160e06`: **69/75** complete, next `Seerah/24Mkhnthon/6Hnab.html`.


## Seerah — batch 24: original-source reconstruction and post-commit verification (2026-10-28)

Canonical originals resolved through `sitemap.xml` and fetched from `http://kingoflinks.net/Seerah/24Mkhnthon/` with Python `urllib.request` (ordinary browser User-Agent) in Vercel Sandbox, decoded as `windows-1256`. Original source headers and complete bibliographic reference paragraphs determine source boundaries. All original non-navigation paragraphs were mapped in source order, with original passage text, unusual spacing/spelling, source-specific numbers, note wording and `الحاشية` retained. The shared `../../modern.css` stylesheet and existing index navigation remain in use.

- `6Hnab.html`: **13 original bibliographic references / 13 `hadith-block` sources**, formerly 12. **58** original non-navigation paragraphs, including title and displayed count; **56/56** subsequent original text segments independently mapped and compared. Source-specific reference text including `ا لجزء` and `الحاشية : 1` retained.
- `7Twis.html`: **11/11 original bibliographic sources**, formerly 10 blocks. **51** original non-navigation paragraphs, **49/49** subsequent segments independently checked, including the Quranic text associated with the القرطبي source.
- `8Dlal.html`: **10 original bibliographic reference sections**, comprising **9 ordinary `hadith-block` sources plus 1 distinct footnote source** (ابن ابي الحديد). Former local markup had 8 `hadith-block` elements and a footnote area. **46** original non-navigation paragraphs, **44/44** subsequent text segments independently checked. The final `الهامش` section is not merged into an unrelated narration.

After HTML corrections, the committed versions were fetched independently from immutable GitHub commit-addressed raw URLs and each original non-navigation text segment after the title/count was matched to its unique `data-original-index` owner in the resulting HTML. Per-page results: `6Hnab` **0 mismatches / 56**, `7Twis` **0 / 49**, `8Dlal` **0 / 44** after whitespace rendering normalization only. Original standalone source headings and source reference boundaries are preserved. The first two original paragraphs are represented by the page title and displayed narration count rather than indexed source content. This is an original-text segment aftercheck, not merely a deployment comparison.

Final HTML commits: `6ea5a395b66d4157f1242c870ce6989075b18361` (6Hnab), `570c310f2af06bd3a4789f086f79e464b988a794` (7Twis), `dfebe3d04c150a81b71cfe8f3f3d8aa1fc7cfa72` (8Dlal).


## Seerah — batch 25: final 3 pages (2026-10-28)

Originals located in current sitemap: `Seerah/24Mkhnthon/9Other.htm`, `Seerah/24Mkhnthon/Main114.htm`, `Seerah/Main131.htm`. Fetched original HTTP content in Vercel Sandbox with browser User-Agent and decoded `windows-1256`. Retained shared `modern.css` and the existing standard 3-column menu structure.

- `9Other.html`: reconstructed **6/6** original bibliographic source sections from **5** prior local `hadith-block` elements. Original **28** non-navigation paragraph segments; 2 are title/count, and **26/26** remaining segments exactly mapped by `data-original-index` to the final committed HTML, whitespace rendering normalized, **zero unmatched segments**. `مفهوم الصحابي` is a page introduction, not an author. Editorial notes and narration numbering remain source-specific.
- `24Mkhnthon/Main114.html`: reconstructed **9** distinct original topic entries, instead of treating the split `3Mate.htm` anchor as two topics. Labels, order, counts and relative destinations individually transcribed from original menu; counts **38, 14, 28, 10, 8, 13, 11, 10, 6** total **138**. Original title and source total restored. Both return links use local HTML equivalents.
- `Main131.html`: reconstructed **24** original topics with original counts and ordering, sum **620**. Preserved original source-specific labels and the original unusual split spelling `ا لمخنثون`. The original section-link count is **137** while its subindex `Main114.htm` displays **138**; this original-source inconsistency is intentionally preserved rather than silently harmonized. Duplicate original anchors within a topic (the `11Ysalli` label, `Main114` split anchor) are represented by one full clickable topic link in the standardized menu.

Independent aftercheck fetched immutable GitHub commit files and the original 9Other text anew: **26/26** source-text segments exactly matched. Menu aftercheck verified 9 and 24 rows, the original total counts (138 and 620), internal link paths and the intentional splitting of historical HTML anchors. No new stylesheet was added.

HTML commits: `bbd2ee2dcb6664558f58728cf0a6e785fbaa3c22` (9Other), `14c4aca358259b2836d0f2a07824362eadef6d13` (Main114), `995fe75aa092de0a69cb39e25d320ff84fd87c09` (Main131).


## Tjseem — batch 1: OPEN, partial corrections only (2026-10-29)

Checklist selection after Seerah 75/75: `Tjseem/1ShabAmrad.html`, `Tjseem/2Atraf.html`, `Tjseem/3Hyah.html`. Original URLs are the matching `.htm` paths in project sitemap; original pages were fetched via HTTP from `kingoflinks.net` with a browser User-Agent and decoded using `windows-1256`. Current originals show narration totals 37, 37, and 26 respectively; **these narration totals are not independently established source-block counts**.

Original reference paragraphs containing `الجزء`: 33, 32, and 18. Local `hadith-block` counts: 37, 33, and 19. These differences must be resolved from actual source boundaries, not inferred from count totals. Preliminary exact-string checks after whitespace normalisation found unexplained mismatches in all three pages, and therefore **no page passes the three-level original-text verification gate**.

Documented partial HTML changes:
- `1ShabAmrad.html`: correctly separates Ibn Taymiyya's scholar name and `بيان تلبيس الجهمية في تأسيس بدعهم الكلامية`; moves `289 / 290` out of falsely assigned page number and retains it as an original hadith reference, preserves brackets around editorial extraction note; corrects metadata in following al-Haythami block. Commit `9f2324eeb5181ac5f67e29addbb8e2593d3a1b9e`.
- `2Atraf.html`: removes the page topic from the first block's `scholar-name`, correctly identifies al-Bukhari; corrects scholar/book/chapter ownership for the subsequent report and adds its number 4849. Commit `5211fefd5615dfb76f38018f3ae3b101d235daf5`.
- `3Hyah.html`: replaces first block's invalid scholar `>` and topic-as-book with al-Bukhari and `صحيح البخاري`; restores full opening narration as independently retrieved original paragraph and identifies hadith 6227. Commit `84be1bcfd7ea65974fa95e00b2945c073ce6a7a5`.

All three committed HTML files were re-fetched from GitHub `main` after updates and their corrected opening fields and unchanged local block counts were inspected. **This limited post-commit inspection is not a full character-by-character verification of all source segments.** The remaining local text, Quran details, source boundaries, hadith-number duplication and all per-block ownership must be independently verified and corrected. Do not mark these three pages `[x]` in `tjek.md`, and do not begin batch 2 until all three pass the full final committed-original comparison.


### Tjseem batch 1 — continued source comparison and number ownership cleanup (2026-10-29)

Re-fetched all three original `.htm` pages over HTTP with ordinary User-Agent in a fresh Vercel Sandbox, decoded as `cp1256`, and compared to fresh GitHub `main` HTML. The original paragraph checks still reported 17 longer original segments not matched as contiguous normalized local text in `1ShabAmrad`, 34 in `2Atraf`, and unresolved discrepancies in `3Hyah`. These figures are **triage**, not independently confirmed missing-source counts: cross-field splits and text alterations remain to be investigated.

Removed only exact duplicate numeric prefixes when an existing `hadith-number` immediately preceded a `hadith-text` paragraph beginning with the same number followed by a hyphen. This removes a duplicate displayed identifier without changing the remainder of the paragraph:
- `Tjseem/1ShabAmrad.html`: 16 redundant prefixes; HTML commit `f714e33e33c46699089988864d2e8a902bdd3f13`.
- `Tjseem/2Atraf.html`: 3 redundant prefixes; HTML commit `d59e78221271a71610bab9193813a35f56e5629b`.
- `Tjseem/3Hyah.html`: 11 redundant prefixes; HTML commit `c7144138c63a306ba618c33bf497a2d9d4bf7ec4`.

Post-commit GitHub `main` re-fetch verified **zero remaining instances of this precise duplicate-prefix pattern** and unchanged local block counts of 37 / 33 / 19. This check is narrow and **does not validate original-to-final content or source boundaries**. Batch 1 remains OPEN, with `tjek.md` unchanged and no authorisation to advance to batch 2.


### Tjseem batch 1 — further original-based book/chapter correction (2026-10-29)

Re-fetched original `Tjseem/3Hyah.htm` via Vercel Sandbox, decoded `cp1256`, and inspected the original al-Bukhari source headers alongside the latest `main` HTML. Corrected the misallocated `book-title` / `chapter-info` for the group of Bukhari reports containing the citation `{ وُجُوهٌ يَوْمَئِذٍ نَّاضِرَةٌ @ إِلَى رَبِّهَا نَاظِرَةٌ ( القيامة : 225 - 23 ) }`. **Preserved the original unusual `225` value** instead of silently changing it. HTML commit: `e4733db52c7439621ded61cdf2497ace62227d79`. Re-read resulting `main` file, confirming the changed fields. Other source metadata and narration text remain unverified. Batch 1 is still OPEN; no checklist ticks or advancement to batch 2.


### Tjseem batch 1 — original narration chain restoration in 2Atraf (2026-10-29)

Retrieved the original `Tjseem/2Atraf.htm` anew via HTTP / `cp1256` in Vercel Sandbox. Restored the full original opening transmission chains in hadiths `4849`, `4850`, and `4919`, from original narrative paragraphs, without replacing their subsequent local continuation paragraphs. Original chain restoration: HTML commit `f2e3619672049f46473981818b1506b4aa8b8555`; continuation for `4849` reinserted after noticing its loss during the narrow re-read: follow-up HTML commit `80a95bb4b8b0fd2498c1e7bbad01431ace9ddbbf`. Latest committed HTML was re-fetched from GitHub `main`; all three restored chains and the relevant continuations are present; local block count remains 33. **Neither those retained continuations nor all other source paragraphs have passed independent character-by-character comparison.** Batch 1 remains OPEN: do not check off pages or advance to batch 2.


### Tjseem batch 1 — continued correction of 3Hyah (2026-10-29)

Fetched original `Tjseem/3Hyah.htm` directly over HTTP with browser User-Agent in Vercel Sandbox and decoded `windows-1256`. Original paragraph text for Bukhari narrations 7434 and 7435 used to restore complete chains and wording in the corresponding two local blocks, preserving the separate `hadith-number` field. HTML commit `10fe88c786732523083894cca62befc3769c6fd9`. Latest GitHub `main` HTML re-read: both restored chains present, 19 local blocks unchanged. **Still not a full independent character-by-character aftercheck for this page or the three-page batch.** Do not mark checklist `[x]` and do not advance to batch 2.


### Tjseem batch 1 — further original narration restoration (2026-10-29)

Fetched `Tjseem/3Hyah.htm` directly over HTTP and decoded `windows-1256`. Reconstructed al-Bukhari report 7437 from the original page's original note and two consecutive narration paragraphs: retained the complete `[ النص طويل لذا استقطع منه موضع الشاهد ]` extraction note, restored full narration/continuation, assigned 7437 once to `hadith-number`, retained original bibliographic info and the separate source-block boundary. HTML commit `8ca90aebab55f5aacda0f84612421e7592b5d66e`; independent GitHub `main` re-fetch confirmed its new note/number and 19 local blocks. **No full page or batch source-to-commit verification has passed.** Tjseem batch 1 remains OPEN; `tjek.md` unchanged.


### Tjseem batch 1 — 1ShabAmrad original narrations 286, 287, 127 (2026-10-29)

Re-fetched `Tjseem/1ShabAmrad.htm` using Vercel Sandbox HTTP and browser User-Agent, decoded `windows-1256`. Replaced three truncated or altered opening hadith paragraphs using original source paragraph indices 24, 28, 31 for reports 286, 287, 127, keeping their existing separate block boundaries and numbers. Committed HTML as `ad56f5b86813c948993001a756f93cb10ebb0e97`; re-fetched GitHub `main` and verified the three report fields and chain text remain present, and local block count is 37. This narrow change is not a complete independent source-text verification. **Batch 1 remains OPEN, checklist unchanged, batch 2 prohibited until final full verification.**


### Tjseem batch 1 — 1ShabAmrad original quotation restoration and concurrent edit guard (2026-10-29)

The canonical original `Tjseem/1ShabAmrad.htm` was fetched again over HTTP and decoded `windows-1256`. The complete original paragraph beginning `- .... وفي هذا الخبر من رواية ابن أبي داود` (including its Quranic punctuation and bracing) was restored into the first Ibn Taymiyya source block. HTML commit `c63d9b1dbdb290d6def00f97bee5ef4e433f51cb`; independent post-commit GitHub read confirmed the opening, braces and the existing count of 37 local blocks. A broader attempted repair was **not** committed because the GitHub branch head moved between read and update (409 conflict). The newer version was re-read before applying this narrow source-backed update, so no intervening changes were overwritten. **Full three-page original-to-committed content, field and block-boundary verification still pending.** Keep the batch open and checklist unchanged.


### Tjseem batch 1 — Ibn Qutayba original paragraph correction (2026-10-29)

Fetched canonical `Tjseem/1ShabAmrad.htm` over HTTP using Vercel Sandbox and decoded as `windows-1256`. Restored the complete original paragraph beginning `- .... قالوا : ومما يدل على ذلك أيضا حديث` into the Ibn Qutayba / `تأويل مختلف الحديث` block, and restored the original brackets around `[ النص طويل لذا استقطع منه موضع الشاهد ]`. HTML commit `8ac32c69a370ad6c65b7a5ba8b16c4fa72a27099`. Re-fetched committed GitHub main HTML confirming the target text/note and 37 local blocks. This is a narrow verified correction, **not** full page character-level verification. All three pages in batch 1 remain unchecked pending complete content, field and source-boundary aftercheck; batch 2 must not start.


### Tjseem batch 1 — Haythami pair correction (2026-10-29)

Re-fetched the original `Tjseem/1ShabAmrad.htm` via Vercel Sandbox (windows-1256). Restored source narrations 11738 and 11745 in their respective al-Haythami blocks, corrected the second block book title `معجم الزوائد`, changed the mislabelled page `179` to hadith reference `179`, and separated report number 11745 into `hadith-number`. HTML commits: `4466ae742402b2cbca699aca45075f9029224fac`, `1ca2a7a50ca8b361cf98568de3da082d7e6f50cf`. Re-fetched the latest GitHub `main` HTML and verified both reports, second book title and unchanged 37 local blocks. **Full original-to-commit content, field and block structure verification remains incomplete.** Keep batch 1 open; do not check off in `tjek.md` or proceed to batch 2.


### Tjseem batch 1 — critical correction to Haythami field mapping (2026-10-29)

A post-commit check detected that a preceding incremental edit had accidentally placed report 11738 inside the Ibn Taymiyya block and duplicated narration numbers in the next two blocks. **Do not rely on the earlier audit statement for commit `4466ae74` as a final verification.** Re-fetched original `1ShabAmrad.htm` and rebuilt the three original opening text segments in their correct separate blocks: Ibn Taymiyya quote at original paragraph 8, al-Haythami 11738 at paragraph 11, and al-Haythami 11745 at paragraph 14. Restored the original editorial note in the first block and exactly one report identifier in each corresponding block. Final corrective HTML commit `cd74f6d792436e6e797789d26b4333246a4f58d9`; re-read `main` and checked the three specific source-text placements and 37 local blocks. Other page content has NOT undergone the required independent full original comparison. Batch 1 remains OPEN and `tjek.md` must stay unchanged.


### Tjseem batch 1 — Abu Yala metadata correction (2026-10-29)

Compared original `Tjseem/1ShabAmrad.htm` (windows-1256) source header `أبو يعلى ابن الفراء - ابطال التأويلات لأخبار الصفات - فصل ثان يتعلق بليلة الإسراء` with the reconstructed local entry, and corrected the wrongly assigned book title `طبقات الحنابلة` to original `ابطال التأويلات لأخبار الصفات`, retaining `فصل ثان يتعلق بليلة الإسراء` as chapter-info. Also restored original brackets for its source extraction note. Committed HTML `146caf4944c7cf304ca8e90f4122a72e5b39b195`, independently re-fetched `main` and confirmed metadata and 37 local source blocks. This is **not** complete text, ownership, and source-block verification for batch 1. Do not update `tjek.md` or move to batch 2.


### Tjseem batch 1 — three additional field/note corrections (2026-10-30)

Retrieved original `Tjseem/1ShabAmrad.htm` over HTTP in Vercel Sandbox and decoded `windows-1256`. Original source heading for Ibn al-Jawzi is `ابن الجوزي - العلل المتناهية في الأحاديث الواهية - كتاب التوحيد - باب في ذكر الصورة`. Corrected local block's misleading `صفة الصفوة` book title to `العلل المتناهية في الأحاديث الواهية`, with remaining chapter info in `chapter-info`. Restored original square brackets around editorial extraction notes for the two preceding Abu Yala sources. HTML commit `19a1204af5b36f1341884c7b0f58955a6fe4b438`; GitHub main re-fetch confirms exact corrected book label, both brackets and unchanged 37 local blocks. **Complete original passage, source boundary and field ownership review remains outstanding for all three batch-1 pages.** Checklist remains unchanged; batch 2 not authorised.


## Tjseem — batch 1: FINAL VERIFIED AND CLOSED (2026-10-30)

**Scope:** `Tjseem/1ShabAmrad.html`, `Tjseem/2Atraf.html`, `Tjseem/3Hyah.html`. All three corresponding original `.htm` URLs were verified in the current repository `sitemap.xml`. Originals fetched anew from `http://kingoflinks.net/` using browser User-Agent and decoded `windows-1256` (`cp1256`). The entire local HTML for all three pages was rebuilt from original source sections, including meaningful original text in legacy HTML nodes *outside* `<p>` tags. This final audit **supersedes all preceding provisional/open/incomplete notes for Tjseem batch 1**.

**Immutable post-commit original-source afterchecks:**

| Page | Original source groups vs. local hadith-blocks | Original reference fields checked | Meaningful original narrative segments checked | Discrepancies | Final HTML commit |
|---|---|---|---|---|---|
| `1ShabAmrad.html` | 37 / 37 | 37 / 37 | 75 / 75 | 0 | `3e866be2e7b9d95655101469ef75cb43aa7e9aa5` |
| `2Atraf.html` | 33 / 33 | 33 / 33 | 65 / 65 | 0 | `a353e0daa03fe5874a1bd755877b93af4b748e22` |
| `3Hyah.html` | 19 / 19 | 19 / 19 | 37 / 37 | 0 | `d278ff5e893b0ae0bc9d2c6f82a08cf66be52b12` |
| **Total** | **89 / 89** | **89 / 89** | **177 / 177** | **0** | |

After rebuilding, the original `.htm` was fetched again and compared to immutable GitHub HTML commits. Checks verified independent original source ordering through `data-original-source-start`, each `ref-info`, each original narrative segment including extra-paragraph legacy text in the corresponding `hadith-text` and `hadith-number`, and original editorial notes. Comparisons ignored only rendering-neutral whitespace/legacy directional characters. **No source content was invented or deliberately modernised.** Unusual original book spelling, punctuation, number ranges, `@`, `{ }`, original Quran citations (including the unusual `القيامة : 225 - 23`) and original reference wording were preserved.

**Independent field-ownership check:** All 89 original source heading/metadata groupings were compared token-by-token for Arabic words and numerals against local `scholar-name`, `book-title`, and `chapter-info`; **0 missing source metadata tokens**. Each of 89 blocks has exactly one `scholar-name`, `book-title`, `ref-info`, and `hadith-text`; HTML block counts **37 + 33 + 19 = 89** unchanged from documented original-source segmentation, with no mergers or splits. The printed original *narration counts* of 37, 37, and 26 are distinct from counts of bibliographic source sections (37, 33, 19); this distinction was preserved rather than fabricating blocks.

**Page/title checks:** The original topic headings and navigation text were restored on all three pages. The original Ibn Taymiyya introductory line `ابن تيمية يقر برواية الشاب الأمرد ويصححه` is explicitly preserved in the separate `page-intro` on `1ShabAmrad.html`. All pages retain the existing `../modern.css` link and site-wide styling. Each rebuilt source carries its original paragraph indices to enable future database migration and audits.

**Final GitHub main structural re-read:** Verified the full 37, 33, 19 counts respectively for `hadith-block`, `scholar-name`, `book-title`, `ref-info`, `hadith-text` and `data-original-source-start`, and verified each of three originals exists in the current sitemap. No errors.

**Decision: ALL THREE PAGES VERIFIED, batch 1 CLOSED.** The first three Tjseem checkboxes in `tjek.md` are authorised to be marked `[x]`; Tjseem status becomes **3/23**, leaving **20** pages. Next batch starts `Tjseem/4Yad.html` only in a subsequent explicitly continued batch, not as part of batch 1.


## Tjseem — batch 2: FINAL VERIFIED AND CLOSED (2026-10-30)

**Scope:** `Tjseem/4Yad.html`, `Tjseem/5Yora.html`, `Tjseem/6Ain.html`. The matching original `.htm` pages were fetched directly over HTTP from `kingoflinks.net`, identified from the current `sitemap.xml`, and decoded as `windows-1256` (`cp1256`). Every original source block was reconstructed from meaningful original HTML text, including text outside `<p>` elements and original bibliographic metadata. The final immutable GitHub commits were **independently re-fetched** and compared to newly fetched originals.

| Page | Original bibliographic sources / local hadith-blocks | Reference fields checked | Original meaningful content segments checked | Original/committed text and metadata discrepancies | Final HTML commit |
|---|---:|---:|---:|---:|---|
| `4Yad.html` | 29 / 29 | 29 / 29 | 57 / 57 | 0 | `d3453bbbdc4bf3eed8f0a68e5f819ec8f7ff0cf0` |
| `5Yora.html` | 15 / 15 | 15 / 15 | 52 / 52 | 0 | `2247be9fb7754d1d9f5c22e89de20072edc8c469` |
| `6Ain.html` | 6 / 6 | 6 / 6 | 7 / 7 | 0 | `22c2039b7c2ff03d26f82b230df4f976ee25afcb` |
| **TOTAL** | **50 / 50** | **50 / 50** | **116 / 116** | **0** | |

The source-block boundaries were checked using immutable `data-original-source-start` attributes against original document source indices. All source-specific reference text is preserved in its matching `ref-info` field, including original numeric formatting and page intervals. Each original source's meaningful content concatenation was checked directly against the corresponding committed `hadith-text`, including `hadith-number` content. Arabic metadata and original numerals from every source heading were independently checked against the corresponding `scholar-name`, `book-title`, and `chapter-info` fields. **No missing original metadata tokens.** Original source order and separate source-block boundaries were preserved, with no mergers or splits. Only rendering-neutral whitespace and legacy bidi marks were normalized during comparisons.

The original page topics and navigation spacing were restored. Original hadith text, Quran text, references, notes, symbols, `@`, braces, source grouping, and unusual spellings or figures were preserved without speculative corrections. Standalone original report identifiers `104`, `1130`, `1131`, and `1162` through `1170` in `4Yad.html` were explicitly assigned to `hadith-number`, without changing their narration text. All three pages retain the site's existing `../modern.css` design. All **50** source sections contain their own scholar, book, bibliographic reference and narrative fields.

**Decision: all three pages verified, Tjseem batch 2 CLOSED.** Update `tjek.md` to **6/23** and mark only the three batch-2 pages `[x]`. **17** Tjseem pages remain. Next batch begins with `Tjseem/7Arsh/1Ateet.html`, but it was not started during batch 2.


## Tjseem — batch 3: FINAL VERIFIED AND CLOSED (2026-10-30)

**Scope:** `Tjseem/7Arsh/1Ateet.html`, `Tjseem/7Arsh/2Hamalah.html`, `Tjseem/7Arsh/3Maa.html`. All matching original `.htm` URLs were confirmed in the current `sitemap.xml`. Originals were re-fetched via Vercel Sandbox directly from `http://kingoflinks.net/` and decoded as `windows-1256` (`cp1256`). Source headings, references, hadith content, notes and meaningful legacy text outside `<p>` were assigned to the correct source sections in original order.

**Important structural repairs:** `1Ateet.html` originally had only **2 local** `hadith-block` elements despite **23** distinct original bibliographic sources; all 23 were restored. `2Hamalah.html` originally had **17 local** blocks against **18** original sources; 18 restored. `3Maa.html` originally had **3 local** blocks against **7** original sources; all 7 restored. This count distinction reflects **source blocks**, not page-level printed counts of narrations. No original sources were merged or divided. Original unusual bibliographic spellings (including `القرآنسورة`) and source-number wording were retained.

| Page | Original sources / committed local blocks | Source ref fields checked | Meaningful original text segments checked | Post-commit original comparison discrepancies | Final HTML commit |
|---|---:|---:|---:|---:|---|
| `7Arsh/1Ateet.html` | 23 / 23 | 23 / 23 | 33 / 33 | 0 | `d9e483fd888ca88ac18080fe6d184450008eecb2` |
| `7Arsh/2Hamalah.html` | 18 / 18 | 18 / 18 | 20 / 20 | 0 | `6faca1acc87600f332bfb8beddfdd81c766e0f43` |
| `7Arsh/3Maa.html` | 7 / 7 | 7 / 7 | 11 / 11 | 0 | `3a9586950d2a25c8c207565461e28c2e0bb438fa` |
| **TOTAL** | **48 / 48** | **48 / 48** | **64 / 64** | **0** | |

**Independent immutable-commit original aftercheck:** Each source's original source-order index was checked against its `data-original-source-start`, all reference text compared against `ref-info`, all source-specific original meaningful text compared with the matching `hadith-text` including `hadith-number`, and original source-heading Arabic words and numerals independently compared with the `scholar-name`, `book-title`, and `chapter-info` fields. All three page topics were also checked against the original headings. Result: **0 textual omissions, reference mismatches, or missing metadata tokens** in those checks. Differences in whitespace and legacy bidirectional marks alone were normalized. Existing page layout and `../../modern.css` were preserved.

**Final GitHub main structural check:** Re-fetched each committed file; `hadith-block`, `scholar-name`, `book-title`, `ref-info`, `hadith-text` and original-source marker counts all match at **23**, **18** and **7** respectively. The source pages all appear in the current project sitemap.

**Decision:** Tjseem batch 3 **CLOSED**, three pages authorised for `[x]` in `tjek.md`, bringing the section to **9/23** pages verified, with **14 remaining**. Next batch begins at `Tjseem/7Arsh/4Arsh.html`; it has NOT been started here.


## Tjseem — batch 4: VERIFIED AND CLOSED (2026-10-30)

**Scope:** `Tjseem/7Arsh/4Arsh.html`, `Tjseem/7Arsh/5Shams.html`, and the index `Tjseem/7Arsh/Main94.html`. Confirmed all original corresponding `.htm` URLs exist in repository `sitemap.xml`, fetched the original pages directly from `http://kingoflinks.net/`, and decoded originals using `windows-1256`. Matched source content with committed immutable GitHub HTML, not merely earlier audits or local text. Original FrontPage layout artefacts were normalized without rewriting original meaningful text, and site-wide `../../modern.css` preserved.

**4Arsh:** Replaced one merged local `hadith-block` with **5 distinct original source blocks**, matching original order and `data-original-source-start` indices `4, 8, 11, 14, 17`. All **5 source references and 5 original meaningful hadith/quote segments** verified against immutable HTML commit `0181180b496c3161255f5593e04b6c2e3f6c3903`; no mismatches. Checked original headings, Arabic tokens and source numeral ownership against `scholar-name`, `book-title`, `chapter-info`; **0 missing source-heading tokens**. Original topic heading restored.

**5Shams:** Replaced one merged local block with **5 original source blocks**, source indices `4, 7, 11, 15, 18`, each with its own original `ref-info` and full narrative. All **5 source references and 5 original meaningful narration segments** independently matched with immutable HTML commit `6e22179bd1acd95f4a6573fe50a5b09f20182c12`; no mismatches. Original Quran quotation, chapter ownership, Arabic heading tokens and original topic heading checked; **0 missing metadata tokens**.

**Main94 index:** Compared the original `Main94.htm` (table with **5** source links) to immutable GitHub commit `27639f4f1074aa271ce11bdde2603057a7765419`. Original title and heading: `( روايات تدعي بأن لله عزوجل عرش ذو أطيط والعياذ بالله )`; original total `عدد المصادر : ( 59 )`. Verified all five topic labels, original individual source counts **23, 19, 7, 5, 5** and matching `.html` links for original `.htm` destinations, with **zero deviations**. Corrected both back-navigation labels and preserved valid reconstructed destinations `../../index-2.html` and `../Main133.html`. The page is an **index**, with 5 `menu-table` rows, **not** 5 hadith blocks.

**Final GitHub main reread:** Found exactly **5, 5, and 0** hadith blocks respectively, with matching scholar/book/ref/text fields on the two source pages, 5 menu rows on index, `../../modern.css` on all three, and sitemap membership confirmed. Original-source-block counts, text ownership and link/count associations pass. Only formatting-neutral whitespace and legacy bidi markers were normalized in comparisons.

**Decision:** Tjseem batch 4 **CLOSED**, authorize `[x]` for all three pages in `tjek.md`. Tjseem total after marking: **12/23** verified, **11 remaining**. Batch 5 begins at the next unchecked page `Tjseem/8Dar.html` and was not started in this batch.
