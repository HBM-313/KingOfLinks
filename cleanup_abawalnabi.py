"""
Cleanup script: Abawalnabi folder  (v4 — single clean pass)
Fixes scholar-name / book-title / chapter-info attribution errors.
"""
import os, re
from bs4 import BeautifulSoup

FOLDER = 'Abawalnabi'
EDITORIAL = '[النص طويل لذا استقطع منه موضع الشاهد ]'

BOOK_TO_SCHOLAR = {
    'مجمع الزوائد ومنبع الفوائد': 'الهيثمي',
    'مجمع الزوائد': 'الهيثمي',
    'صحيح البخاري': 'البخاري',
    'صحيح مسلم': 'مسلم',
    'السنن الكبرى': 'البيهقي',
    'المعجم الكبير': 'الطبراني',
    'المستدرك على الصحيحين': 'الحاكم النيسابوري',
    'مسند الامام أحمد بن حنبل': 'أحمد بن حنبل',
    'صحيح ابن حبان': 'ابن حبان',
    'سير أعلام النبلاء': 'الذهبي',
    'البداية والنهاية': 'ابن كثير',
    'تاريخ دمشق': 'ابن عساكر',
}

JUNK_RE = re.compile(r'^(عدد|^\d|^قوله تعالى|^سورة|^باب\b|^كتاب\b|\s*$)')

# NOTE: 'مسند ' removed — it's often a book title (مسند أحمد), not just a chapter
CHAPTER_KW = ('كتاب', 'باب', 'فصل', 'ذكر', 'شرح', 'حرف', 'تتمة', 'جماع',
               'تفسير سورة', 'الباب', 'موضوع', 'سورة ')
CHAP_KW_PATTERN = r'كتاب|باب|فصل|ذكر|شرح|تفسير\s|تتمة|جماع|الباب|سورة\s|حرف\s'


def ct(tag):
    if tag is None: return ''
    return re.sub(r'\s+', ' ', tag.get_text(' ', strip=True)).strip()

def is_junk(t):
    return bool(JUNK_RE.match(t.strip())) if t else True

def is_chapter(t):
    return any(t.startswith(k) for k in CHAPTER_KW)

def split_combined(text):
    """Split 'A -B' into ('A', 'B')."""
    idx = text.find(' -')
    if idx > 1: return text[:idx].strip(), text[idx+2:].strip()
    return text, None

def extract_book_from_chapter(raw):
    """
    Given chapter-info text like '- المعجم الكبير -باب : العين - عكرمة...'
    returns (book_title, remaining_chapter_text).
    Keyword-split fires BEFORE space-split to avoid ` - عكرمة` stealing the split.
    """
    text = re.sub(r'^[\s\-–]+', '', raw).strip()
    if not text: return None, None

    # Priority 1: ` -keyword` (space + hyphen + chapter keyword, no space required after)
    m = re.search(r'\s+-\s*(' + CHAP_KW_PATTERN + r')', text)
    if m:
        b = text[:m.start()].strip()
        c = text[m.start():].lstrip('-').strip()
        if len(b) > 3 and not is_chapter(b):
            return b, c

    # Priority 2: ` - ` (spaces on both sides)
    parts = re.split(r'\s+[-–]\s+', text, maxsplit=1)
    if len(parts) == 2:
        b, c = parts[0].strip(), parts[1].strip()
        if len(b) > 3 and not is_chapter(b):
            return b, c

    # Whole string is the book title (no chapter found)
    if len(text) > 3 and not is_chapter(text):
        return text, None
    return None, text

def resolve_scholar(book):
    if not book: return None
    if book in BOOK_TO_SCHOLAR: return BOOK_TO_SCHOLAR[book]
    for k, v in BOOK_TO_SCHOLAR.items():
        if book.startswith(k): return v
    return None

def detect_scholar_problem(t):
    if not t: return 'missing'
    if t == EDITORIAL or t.startswith('[النص طويل'): return 'editorial'
    if t.startswith('(') and len(t) > 5: return 'topic'
    if t.startswith('سورة') or t.startswith('قوله تعالى'): return 'quran'
    if (t.startswith('ذكر ') and len(t) > 20) or t.startswith('تم الاستدلال'): return 'heading'
    if ' -' in t and len(t.split(' -')[0].strip()) > 1: return 'combined'
    # Scholar name that is actually a book name (e.g. "صحيح البخاري")
    if t in BOOK_TO_SCHOLAR: return 'bookname_as_scholar'
    return None

def add_ci(soup, bi_div, text):
    if text and text.strip():
        ci = soup.new_tag('span', attrs={'class': 'chapter-info'})
        ci.string = text.strip()
        bi_div.append(ci)

def fix_block(block, soup, block_idx):
    changes = []
    sn_div   = block.find('div', class_='scholar-name')
    bi_div   = block.find('div', class_='book-info')
    bt_span  = block.find('span', class_='book-title') if bi_div else None
    ci_spans = block.find_all('span', class_='chapter-info') if bi_div else []
    sn_text  = ct(sn_div)
    bt_text  = ct(bt_span)
    ci_texts = [ct(s) for s in ci_spans]
    problem  = detect_scholar_problem(sn_text)

    # =========================================================================
    # CASE 1: scholar wrong (missing/editorial/topic/quran/heading/bookname)
    # =========================================================================
    if problem in ('missing', 'editorial', 'topic', 'quran', 'heading', 'bookname_as_scholar'):
        note = sn_text if problem in ('editorial', 'topic', 'heading') else None

        # Decompose combined book-title "Scholar -Book [-Chapter]"
        bt_scholar, bt_book, bt_chap = bt_text, None, None
        if bt_text and ' -' in bt_text:
            s, rest = split_combined(bt_text)
            if rest and not is_junk(s):
                bt_scholar = s
                if rest and ' -' in rest:
                    bt_book, bt_chap = split_combined(rest)
                else:
                    bt_book = rest

        real_scholar = bt_scholar if not is_junk(bt_scholar) else None
        real_book    = bt_book   # may be None

        # Build remaining chapters: bt_chap first, then extract from ci_texts
        remaining = []
        if bt_chap:
            remaining.append(bt_chap)

        if not real_book and ci_texts:
            bk, ch_rest = extract_book_from_chapter(ci_texts[0])
            if bk:
                real_book = bk
                if ch_rest: remaining.append(ch_rest)
                remaining.extend(ci_texts[1:])
            else:
                remaining.extend(ci_texts)
        else:
            remaining.extend(ci_texts)

        # If real_scholar is itself a book name, look up actual scholar
        if real_scholar and real_scholar in BOOK_TO_SCHOLAR:
            if not real_book:
                real_book = real_scholar
            real_scholar = BOOK_TO_SCHOLAR[real_scholar]

        # For quran/junk, lookup from book
        if problem in ('quran', 'bookname_as_scholar') or is_junk(str(real_scholar)):
            looked = resolve_scholar(real_book or '')
            if looked:
                real_scholar = looked
            elif is_junk(str(real_scholar)):
                real_scholar = None

        # --- Apply scholar ---
        if real_scholar:
            if sn_div:
                if sn_text != real_scholar:
                    sn_div.string = real_scholar
                    changes.append(f'scholar: "{sn_text[:50]}" → "{real_scholar}"')
            else:
                new_sn = soup.new_tag('div', attrs={'class': 'scholar-name'})
                new_sn.string = real_scholar
                bi_div.insert_before(new_sn)
                changes.append(f'scholar [created]: "{real_scholar}"')

        # --- Apply book ---
        if bi_div and real_book:
            if bt_span:
                if bt_text != real_book:
                    bt_span.string = real_book
                    changes.append(f'book: "{bt_text[:50]}" → "{real_book}"')
            else:
                new_bt = soup.new_tag('span', attrs={'class': 'book-title'})
                new_bt.string = real_book
                bi_div.insert(0, new_bt)
                changes.append(f'book [created]: "{real_book}"')

        # --- Rebuild chapter spans ---
        if bi_div and remaining != ci_texts:
            for s in ci_spans: s.decompose()
            for ch in remaining: add_ci(soup, bi_div, ch)
            changes.append(f'chapters: {len(ci_texts)} → {len(remaining)}')

        # --- Move note to hadith-text ---
        if note:
            ht = block.find('div', class_='hadith-text')
            if ht and note not in ct(ht):
                p = soup.new_tag('p')
                p.string = note
                ht.insert(0, p)
                changes.append(f'note → hadith-text: "{note[:50]}"')

    # =========================================================================
    # CASE 2: scholar combined "Scholar -Book [-Chapter]"
    # =========================================================================
    elif problem == 'combined':
        scholar_part, rest = split_combined(sn_text)
        extracted_book = rest
        extracted_chap = None
        if rest and ' -' in rest:
            extracted_book, extracted_chap = split_combined(rest)

        sn_div.string = scholar_part
        changes.append(f'scholar split: "{sn_text[:60]}" → "{scholar_part}"')

        if bi_div:
            old_bt = bt_text
            if bt_span:
                bt_span.string = extracted_book
            else:
                new_bt = soup.new_tag('span', attrs={'class': 'book-title'})
                new_bt.string = extracted_book
                bi_div.insert(0, new_bt)
            changes.append(f'book: "{old_bt[:50]}" → "{extracted_book[:50]}"')

            if old_bt and (is_chapter(old_bt) or old_bt.startswith('تفسير سورة')):
                add_ci(soup, bi_div, old_bt)
                changes.append(f'old-book → chapter: "{old_bt[:50]}"')

            if extracted_chap:
                add_ci(soup, bi_div, extracted_chap)
                changes.append(f'chapter from split: "{extracted_chap[:50]}"')

    # =========================================================================
    # CASE 3: scholar OK, book-title combined "Book -Chapter"
    # =========================================================================
    if problem is None and bt_span and bt_text and ' -' in bt_text:
        m = re.search(r'\s+-\s*(' + CHAP_KW_PATTERN + r')', bt_text)
        if m:
            book_part = bt_text[:m.start()].strip()
            chap_part = bt_text[m.start():].lstrip('-').strip()
            bt_span.string = book_part
            add_ci(soup, bi_div, chap_part)
            changes.append(f'book split: "{bt_text[:60]}" → "{book_part}" + "{chap_part[:40]}"')
        else:
            idx = bt_text.find(' -')
            if idx > 3:
                book_part = bt_text[:idx].strip()
                chap_part = bt_text[idx+2:].strip()
                bt_span.string = book_part
                add_ci(soup, bi_div, chap_part)
                changes.append(f'book split: "{bt_text[:60]}" → "{book_part}" + "{chap_part[:40]}"')

    return changes


def process_file(filepath):
    with open(filepath, encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    blocks = soup.find_all('div', class_='hadith-block')
    all_changes = []
    for i, block in enumerate(blocks):
        c = fix_block(block, soup, i + 1)
        if c: all_changes.append((i + 1, c))
    if all_changes:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    return all_changes


def main():
    files = sorted([f for f in os.listdir(FOLDER)
                    if f.endswith('.html') and f != 'Main116.html'])
    print(f'Processing {len(files)} files in {FOLDER}/\n')
    total = 0
    for fname in files:
        changes = process_file(os.path.join(FOLDER, fname))
        if changes:
            print(f'{fname}:')
            for bn, cl in changes:
                for c in cl: print(f'  block {bn}: {c}')
            total += sum(len(c) for _, c in changes)
        else:
            print(f'{fname}: ✓ no changes')
    print(f'\nTotal changes: {total}')

if __name__ == '__main__':
    main()
