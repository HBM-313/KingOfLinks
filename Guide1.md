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

## Lessons from Live Verification — Specific Failure Modes

These are **additional checks** drawn from direct comparison with `kingoflinks.net`. They supplement, rather than replace, the mandatory three-level verification rules above.

1. **Detect duplicated `page-intro` elements.** Compare the number, wording, and location of original introductory headings or Quran verses. An accidental duplicate may appear even when every hadith block is otherwise correct. Do not delete intentional Quran repetitions *inside* different original quotations; distinguish these from a repeated page introduction.
2. **Reconstruct hadith numbers across legacy HTML tags.** FrontPage markup may split one colored number into separate elements, e.g. `3` + `2272` = `32272`, or `3754` + `4` = `37544`. Inspect the actual source markup and surrounding text before deciding whether adjacent digits are one number. Store the verified number in `hadith-number`, not in `hadith-text`, and do not duplicate it.
3. **Never equate `hadith-count` with the number of source blocks.** The original may state 24 narrations while containing only six independent bibliographic sections, as on `38Byoomi.htm`. Verify the displayed count against the original **and independently** verify the number and order of `hadith-block` elements against the original source divisions. Do not force these two counts to agree.
4. **Audit navigation indexes for omitted links and shifted row numbers.** Check every link target against the live menu, including intermediate entries even when their destination pages already exist locally. A missing `13IbnAbiShaybah.html` link in `Main58.html` caused subsequent row positions to shift. After inserting a row, verify the complete link order, numbering, labels, and counters against the original rather than assuming adjacent links are sufficient.
5. **Avoid text loss or word fusion at extraction and chunk boundaries.** When fetching or assembling long Arabic documents in multiple chunks, preserve exact character boundaries. Accidental joins can change `أشهر كان` to `أشهركان`, or split digits and punctuation. Compare **each complete source-block text** with the correctly decoded original after assembly and after editing, not only page-level lengths, excerpts, or word counts.
6. **Verify the final GitHub commit, not an earlier working copy.** After the *last* HTML edit, fetch that exact file again from `main` and recheck text, field ownership, source order, references, numbers, intro count, and analysis notes. Commit the `tjek.md` `[x]` update only after successful verification; read the checklist again to confirm that its recorded status matches the committed state. Any later correction requires another post-commit check.

**Acceptance reminder:** Exact normalized text matching is necessary but **not sufficient**. Approve a page only when (a) all meaningful live content is preserved, (b) each item belongs to its correct structural field, and (c) source order and block boundaries match the live original. Never infer a missing field, number, or boundary from assumptions.

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



## Supplement — Batch 25 lessons (2026-10-20; additive, newer guidance takes precedence where older text conflicts)

- **Live text is canonical, not merely semantically equivalent.** Always fetch the current original `.htm` from the precise `sitemap.xml` entry via Vercel Sandbox (`http://kingoflinks.net/`, User-Agent `Mozilla/5.0`, decode `windows-1256`). Compare the complete original Arabic source directly to the matching repository `.html`. Preserve every meaningful character and its original source ownership.
- **A near-match is a failed comparison.** Batch 25 exposed superficially similar hadith passages missing `{ }`, `( آل عمران : 61 )`, `( آل عمران : 59 - 60 - 61 )`, Quranic marks such as `ٰ` and `ۖ`, punctuation, and citation fragments. Word-presence or high similarity scores cannot approve these.
- **Check independent page-intro Quran passages.** `3Mbahala/6IbnKatheer.html`, `7Syooti.html`, and `8Tabari.html` previously had no `page-intro` despite the original Quranic introduction. Compare its full content, its count, placement, opening/closing symbols, and distinguish it from the heading in `<title>`/`<h2>` and Quran passages repeated legitimately inside separate source blocks.
- **Compare original paragraphs in full and in order.** For each original source, map every quotation, paragraph, editorial remark, bibliography item, and Quran reference to one local `hadith-block`. Do not rely on count alone. For batch 25 the original divisions were 4 + 2 + 6 source blocks; this is historical context, not a reusable count for other pages.
- **Never silently duplicate a hadith number.** Batch 25's `8Tabari.html` still had `2634` in both a `hadith-number` element and the leading text paragraph after commit. This is a **known follow-up structural issue**: verify the exact live number and its ownership, put it in `hadith-number` exactly once, and preserve the following text without an extra copy. A perfect text-presence test does not detect this.
- **The source heading is not automatically hadith prose.** Check `تفسير قوله تعالى`, `ذكر ما جاء`, `آل عمران : 61` and similar headings: their original positions determine whether they belong in `chapter-info`, `page-intro`, or quotation text. Never move or omit them on heuristic grounds.
- **A generated diff is not the whole validation.** Inspect source-block order, per-field ownership, complete Quran notation and formatting semantically; re-fetch each committed `.html` from GitHub `main`, compare to intended content, and only then mark `[x]` in `tjek.md`. If GitHub/Vercel tool calls fail, retry safely; **do not call the page finished or claim a commit that did not succeed**. Do not stage temporary transfer files; never touch CGPT/backup folders and never visit kufan.org.
- **Work in exactly three-page batches, not three guessed pages.** Read the current `tjek.md` and `main` before selecting the next three `[ ]` HTML entries. Historical user handoffs and progress figures can be stale. Additive documentation must not erase earlier historical logs, even where they describe an older practice.
- **Repository state (historical checkpoint, 2026-10-20):** batch 25 HTML commits `62ea6273`, `f66d7bcf`, `8febfe37`; checklist commit `33305cda`; `AhlAlBait` showed 75/210. The outstanding `2634` duplication should be checked before treating its structural review as fully resolved. Re-read actual `main` for all future work.

**Resolution — 2026-10-20:** The known duplicate `2634` in `AhlAlBait/3Mbahala/8Tabari.html` was checked against the current original `8Tabari.htm` using Vercel Sandbox. The live original has one occurrence. Removed the redundant number from the beginning of the hadith text while preserving `<span class="hadith-number">2634</span>`. Committed on `main` as `504dcd46` and re-fetched with exact content match. The historical warning above remains as a regression example; the specific issue is now closed.


## Mandatory Completion Gate — No Partial Corrections (2026-10-20)

**Always finish the full verification and the full correction of every page in the active batch. Partial fixes are not acceptable.** First compare each page completely against its current `kingoflinks.net` `.htm` original (correctly decoded); verify every meaningful item, correct field ownership and exact source-block boundaries/order. Then fix **all** documented deviations, including minor text, punctuation, Quran references, headings, bibliographic values, editorial notes and separators. Re-fetch every committed HTML from GitHub `main` and repeat the complete three-level verification. Do not mark any page `[x]`, increase totals, report a batch as complete, or start the next batch until all three pages have passed the final post-commit check. If blocked, keep the batch open, report the exact blocker and do not present partial progress as completion. Preserve existing guidance and historical records.


## Uniform modern Main-page structure — mandatory (2026-10-20)

**Goal: a consistent website-wide layout and structure.** For each index/menu page (`Main*.html`), use the already modernized `Abawalnabi/Main116.html` as the structural and visual reference, adapted only for the correct relative links and the page's actual content.

- Keep the common `page-wrap`, `page-nav`, `page-title`, `menu-container`, and `menu-table` layout with the existing shared `modern.css`. Do not introduce a one-off menu layout when the standard works.
- Use exactly the standard three visible menu columns: `ت` (ordinal), `الموضوع` (link text), `المصادر` (source count). Use one source/topic per row, in the original source order. Place the ordinal **only** in `col-num`; place the complete original source/topic name **only** inside the `col-topic` link; display the original count **only** under `col-count` using `count-badge`. Do **not** append counts to the clickable link text and do not use repeated page titles in place of source/topic names.
- Preserve the source page's actual title, introductory material, headings, all links and destinations (convert `.htm` to the corresponding repo `.html`), source/topic names, ordering, numbers, distinct counts, overall source total (if present), symbols and meaningful content. Use `sitemap.xml` and directly re-read the matching `kingoflinks.net` original before changing the page. Never derive or guess counts from another page or from automated summaries.
- The old site's multi-column or nested FrontPage layout may be normalized to the standard **one-topic-per-row** table as a presentational change; the underlying original ordering, source boundaries and field ownership must remain correct. In particular do not lose a right-hand column's sources when flattening a two-column original.
- Use the shared navigation convention and correct relative links for the current directory. Do not blindly copy filenames, headings, counters or paths from `Main116.html`.
- Verify all entries against the live original, then commit to `main`, re-fetch the committed HTML and recheck the link texts, destinations, ordinals, counts, total, headings and structure before marking the page `[x]`. The no-partial-fixes rule remains absolute.

**Regression example (2026-10-20):** `AhlAlBait/3Mbahala/Main60.html` initially repeated the Quran/page heading for every menu item and showed erroneous figures. A later version restored the 17 original source links but retained an inconsistent two-column layout and embedded the counts in the links. The standardized correction follows `Abawalnabi/Main116.html`: 17 separate menu rows, three columns, original source labels, source counts only in `المصادر`, and overall count 72. Final layout commit `a852d1be1f4d956d5512de321992e413bd0c4207`. Earlier intermediate corrections are historical, not approved templates.


## Lessons from live verification batches 46–50 — binding practice (2026-10-21)

These rules supplement, without deleting, previous guidance. **Qualified correction of obvious typographical/technical errors (item 9) replaces any blanket instruction to reproduce such obvious accidental spaces verbatim.** Never use this exception to rewrite meaningful original content.

1. **Independent scholar field:** In each `hadith-block`, `scholar-name` must be a dedicated direct field, **outside** `book-info`; a name nested in book metadata is structurally wrong even if visible text is correct. Example: `9Khleefa/3Muslim.html` and `9Khleefa/7Hakim.html`.
2. **Complete book title:** Compare the complete `book-title` against the specific original source header. A nonempty title is not proof: `8Njoom.html` contained only `ا` as a purported title. Do not mistake a scholar, chapter or book-series description for an actual book title. If the original does not document a book title, do **not** invent one.
3. **Chapter ownership in every block:** Original book/chapter/section lines belong in `chapter-info`, not as stray paragraphs in `hadith-text`. Verify each occurrence independently, even where a heading repeats dozens of times; `9Khleefa/4IbnHnbal.html` required checking all **34** original headings. Do not globally impose one chapter heading across sources without checking original order.
4. **Repeated hadith numbers are valid:** The same original hadith number can occur in multiple independent source blocks (e.g. `1821` in `9Khleefa/3Muslim.html`). Never merge or deduplicate blocks merely because their numbers match.
5. **Single number ownership:** When the original identifies a hadith number, put it in `hadith-number` exactly once, not also as a redundant prefix to `hadith-text`. Avoid accidentally stripping original narrative digits, chapter numbers, reference numbers or editorial number expressions.
6. **Menus have their own audit:** For `Main*.html`, verify **each** original row's ordinal, link destination, distinct source/topic label, source count, order and page total. `7SafinatNooh/Main61.html` initially repeated one page heading across all 13 links and mismatched counts. `col-num` owns the ordinal; only `col-count` owns the count. Keep the established `Main116.html` structural pattern.
7. **Paragraph splits versus source blocks:** A single narration may span several original HTML elements (or several local `p` elements); compare its full combined text **within the same independent source block** as well as paragraph-level details. A one-to-one paragraph similarity mismatch can be a false alarm, but must be resolved, not ignored. Do not join independent sources to make a text comparison pass.
8. **Near-perfect similarity is not completion:** A 98–99% match can hide missing meaningful words; `8Njoom.html` required restoring `وأنا أمان لأصحابي`. Explicitly check omissions, inserted fragments, punctuation, important particles and all Quranic material after alignment.
9. **Correct only unequivocal technical typos:** The live original remains the content authority, **but clearly accidental spacing/splitting errors should be normalized when the intended spelling is unambiguous**: `ر سول الله` → `رسول الله`, `ا لترمذي` → `الترمذي`, `ا لمستدرك` → `المستدرك`, `حد يث` → `حديث`, `ا لجزء` → `الجزء`. The same principle covers indisputable stray spaces or split characters. Record/recognize these as deliberate typo fixes, not missing original content. **Do not** modernize, rephrase or 'correct' unusual names, manuscript readings, bibliographic references, hadith/Quran spellings, numerals, source-specific wording or any ambiguous case. When unsure, preserve the original and investigate it first; do not guess.
10. **Editorial notes vs source analysis:** Preserve bracketed extraction notes such as `[ النص طويل لذا استقطع منه موضع الشاهد ]` in `editorial-note`. Source-author critical evaluations (e.g. `هذا حديث صحيح الاسناد ، ولم يخرجاه`, `نوع الحديث : صحيح`, `قال أبو عيسى : هذا حديث حسن صحيح`) belong in `analysis-note` where structurally appropriate, not in the editorial-note field or silently dropped. Preserve the full text and its source ownership.
11. **Vercel Sandbox lifecycle:** For `kingoflinks.net` use a Vercel Sandbox Python `urllib.request` fetch with normal User-Agent and correct `windows-1256` decoding. A new sandbox may fail because of storage quota while **resuming an existing named sandbox** works. A session can also expire during a batch: resume it and rerun interrupted verifications. Do not mark a batch done when the connection fails.
12. **Post-commit evidence:** After every correction, re-fetch the **latest committed** HTML from GitHub `main` (or immutable commit SHA), compare content, fields, source-block count and order, hadith numbers and all relevant menu links again against the original. Cached raw URLs can return stale content: prefer exact commit-addressed fetches or fresh GitHub `main` file reads and verify SHA. Only then update `tjek.md`. Never treat an old `[x]`, automated similarity, existing local text, database or audit report as certification.

**Batch exit rule:** Complete correction of all known differences for all three pages first. No partial fixes, speculative gap filling or checklist marks before verified post-commit completion. For item 9 the only permissible exception to exact original spelling is a *certain*, meaning-preserving correction of an obvious typing/layout defect.


## Responsive narrator evaluation cards (verified design, 2026-10-21)

When a canonical `.htm` page contains a table/grid of narrators and scholarly evaluations, preserve the **meaning and complete data** but not the outdated FrontPage table layout. Implement the existing KingOfLinks narrator-card design in `modern.css`, rather than rendering assessments as a flat prose list.

- Place narrator evaluations in a separate `<section class="narrator-section">` containing the heading `section-heading` and a `<div class="narrator-grid">`. Use **one** `<article class="narrator-card" data-narrator-order="N">` per original narrator, in the exact original order, with `<h4 class="narrator-name">` for the name and `<div class="narrator-evaluations">` for the assessments.
- Use one `<div class="narrator-evaluation">` per original assessment, containing **both** `<span class="evaluation-scholar">` (who gave it) and `<span class="evaluation-text">` (their verbatim statement), in original order. Unattributed stand-alone remarks, such as a companion's status, use `<p class="narrator-remark">`, **not** an invented scholar/evaluation pair.
- **Never** conflate a narrator, reviewer, evaluation, bibliographic source, hadith text, editorial note, and analytical note. Keep the source's original wording (e.g. `ثقة`, `صدوق`, `فيه ضعف`) without introducing subjective translation, categorization, scoring, or colors implying new scholarly judgments. Preserve associated bibliographic citation blocks separately with their correct `scholar-name`, `book-title`, `chapter-info`, `ref-info`, `hadith-number` and `hadith-text` ownership.
- Design stays consistent with the shared site theme via **`modern.css`**: 3 columns on desktop, 2 on tablet, 1 on mobile; the assessments are all **visible by default**, without collapsible content. Do not duplicate presentation styles inline or create per-page one-offs. This semantic HTML is **database-ready** (narrator → assessment → reviewing scholar and citation) but remains static until an explicit data migration; do not invent IDs/links or normalize uncertain names.
- Verification is **both content and UI**: compare every original narrator cell and assessment verbatim and in order against the resulting cards, including counts and unpaired remarks; check accessibility/legibility across screen sizes. After CSS or template changes, also inspect the **deployed production** HTML and `https://kingoflinks.vercel.app/modern.css`: GitHub `main` having the correct CSS does **not** prove the production CSS deployed. If production still shows a single long column, confirm the deployment SHA and trigger a fresh production deployment from the intended `main` commit, then re-fetch live assets. Do not declare the design fixed until the live styles and cards are confirmed.
- Confirmed examples: `AhlAlBait/10Hrbhom/2Trmethee.html` has **6 narrator cards / 22 assessments**, and `3IbnMajah.html` has **6 cards / 31 assessments** (53 total), with fields faithfully checked against their original table cells. Shared stylesheet: `modern.css`. Avoid re-adding this same material as unstructured paragraphs under `analysis-note`.

This visual modernization is allowed **only** when full original content, source ownership, and source block structure remain verifiable; the usual original-first and complete-batch rules still apply.
