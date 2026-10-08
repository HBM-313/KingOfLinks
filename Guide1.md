&#x20;# KingOfLinks Cleanup — Session Handoff Prompt



&#x20; ## Project Overview

&#x20; Normalizing all `hadith-block` HTML elements across the KingOfLinks site repo to a

&#x20; consistent, correct structure. One folder at a time: inspect → fix → verify clean → commit.

&#x20; Content preservation is the HIGHEST priority — never invent or alter hadith text.



&#x20; Working directory: C:\\xampp\\htdocs\\AlQanas2\\KingOfLinks

&#x20; Live site: http://kingoflinks.net/  (uses .htm extension; repo uses .html)

&#x20; Branch: main





&#x20; ## Fetch Live Pages (WORKING — use this, not WebFetch)



&#x20; ```python

&#x20; def fetch\_live(path):

&#x20;     """path e.g. 'AhlAlBait/6Thqlain/22Ajori.htm'"""

&#x20;     import urllib.request

&#x20;     url = f"http://kingoflinks.net/{path}"

&#x20;     req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

&#x20;     with urllib.request.urlopen(req, timeout=15) as r:

&#x20;         html = r.read()

&#x20;     text = html.decode('windows-1256', errors='replace')

&#x20;     return url, text



&#x20; Run via Bash: python -X utf8 -c "..."

&#x20; Arabic must decode correctly (typically windows-1256); garbled text or numbers-only checks are not adequate for verification.

&#x20; Use numbers only as alignment aids. Full correctly decoded Arabic content from the current live original is required to approve a page.



&#x20; Inspection Script



&#x20; inspect\_folder.py at project root. Run:

&#x20;     python -X utf8 inspect\_folder.py FolderName

&#x20; Recursively checks all .html in that folder and subfolders.



&#x20; Issue Types (what the script detects)



&#x20; ┌─────────────────────┬───────────────────────────────────────────────────────────────────────────────────────┐

&#x20; │        Code         │                                        Meaning                                        │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ BOOK\_AS\_SN          │ Book/collection name is in scholar-name field (e.g. يراخبلا حيحص in scholar-name)     │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ SN\_EQ\_BT            │ scholar-name equals book-title                                                        │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ COMBINED\_BT         │ book-title contains scholar name merged with book name (e.g. "نيبلاطلا ةضور- يوونلا") │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ HADITH\_IN\_CI        │ Full hadith text placed in chapter-info span instead of hadith-text div               │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ UNWRAPPED\_EDITORIAL │ Editorial/analysis text floating directly in hadith-text without a span wrapper       │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ FLOATING\_NOTE       │ analysis-note div outside any hadith-block                                            │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ MISSING\_PAGE        │ ref-info missing ةحفصلا value                                                         │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ EMPTY\_SN            │ scholar-name div is empty                                                             │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ FOOTNOTES\_SECTION   │ Footnotes section present at bottom of article-body                                   │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ LOOSE\_P             │  tags floating directly in article-body outside any hadith-block                      │

&#x20; ├─────────────────────┼───────────────────────────────────────────────────────────────────────────────────────┤

&#x20; │ EDITORIAL\_IN\_SN     │ Editorial/note text placed in scholar-name field                                      │

&#x20; └─────────────────────┴───────────────────────────────────────────────────────────────────────────────────────┘



&#x20; Correct hadith-block Structure



&#x20; <div class="hadith-block">

&#x20;   <div class="scholar-name">ملاعلا مسا</div>

&#x20;   <div class="book-info">

&#x20;     <span class="book-title">باتكلا مسا</span>

&#x20;     <span class="chapter-info">بابلا/باتكلا (optional)</span>

&#x20;   </div>

&#x20;   <div class="ref-info">

&#x20;     <span><span class="ref-label">ءزجلا: </span><span class="ref-value">N</span></span>

&#x20;     <span><span class="ref-label">ةحفصلا: </span><span class="ref-value">N</span></span>

&#x20;   </div>

&#x20;   <div class="hadith-text">

&#x20;     <span class="hadith-number">N</span>  <!-- optional -->

&#x20;     <p>...</p>

&#x20;     <p><span class="editorial-note">دهاشلا عضوم هنم عطقتسا اذل ليوط صنلا</span></p>

&#x20;     <div class="analysis-note">...</div>  <!-- optional, INSIDE hadith-block -->

&#x20;   </div>

&#x20; </div>



&#x20; Special classes:

&#x20; - page-intro: intentional floating intro at top of article-body (NOT flagged as FLOATING\_NOTE)

&#x20; - editorial-note span: wraps short editorial markers inside <p> tags

&#x20; - analysis-note div: longer editorial/authentication notes — must be INSIDE a hadith-block



&#x20; Fix Patterns



&#x20; BOOK\_AS\_SN (most common):

&#x20; - scholar-name has collection name → move collection to book-title

&#x20; - book-title has sub-book → merge as chapter-info

&#x20; - Example: scholar-name=يراخبلا حيحص, bt=ماكحألا باتك, ci=- فالختسالا : باب

&#x20; → scholar-name=يراخبلا, bt=يراخبلا حيحص, ci=فالختسالا : باب - ماكحألا باتك



&#x20; COMBINED\_BT: Split "scholar -book" → separate scholar-name and book-title



&#x20; HADITH\_IN\_CI: Move hadith text from chapter-info into hadith-text div; keep only

&#x20; Y" in chapter-info : باب - X باتك"



&#x20; UNWRAPPED\_EDITORIAL: Wrap in <p><span class="editorial-note">...</span></p>



&#x20; LOOSE\_P / FOOTNOTES\_SECTION: Wrap loose paragraphs into proper hadith-blocks,

&#x20;   only when the live original proves these are separate sources; if genuinely introductory, use <div class="page-intro">, or attach analyses to their documented original section.



&#x20; )hadith number = page locator( ]hadith\_number\[ :ةحفصلا ,1 :ءزجلا :convention ينابلألا



&#x20; ## Mandatory Live-Source Verification (Current Policy — Overrides Older Instructions)

**No page may be approved unless its complete current original at `kingoflinks.net` has been retrieved, correctly decoded, and compared against the corresponding repository page.** The purpose is to ensure that the rebuilt page contains **all meaningful content present on the live page, with nothing omitted**, and that every item remains in the correct field and source block.

1. Begin with the project's `sitemap.xml` to identify the exact original `.htm` URL for each repository `.html` file. Treat `kingoflinks.net` as the sole authoritative source for the page's current content.
2. Fetch the **current live original**, not merely a cached snippet, historical repository version, database record, old audit, or a third-party mirror. For pages served in `windows-1256`, decode the complete response accurately; do not accept corrupted Arabic text, partial extraction, or number-only comparisons.
3. Compare the **entire live document** with the local page, from the initial title and `page-intro` through the last source and analysis. Account for every meaningful original item: all Arabic prose, individual quotations and narrations, source names, book and chapter headings, volume/page/page ranges, hadith numbers, editorial and analytical notes, `الحاشية` / `الحاشية رقم`, Quran text, sura and verse identifiers, `{ }`, `@`, parentheses, separators, and meaningful punctuation. Do not shorten, paraphrase, reorder, or silently "correct" the original.
4. Verify **content completeness, field ownership, and source-block boundaries** separately. Check every original source against the matching `hadith-block` in original order; do not combine independent sources or split one source without live evidence. Compare source **contents**, not just the number of blocks.
5. Pay special attention to **content-loss symptoms**: Quran citations reduced to fragments such as `( ا : 128 )`; missing verses or sura numbers; missing or duplicated hadith numbers; chapter headings inside `hadith-text`; evidence headings such as `الدليل الثاني` inside a source quotation; source commentary incorrectly included in `hadith-text`; lost concluding analysis paragraphs; source titles truncated to single letters; and text whose words exist locally but are under the wrong source or field.
6. Treat menu pages as full content: compare original headings, every visible topic label, target URL, order, individual topic counter, and total. A correct total does **not** validate incorrect per-topic counts; preserve original menu labels even if they differ from page titles.
7. After any correction, **re-fetch the modified file from `main`** and compare it again against the live original, including full text and source ownership. Automated scripts, counts, and text diffs assist screening but cannot independently establish approval.
8. Only then change that page to `[x]` in `tjek.md`, commit on `main`, and report the paths and commit results. If complete direct live comparison cannot be performed, leave the page `[ ]`, record the blocker precisely, and **do not claim it is verified**.
9. The original HTTrack snapshot in historical Git commit `6be3020bdca309b455c3d6c0092b155207f55fba` (with source comments referencing `kingoflinks.net`) may be consulted to diagnose older conversion defects, but **cannot substitute for checking the actual current live site** or justify an `[x]` when live access is unavailable. A snapshot is historical, not proof of today's live content.
10. Never consult or use `kufan.org` for this project. Do not use other mirrors as substitutes for the original.
11. Work in batches of exactly three unverified HTML pages (or fewer only when reaching the end of a folder); commit changes directly to `main`, leave `CGPT` and every backup branch untouched, and stop for the user's `fortsæt` after each batch. If one page is blocked, document it as unverified rather than silently skipping the completeness requirement.

**Important retroactive distinction:** Previous `[x]` statuses, including those granted using only the historical HTTrack snapshot, must not be described as **current-live-verified** until each page has also passed a complete direct comparison against the current `kingoflinks.net` original. Do not retroactively assume those pages are incorrect; their live verification is simply unproven.

## Permanent Verification Rules

&#x20; A page is verified on three levels: **content, field ownership, and block structure**. A text match alone is never enough.

&#x20; - `sitemap.xml` is the authoritative page list. Match each repo `.html` to its corresponding live `.htm` before approving it.
&#x20; - The live original at `http://kingoflinks.net/` is the default source of truth. Do not approve a page from an old audit, previous `[x]`, database match, or automated diff alone.
&#x20; - Verify menu/overview pages as real pages too: title, topic labels, link targets, order, and source counters must match the original.
&#x20; - Compare the number and order of original sources with the number and order of `hadith-block` elements. A block-count mismatch is a strong signal that sources were merged, split, or lost.
&#x20; - Never merge two distinct original sources into one `hadith-block`, even when they discuss the same quotation. Never split one original source into separate blocks without evidence from the original.
&#x20; - `scholar-name` contains only the scholar/source author. Book names, topic headings, chapter text, references, editorial text, and quotations must never be placed there.
&#x20; - `book-title` contains the book title. `chapter-info` contains book/chapter/section headings and structural Quran-heading text when the original uses them as source metadata.
&#x20; - `ref-info` must preserve all meaningful bibliographic information, not only volume and page. This includes footnote numbers such as `الحاشية` / `الحاشية رقم`, page ranges, and other original reference markers.
&#x20; - A hadith number belongs only in `hadith-number`. Do not duplicate it at the start of `hadith-text`. Remove migration artifacts such as an extra `1 -` only when direct comparison proves they are not part of the original text.
&#x20; - Quran material must be preserved completely, including `{ ... }`, `@`, sura names, verse numbers, verse ranges, parentheses, and punctuation that carries meaning.
&#x20; - `analysis-note` must stay attached to the same source block and in the same logical position as on the original. Do not move an analysis to the previous or next source.
&#x20; - A page title is not automatically a `page-intro`. Use `page-intro` only for genuine internal topic/section headings between source blocks.
&#x20; - Internal evidence/topic headings such as `الدليل الأول`, `الدليل الثاني`, etc. must not live inside `hadith-text` when they function structurally on the page; place them as `page-intro` immediately before the source they introduce.
&#x20; - A documented manual restoration may intentionally differ from the current live page when the project has explicitly established that the original itself omitted a required structural heading. Such exceptions must be preserved and not removed by later audits solely because live still lacks them.
&#x20; - Do not copy FrontPage/legacy rendering artifacts blindly. Broken visual spacing such as split digits or split words may be normalized when clearly caused by old HTML layout, but genuine original values and unusual references must be preserved exactly.
&#x20; - Do not linguistically modernize, correct, shorten, or rewrite original content. Strange spellings, odd references, and unusual values remain unchanged unless the live source proves the repo is wrong.
&#x20; - Automated diff/inspection is a screening tool only. Final approval requires direct manual comparison of scholar, book, chapter, refs, hadith number, quotation text, Quran references, analysis, ordering, and structural boundaries.
&#x20; - After every correction, re-fetch/re-read the repo page and perform a post-fix structural check before marking it complete.
&#x20; - Mark `[x]` in `tjek.md` only after the page itself has been verified clean. If the checklist cannot be written or committed, report that separately instead of pretending the status changed.
&#x20; - PDF files and images remain outside this verification workflow and are skipped.
&#x20; - Work directly on `main`. Backup branches such as `CGPT` must not be changed unless the user explicitly requests it.

&#x20; Historical Audit Folder Statuses (NOT Live-Verification Evidence)



&#x20; - Historical audit-only statuses (not proof of current-live verification): Abawalnabi, Abdulmtalib, Abutalib, AhlAlBait, Bahth, Mkhalfoon, Rdod



&#x20; Remaining Folders with Issues ❌



&#x20; Aqydatona



&#x20; - 11Shafaah.html: b1+b2 BOOK\_AS\_SN (ملسم حيحص), b7 UNWRAPPED\_EDITORIAL

&#x20; - 13Tqyyah.html: multiple UNWRAPPED\_EDITORIAL (b8,13-19), COMBINED\_BT b17-19 (روثنملا ردلا)



&#x20; Bhooth



&#x20; - 10Kayfa.html: b6 HADITH\_IN\_CI

&#x20; - 11Laban.html: multiple UNWRAPPED\_EDITORIAL, EDITORIAL\_IN\_SN (b2,6,8), COMBINED\_BT (b4,6,8)



&#x20; Daeefa



&#x20; - 1.html: b5 COMBINED\_BT (يئوخلا ديسلا)

&#x20; - 10.html: b2 HADITH\_IN\_CI

&#x20; - 12.html: b3 COMBINED\_BT

&#x20; - 13.html: b1,3,6 HADITH\_IN\_CI

&#x20; - 14.html: FOOTNOTES\_SECTION, b1 UNWRAPPED\_EDITORIAL, b3 HADITH\_IN\_CI

&#x20; - 16.html: (details below threshold — run inspect to see full output)



&#x20; Fatima



&#x20; - 18Shiah.html: many LOOSE\_P (needs content rebuild — partial/garbled migration)



&#x20; Hywan



&#x20; - 10Hayyah.html: b1-4 UNWRAPPED\_EDITORIAL, b3 EDITORIAL\_IN\_SN

&#x20; - 11Ghanam.html: b2 COMBINED\_BT, b2-7 UNWRAPPED\_EDITORIAL, b7 EDITORIAL\_IN\_SN

&#x20; - 12Other.html: b3 UNWRAPPED\_EDITORIAL



&#x20; ImamAli



&#x20; - 13Ybaye.html: b1 BOOK\_AS\_SN (يراخبلا), b2 BOOK\_AS\_SN (ملسم), b3-10 UNWRAPPED\_EDITORIAL

&#x20; - 14Yrfodh.html: multiple LOOSE\_P

&#x20; - (18Syed subfolder: known issues in 10ZKH.html b1, 7IbnAsaker.html b1, 8IbnQane.html b1 — SN\_EQ\_BT/BOOK\_AS\_SN)



&#x20; ImamHasan



&#x20; - 1Hob.html: b20-23 COMBINED\_BT (يذمرتلا ننس- يذمرتلا)

&#x20; - 2Tdleel.html: b7,9,10 HADITH\_IN\_CI

&#x20; - 6Bnood.html: multiple LOOSE\_P



&#x20; ImamHussain



&#x20; - 12Inzel.html: b4-9 HADITH\_IN\_CI and UNWRAPPED\_EDITORIAL

&#x20; - 13Ynsorh.html: FOOTNOTES\_SECTION, b1,3,5 UNWRAPPED\_EDITORIAL, b6 HADITH\_IN\_CI

&#x20; - 1Hob.html: b9 COMBINED\_BT (يذمرتلا)



&#x20; ImamMahdi



&#x20; - 1Mnkom.html: b2+3 BOOK\_AS\_SN (ملسم), b6+21 EDITORIAL\_IN\_SN, b7-9+19-20+25-26 UNWRAPPED\_EDITORIAL, b22-24 HADITH\_IN\_CI



&#x20; NabiMohd



&#x20; - 10LaYagheer.html: b1 HADITH\_IN\_CI

&#x20; - 11Mashoor.html: b1 UNWRAPPED\_EDITORIAL (×2)

&#x20; - 12Mkhneeth.html: b1 HADITH\_IN\_CI

&#x20; - 13Nabeeth.html: b1 BOOK\_AS\_SN (يراخبلا), b2 COMBINED\_BT

&#x20; - 17Yashek.html: b1+2 BOOK\_AS\_SN (ملسم + يراخبلا)

&#x20; - 18Yashoo.html: b1 COMBINED\_BT (يراخبلا حيحص -)



&#x20; RAG



&#x20; - 10Brdzbah.html: b1-8 UNWRAPPED\_EDITORIAL, b8 EDITORIAL\_IN\_SN + COMBINED\_BT

&#x20; - 1Ftawi.html: b4-6 UNWRAPPED\_EDITORIAL, b5+6 COMBINED\_BT



&#x20; RS



&#x20; - 1.html: b1+2 UNWRAPPED\_EDITORIAL, b5 HADITH\_IN\_CI

&#x20; - 10.html: multiple LOOSE\_P (needs content rebuild)



&#x20; Seerah



&#x20; - 10Slook.html: b1-7 BOOK\_AS\_SN (2× ملسم ,5× يراخبلا), b10-13 UNWRAPPED\_EDITORIAL + COMBINED\_BT

&#x20; - 11Ysalli.html: b1+2 BOOK\_AS\_SN (ملسم + يراخبلا)



&#x20; SwR



&#x20; - 10Karamat.html: many LOOSE\_P + b2 UNWRAPPED\_EDITORIAL (needs rebuild)

&#x20; - 11Dbor.html: b3-6 UNWRAPPED\_EDITORIAL, b9 SN\_EQ\_BT (يوونلا)



&#x20; Threef



&#x20; - 10hakim.html: b1 UNWRAPPED\_EDITORIAL

&#x20; - 11Hythami.html: b2-4 HADITH\_IN\_CI

&#x20; - 12Byhaqi.html: b1 COMBINED\_BT

&#x20; - 14IbnHjar.html: b1+2 UNWRAPPED\_EDITORIAL

&#x20; - 16Syooti.html: b1-3 UNWRAPPED\_EDITORIAL



&#x20; Tjseem



&#x20; - 10Yhrwel.html: b2 BOOK\_AS\_SN (ملسم)

&#x20; - 11Ynzil.html: b1+2 BOOK\_AS\_SN (ملسم + يراخبلا)

&#x20; - 12Yqabel.html: b3 UNWRAPPED\_EDITORIAL

&#x20; - 13Haqow.html: b2 UNWRAPPED\_EDITORIAL

&#x20; - 14Amaa.html: b5 HADITH\_IN\_CI

&#x20; - 15LA.html: b1 COMBINED\_BT, b3+4 UNWRAPPED\_EDITORIAL



&#x20; Workflow Per Folder



&#x20; 1. python -X utf8 inspect\_folder.py FolderName

&#x20; 2. Read flagged files

&#x20; 3. Fix issues (fetch live numbers via fetch\_live() if needed for page refs)

&#x20; 4. For missing/empty hadith-text: fetch live page and use numbers to align, ask user to

&#x20; paste Arabic content if text is needed and garbles too badly to reconstruct

&#x20; 5. Re-run inspect → confirm ALL CLEAN

&#x20; 6. git add <specific files> \&\& git commit -m "..."

&#x20; 7. When using the connected GitHub API, commit edits directly to main; with a local checkout, follow the user's current push instructions and confirm remote state before claiming the changes are on GitHub.



&#x20; Git State



&#x20; Historical note only: commit 3158d3f — AhlAlBait content restoration (not current repository HEAD)

&#x20; Historical status only. Re-check GitHub main for current commits and working state.

