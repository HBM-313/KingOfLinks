# KingOfLinks — Audit Report & Project State

> **!!! CRITICAL !!!**
> ALL content MUST come from LIVE PAGES. Never assume. Always ask if confused.
> Any `.py` file created must be deleted once done using it.

---

## 1. Project Status Summary

- **Total pages**: ~1,994 HTML files
- **Completed folders**: 5 (with subfolders)
- **Remaining folders**: 18
- **Branch**: `Verdentai` (base: `main`)

---

## 2. Completed Folders (Content-Verified Against Live)

- [x] **Abawalnabi** — 13 files
- [x] **Abdulmtalib** — 11 files
- [x] **Abutalib** — 9 files
- [x] **AhlAlBait** — ~203 files
  - [x] 1Ttheer, 2Moadah, 3Mbahala, 6Thqlain, 7SafinatNooh, 9Khleefa, 10Hrbhom
- [x] **Aqydatona** — ~174 files
  - [x] 4Sjood, 8ZQ, 9Tbarrok, 10Twassol, 12Mutaah, 15Bkaa, 17Laen, 18Khoms

---

## 3. Remaining Folders

| Folder | Subfolders |
|--------|-----------|
| Bahth | — |
| Bhooth | 5Klbani |
| Daeefa | 15 |
| Fatima | — |
| Hywan | — |
| ImamAli | 1AlAyat, 2Mwlah, 3Malhaq, 4MalQran, 5Siddiq, 6Islamoh, 8Yjri, 9Haroon, 10Altaaer, 11RadShams, 12Mwqefoh, 15NafsNabi, 16Braah, 17Ahab, 18Syed, 21AliMnny, 25Wasi, 29Mwakhat, 30ElmAli, 31Azaa, 32HobAli, 33SabAli, 36Monajatoh, 40MA, 46BabAli, 47ShjatAli, 48HDN |
| ImamHasan | 5Syed, 10Estshhadoh |
| ImamHussain | 4Syed, 9Estshhadoh, 10NawhelJen, 11Kramat |
| ImamMahdi | 3Mna |
| Mkhalfoon | 1Abubaker, 2Omar, 3Othman, 4Aysha, 5Hfsa, 6Talha, 7AlZobair, 8Muawyah, 9AlAas, 10Khalid, 11Mogeerah, 12Abohraira, 13Braidah, 14Yzeed, 15AlHakam, 16Ibnsaad, 17Smarah, 18Ikramah, 19Qdamah, 20Rwished, 21Jahsh, 22maez, 23Sarh, 24Waleed, 25Mhjan, 26BniOmayaa, 27Hind, 28AhlNajd, 29Alarbaa, 30Slool, 31Krkra, 32Hmar, 33Alnuaiman, 34AbdulRahman, 35Oqba, 36Rabeah, 37Obaidellah, 38AbaJandal, 39Dherar, 40AbaAlAzwar, 41Alqamah, 42MadiKareb, 43IbnOmar |
| NabiMohd | 29Moled |
| RAG | — |
| RS | — |
| Rdod | — |
| Seerah | 1Zahf, 17Mbayoon, 24Mkhnthon |
| SwR | 1Rzyah, 2Elaqah, 20Teen |
| Threef | — |
| Tjseem | 7Arsh |

---

## 4. Issue Code Registry

| Code | Meaning | Detection | Fix |
|------|---------|-----------|-----|
| BOOK_AS_SN | Book/collection name in scholar-name | `sn_text in BOOK_NAMES` | Move collection to book-title, set scholar from live page |
| SN_EQ_BT | Scholar-name equals book-title | `sn_text == bt_text` | Apply correct book from context/live (see Guide.md §10) |
| COMBINED_BT | "Scholar - Book" or "Book - Chapter" merged in book-title | `' -' in bt_text` | Split on first ` -`; left→scholar or book, right→book or chapter |
| HADITH_IN_CI | Hadith text inside chapter-info | `^-\s*\d+\s*-\s*.{10,}` in ci | Move text to hadith-text div |
| UNWRAPPED_EDITORIAL | Editorial text not wrapped in `<span class="editorial-note">` | `النص طويل` in `<p>` without span | Wrap in `<span class="editorial-note">` |
| FLOATING_NOTE | analysis-note div outside any hadith-block | Direct child of article-body | Move into preceding hadith-block (after hadith-text) |
| LOOSE_P | `<p>` tags floating in article-body | `<p>` direct child of article-body | Wrap in `<div class="page-intro">` or proper hadith-block |
| FOOTNOTES_SECTION | Footnotes section not converted | `div.footnotes-section` exists | Convert to hadith-block or page-intro; fetch live for data |
| MISSING_PAGE | ref-info missing الصفحة value | No `الصفحة` in ref-labels | Add from live page |
| EMPTY_SN | Empty scholar-name div | `sn_text == ''` | Set scholar from live page |
| NUMBER_IN_SN | Hadith number in scholar-name | `^\s*[\d]+\s*$` matches sn | Move number to hadith-number span; set scholar from live |
| EDITORIAL_IN_SN | Editorial note text in scholar-name | `النص طويل` in sn | Move editorial to hadith-text; restore scholar |
| NOTE_AS_SN | Non-Sunni source note in scholar-name | `هذا المصدر ليس` in sn | Move note to analysis-note; set real scholar from live |
| NESTED_SN_IN_BI | scholar-name div inside book-info | Structural check | Move scholar-name to proper position |
| BT_IN_HT | Book title stub in hadith-text | Detect `"Book -"` pattern in ht | Remove and verify book-title is correct |
| FRAG_ANALYSIS | Multiple analysis-note divs in one block | `count > 1` | Merge into one |
| DUP_SN | Multiple scholar-name divs in one block | `count > 1` | Remove duplicate |

---

## 5. Special Pages Registry

| Page | Type | Description |
|------|------|-------------|
| `Aqydatona/8ZQ/24ZQ.html` | Type 2 | 12 evidence blocks. SN = `( N )`, no book-info/ref-info. hadith-text + analysis-note (numbered source list with `<br>` separators). page-intro has editorial intro. |
| `Aqydatona/12Mutaah/11Albani.html` | Type 3 | Hadith-number-only convention. الصفحة holds hadith number, no الجزء. |
| `Aqydatona/17Laen/4.html` (block 22) | Type 4 | Has "هذا المصدر ليس من المصادر السنية فانتبه عزيزي القارئ" in analysis-note. Scholar = أحمد بن صديق المغربي (NOT the note text). |

> **If you encounter ANY page with a structure not matching Types 1-4, STOP AND ASK the user.**

---

## 6. Data Files

### `_live_cache/`
- Mirrors live site folder structure
- Files stored as raw bytes (windows-1256 encoded `.htm`)
- Read: `open(path, 'rb').read().decode('windows-1256', errors='replace')`

### `_url_map.json`
- JSON dict: `{"local/path.html": "live/path.htm", ...}`
- Used by `verify_content.py` to look up live paths

### `_audit_results.json`
- JSON array of verification results per file
- Fields: `local_path`, `live_url`, `status`, `issues`, `live_ref_count`, `local_block_count`

### `process.md`
- **Authoritative** folder progress tracker
- Checkbox format: `- [x] FolderName` for completed, `- [ ]` for pending
- Includes subfolder checklists

---

## 7. Verification Procedures

### Running `inspect_folder.py`
```powershell
python -X utf8 inspect_folder.py FolderName
```
- Recursively checks all `.html` in folder + subfolders
- Reports structural issues per file
- Target: `✅ ALL CLEAN`

### Running `verify_content.py`
```powershell
python -X utf8 verify_content.py FolderName
```
- Compares local blocks against live refs (juz/page pairs)
- SPECIAL_PAGES skip live ref comparison, use hadith-count instead
- Target: `✅ ALL CLEAN`

### Manual Per-Page Checklist
- [ ] Scholar name correct (personal name only)
- [ ] Book title correct (book title only)
- [ ] Chapter info correct (chapter/section only)
- [ ] Ref info complete (الجزء + الصفحة)
- [ ] Hadith text present and correct
- [ ] Hadith number correct when present
- [ ] Analysis-note inside hadith-block (after hadith-text)
- [ ] No skipped content
- [ ] No guessed mapping
- [ ] Matches live page exactly

### End-of-Folder Checklist
1. `inspect_folder.py` → ALL CLEAN
2. `verify_content.py` → ALL CLEAN
3. All pages compared against live 1-by-1
4. Commit with descriptive message
5. Delete `.py` scripts

---

## 8. Per-Folder Known Issues (Pre-Scan)

These were identified before content verification. Some may already be fixed in completed folders.

### Bhooth
- `10Kayfa.html`: b6 HADITH_IN_CI
- `11Laban.html`: UNWRAPPED_EDITORIAL, EDITORIAL_IN_SN, COMBINED_BT

### Daeefa
- `1.html`: b5 COMBINED_BT
- `10.html`: b2 HADITH_IN_CI
- `12-14.html`: various HADITH_IN_CI, COMBINED_BT, FOOTNOTES_SECTION

### Fatima
- `18Shiah.html`: many LOOSE_P (needs content rebuild)

### Hywan
- `10Hayyah.html`: b1-4 UNWRAPPED_EDITORIAL, b3 EDITORIAL_IN_SN
- `11Ghanam.html`: b2 COMBINED_BT, b2-7 UNWRAPPED_EDITORIAL
- `12Other.html`: b3 UNWRAPPED_EDITORIAL

### ImamAli
- `13Ybaye.html`: b1-2 BOOK_AS_SN, b3-10 UNWRAPPED_EDITORIAL
- `14Yrfodh.html`: LOOSE_P
- `18Syed/`: SN_EQ_BT, BOOK_AS_SN in multiple files

### ImamHasan
- `1Hob.html`: b20-23 COMBINED_BT
- `2Tdleel.html`: b7,9,10 HADITH_IN_CI
- `6Bnood.html`: LOOSE_P

### ImamHussain
- `12Inzel.html`: b4-9 HADITH_IN_CI, UNWRAPPED_EDITORIAL
- `13Ynsorh.html`: FOOTNOTES_SECTION, UNWRAPPED_EDITORIAL, HADITH_IN_CI
- `1Hob.html`: b9 COMBINED_BT

### ImamMahdi
- `1Mnkom.html`: b2-3 BOOK_AS_SN, EDITORIAL_IN_SN, UNWRAPPED_EDITORIAL, HADITH_IN_CI

### NabiMohd
- Various: HADITH_IN_CI, BOOK_AS_SN, COMBINED_BT, UNWRAPPED_EDITORIAL

### RAG
- `10Brdzbah.html`: b1-8 UNWRAPPED_EDITORIAL, EDITORIAL_IN_SN, COMBINED_BT
- `1Ftawi.html`: b4-6 UNWRAPPED_EDITORIAL, COMBINED_BT

### RS
- `1.html`: UNWRAPPED_EDITORIAL, HADITH_IN_CI
- `10.html`: LOOSE_P (needs rebuild)

### Seerah
- `10Slook.html`: b1-7 BOOK_AS_SN, b10-13 UNWRAPPED_EDITORIAL, COMBINED_BT
- `11Ysalli.html`: b1-2 BOOK_AS_SN

### SwR
- `10Karamat.html`: LOOSE_P, UNWRAPPED_EDITORIAL
- `11Dbor.html`: UNWRAPPED_EDITORIAL, SN_EQ_BT

### Threef
- `10hakim.html`: UNWRAPPED_EDITORIAL
- `11Hythami.html`: HADITH_IN_CI
- `12Byhaqi.html`: COMBINED_BT
- **Note**: In Threef, `scholar-name` holding a book name (e.g. صحيح البخاري) is INTENTIONAL — this folder is organized by book, not by scholar. NOT a BOOK_AS_SN error.

### Tjseem
- `10Yhrwel.html`: b2 BOOK_AS_SN
- `11Ynzil.html`: b1-2 BOOK_AS_SN
- Various: UNWRAPPED_EDITORIAL, HADITH_IN_CI, COMBINED_BT

---

## 9. Session Progress Log

| Session | What Was Done |
|---------|--------------|
| Sessions 1-4 | Structural fixes (loose_p, frag_note, bad_scholar) in 5 folders |
| Session 5 | 1,876 structural fixes across project |
| Session 6 | 1,076 scholar_eq_book, 64 empty scholars |
| Session 7 | 34Serran fixes, 70 المحب الطبري corrections |
| Session 8 | Batch 1: 22 pages + structural fixes |
| Session 9 | 57 pages, 20+ structural fixes |
| Session 10 | 64 pages, 30 structural fixes |
| Session 11 | Full content verification: Abawalnabi through Aqydatona (~430 files fixed across 13 commits) |
| Session 12 | Aqydatona 24ZQ rebuild (Type 2 special page), analysis-note font-size to 0.7rem |
| Session 13 | Planning for Handoff/Audit/Guide documentation |

---

## 10. Known Blockers / Data Injection Warning

**NEVER apply page/volume data from one file to blocks in a different file.**

Before applying any live-page data to a block, ALWAYS verify:
1. The local block's scholar/book matches the live page for that block
2. The volume number matches
3. The hadith number (if present) matches

If any field mismatches: **DO NOT APPLY** — flag as open issue.
