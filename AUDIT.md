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
