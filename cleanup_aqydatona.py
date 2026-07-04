#!/usr/bin/env python3
"""Cleanup script for Aqydatona folder - fix all data quality issues."""

import glob
import re
from bs4 import BeautifulSoup

EDITORIAL_TEXT = 'النص طويل لذا استقطع منه موضع الشاهد'
EDITORIAL_PATTERN = re.compile(
    r'\[?\s*النص طويل\s*(?:جدا\s*)?لذا استقطع منه موضع الشاهد\s*\]?'
)
HADITH_IN_CI_RE = re.compile(r'^-\s*(\d+)\s*-\s*(.{10,})', re.DOTALL)
CHAPTER_SPLIT_RE = re.compile(
    r'\s*-+\s*(?:كتاب|باب|فصل|حرف|الطبقة|المجلد|الجزء|ذكر|من اسمه|من اسمها|'
    r'القسم|النوع|الفصل|الباب|مسألة|أبواب)',
    re.IGNORECASE,
)
CHAPTER_STARTS_RE = re.compile(
    r'^(?:كتاب|باب|فصل|حرف|ذكر|من اسمه|الطبقة|المجلد|الجزء|مسألة|أبواب)',
    re.IGNORECASE,
)

BOOK_TO_SCHOLAR = {
    'صحيح البخاري': 'البخاري',
    'صحيح مسلم': 'مسلم',
    'صحيحمسلم': 'مسلم',   # common concatenation typo
    'سنن أبي داود': 'أبو داود',
    'سنن الترمذي': 'الترمذي',
    'سنن ابن ماجه': 'ابن ماجه',
    'السنن الكبرى': 'البيهقي',
    'المستدرك على الصحيحين': 'الحاكم النيسابوري',
    'مجمع الزوائد ومنبع الفوائد': 'الهيثمي',
    'مسند الامام أحمد بن حنبل': 'أحمد بن حنبل',
    'صحيح ابن حبان': 'ابن حبان',
    'المعجم الكبير': 'الطبراني',
    'المعجم الأوسط': 'الطبراني',
    'البداية والنهاية': 'ابن كثير',
    'تاريخ دمشق': 'ابن عساكر',
    'سير أعلام النبلاء': 'الذهبي',
    'سنن الدارمي': 'الدارمي',
    'موطأ مالك': 'مالك بن أنس',
    'سنن النسائي': 'النسائي',
    'المحلى بالآثار': 'ابن حزم',
    'شرح مسلم': 'النووي',
    'نيل الأوطار': 'الشوكاني',
    'المصنف': 'الصنعاني',
    'المسند': 'أحمد بن حنبل',
    'كنز العمال في سنن الأقوال والأفعال': 'المتقي الهندي',
}

# When only scholar known from bt field and can't extract book from ci
AUTHOR_TO_BOOK = {
    'الشوكاني': 'نيل الأوطار',
    'البيهقي': 'السنن الكبرى',
    'الطبراني': 'المعجم الكبير',
    'النووي': 'شرح مسلم',
    'الحلبي': 'السيرة الحلبية',
    'الصنعاني': 'المصنف',
    'الهيثمي': 'مجمع الزوائد ومنبع الفوائد',
    'ابن أبي شيبة': 'الكتاب المصنف في الأحاديث والآثار',
    'السرخسي': 'المبسوط',
    'ابن قدامه': 'المغني',
    'البكري الدمياطي': 'اعانة الطالبين',
    'الشربيني': 'مغني المحتاج',
    'محمود سعيد ممدوح': 'رفع المنارة',
    'الخوارزمي': 'مناقب أبي حنيفة',
    'ابن عساكر': 'تاريخ دمشق',
    'الذهبي': 'سير أعلام النبلاء',
    'ابن حزم': 'المحلى بالآثار',
}

changes = 0


def make_editorial_p(soup):
    p = soup.new_tag('p')
    span = soup.new_tag('span', **{'class': 'editorial-note'})
    span.string = EDITORIAL_TEXT
    p.append(span)
    return p


def ensure_editorial_in_ht(block, soup):
    global changes
    ht = block.select_one('.hadith-text')
    if ht:
        has_editorial = any(
            p.select_one('.editorial-note') or EDITORIAL_PATTERN.search(p.get_text())
            for p in ht.select('p')
        )
        if not has_editorial:
            ep = make_editorial_p(soup)
            ht.insert(0, ep)
            changes += 1
    else:
        ref = block.select_one('.ref-info')
        ht_div = soup.new_tag('div', **{'class': 'hadith-text'})
        ep = make_editorial_p(soup)
        ht_div.append(ep)
        if ref:
            ref.insert_after(ht_div)
        else:
            block.append(ht_div)
        changes += 1


def parse_scholar_book_from_sn_bt(sn_txt, bt_txt, ci_texts=None):
    """Parse scholar/book from sn/bt fields, return (scholar, book, new_ci0_or_None)."""
    new_ci0 = None
    sn_clean = sn_txt.rstrip('- ')

    # Pattern C: sn is a known book title
    if sn_clean in BOOK_TO_SCHOLAR:
        return BOOK_TO_SCHOLAR[sn_clean], sn_clean, None

    # Pattern B: sn has dash → "scholar - book [- chapter...]"
    if '-' in sn_txt:
        m = re.match(r'^([^-]+?)\s*-+\s*(.+)', sn_txt, re.DOTALL)
        if m:
            scholar = m.group(1).strip()
            rest = m.group(2).strip()
            ch_m = CHAPTER_SPLIT_RE.search(rest)
            book = rest[:ch_m.start()].strip() if ch_m else rest.rstrip('- ').strip()
            return scholar, book or bt_txt, None

    # Pattern A-C on bt field: bt is a known book title
    if bt_txt in BOOK_TO_SCHOLAR:
        return BOOK_TO_SCHOLAR[bt_txt], bt_txt, None

    # Pattern B on bt: bt has dash
    if '-' in bt_txt:
        m = re.match(r'^([^-]+?)\s*-+\s*(.+)', bt_txt, re.DOTALL)
        if m:
            scholar = m.group(1).strip()
            rest = m.group(2).strip()
            ch_m = CHAPTER_SPLIT_RE.search(rest)
            book = rest[:ch_m.start()].strip() if ch_m else rest.rstrip('- ').strip()
            return scholar, book or sn_txt, None

    # Pattern A: bt=scholar, book from ci
    scholar = bt_txt or sn_clean
    if ci_texts:
        ci_raw = ci_texts[0].lstrip('- ')
        if not CHAPTER_STARTS_RE.match(ci_raw.strip()):
            ch_m = CHAPTER_SPLIT_RE.search(ci_raw)
            if ch_m:
                book = ci_raw[:ch_m.start()].strip()
                new_ci0 = '- ' + ci_raw[ch_m.start():].lstrip('- ').strip()
                return scholar, book, new_ci0
            else:
                parts = re.split(r'\s*-+\s*', ci_raw, 1)
                if len(parts) > 1:
                    return scholar, parts[0].strip(), '- ' + parts[1].strip()
    # Fallback to AUTHOR_TO_BOOK
    book = AUTHOR_TO_BOOK.get(scholar, scholar)
    return scholar, book, None


def fix_editorial_sn_block(block, soup, blocks=None, block_idx=None):
    """Fix EDITORIAL_SN block."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not sn: return

    bt_text = bt.get_text(strip=True) if bt else ''
    ci_elements = block.select('.chapter-info')
    ci_texts = [c.get_text(strip=True) for c in ci_elements]

    # If bt is a placeholder (dots, very short), use context propagation
    if not bt_text or re.match(r'^[.\s]+$', bt_text):
        scholar, book = None, None
        if blocks and block_idx is not None:
            scholar, book = get_nearby_context(blocks, block_idx)
        if not scholar:
            scholar = '?'
            book = '?'
    else:
        scholar, book, new_ci0 = parse_scholar_book_from_sn_bt(bt_text, '', ci_texts)

        # If book came from ci, also update the ci element
        if new_ci0 and ci_elements:
            ci_elements[0].clear()
            ci_elements[0].append(new_ci0)
            changes += 1

    # Update sn
    sn_text = sn.get_text(strip=True)
    if sn_text != scholar:
        sn.clear()
        sn.append(scholar)
        changes += 1

    # Update bt
    if bt and bt_text != book:
        bt.clear()
        bt.append(book)
        changes += 1

    ensure_editorial_in_ht(block, soup)


def get_nearby_context(blocks, idx):
    """Scan backward/forward for nearest valid scholar/book context."""
    for j in range(idx - 1, -1, -1):
        sn = blocks[j].select_one('.scholar-name')
        bt = blocks[j].select_one('.book-title')
        sn_txt = sn.get_text(strip=True) if sn else ''
        bt_txt = bt.get_text(strip=True) if bt else ''
        sn_stripped = sn_txt.strip('‏ ')
        if (sn_txt and not EDITORIAL_PATTERN.search(sn_txt)
                and not sn_stripped.isdigit()
                and sn_txt not in ('المصادر :', 'المصدر :')
                and not sn_txt.startswith('(')):
            s, b, _ = parse_scholar_book_from_sn_bt(sn_txt, bt_txt)
            if s and s != '?':
                return s, b
    for j in range(idx + 1, len(blocks)):
        sn = blocks[j].select_one('.scholar-name')
        bt = blocks[j].select_one('.book-title')
        sn_txt = sn.get_text(strip=True) if sn else ''
        bt_txt = bt.get_text(strip=True) if bt else ''
        sn_stripped = sn_txt.strip('‏ ')
        if (sn_txt and not EDITORIAL_PATTERN.search(sn_txt)
                and not sn_stripped.isdigit()
                and sn_txt not in ('المصادر :', 'المصدر :')
                and not sn_txt.startswith('(')):
            s, b, _ = parse_scholar_book_from_sn_bt(sn_txt, bt_txt)
            if s and s != '?':
                return s, b
    return None, None


def fix_sn_number_bt_text(block, soup, scholar, book, hadith_num):
    """Move bt content (hadith text/chain) to hadith-text; set sn=scholar, bt=book."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not bt:
        return

    hadith_body = bt.get_text(strip=True)

    if sn and sn.get_text(strip=True) != scholar:
        sn.clear()
        sn.append(scholar)
        changes += 1

    if bt.get_text(strip=True) != book:
        bt.clear()
        bt.append(book)
        changes += 1

    ht = block.select_one('.hadith-text')
    if not ht:
        ref = block.select_one('.ref-info')
        ht = soup.new_tag('div', **{'class': 'hadith-text'})
        if ref:
            ref.insert_after(ht)
        else:
            block.append(ht)
        changes += 1

    if hadith_num and not ht.select_one('.hadith-number'):
        hn = soup.new_tag('span', **{'class': 'hadith-number'})
        hn.string = str(hadith_num)
        ht.insert(0, hn)
        changes += 1

    p = soup.new_tag('p')
    p.string = hadith_body
    ht.append(p)
    changes += 1


def propagate_scholar_book(soup, blocks):
    """Fix sn=number + bt=chain blocks using context propagation."""
    global changes

    # Build context map from valid blocks
    contexts = {}
    for i, b in enumerate(blocks):
        sn = b.select_one('.scholar-name')
        bt = b.select_one('.book-title')
        if not sn:
            continue
        sn_txt = sn.get_text(strip=True)
        bt_txt = bt.get_text(strip=True) if bt else ''
        sn_stripped = sn_txt.strip('‏ ')
        if (sn_stripped.isdigit()
                or EDITORIAL_PATTERN.search(sn_txt)
                or sn_txt in ('المصادر :', 'المصدر :')
                or sn_txt.startswith('(')):
            continue
        scholar, book, _ = parse_scholar_book_from_sn_bt(sn_txt, bt_txt)
        if scholar and scholar != '?':
            contexts[i] = (scholar, book)

    # Fix number blocks
    for i, b in enumerate(blocks):
        if b.select_one('.hadith-text'):
            continue
        sn = b.select_one('.scholar-name')
        bt = b.select_one('.book-title')
        if not sn or not bt:
            continue
        sn_stripped = sn.get_text(strip=True).strip('‏ ')
        if not sn_stripped.isdigit():
            continue
        bt_txt = bt.get_text(strip=True)
        bt_is_chain = len(bt_txt) > 30 and ('حدثنا' in bt_txt or 'أخبرنا' in bt_txt)
        if not bt_is_chain:
            continue

        scholar = book = None

        # Check ci for book hint
        for ci in b.select('.chapter-info'):
            ci_txt = ci.get_text(strip=True).lstrip('- ')
            ch_m = CHAPTER_SPLIT_RE.search(ci_txt)
            if ch_m:
                potential_book = ci_txt[:ch_m.start()].strip()
                if potential_book and potential_book in BOOK_TO_SCHOLAR and not CHAPTER_STARTS_RE.match(potential_book):
                    scholar = BOOK_TO_SCHOLAR[potential_book]
                    book = potential_book
                    break

        # Context propagation backward
        if not scholar:
            for j in range(i - 1, -1, -1):
                if j in contexts:
                    scholar, book = contexts[j]
                    break
        # Context propagation forward
        if not scholar:
            for j in range(i + 1, len(blocks)):
                if j in contexts:
                    scholar, book = contexts[j]
                    break

        if not scholar:
            print('  WARNING: no context for num block at index ' + str(i + 1))
            continue

        fix_sn_number_bt_text(b, soup, scholar, book, sn_stripped)


def fix_hadith_in_ci(block, soup, ci_element):
    """Move hadith content from chapter-info to hadith-text."""
    global changes
    ci_text = ci_element.get_text(strip=True)
    m = HADITH_IN_CI_RE.match(ci_text)
    if not m:
        return

    hadith_num = m.group(1).strip()
    hadith_body = m.group(2).strip()

    ci_element.decompose()
    changes += 1

    ht = block.select_one('.hadith-text')
    if not ht:
        ref = block.select_one('.ref-info')
        ht = soup.new_tag('div', **{'class': 'hadith-text'})
        if ref:
            ref.insert_after(ht)
        else:
            block.append(ht)
        changes += 1

    if not ht.select_one('.hadith-number'):
        hn = soup.new_tag('span', **{'class': 'hadith-number'})
        hn.string = hadith_num
        ht.insert(0, hn)
        changes += 1

    p = soup.new_tag('p')
    p.string = hadith_body
    ht.append(p)
    changes += 1


def wrap_editorial_notes(soup):
    """Global pass: wrap unspanned editorial notes."""
    global changes
    for ht in soup.select('.hadith-text'):
        for p in ht.select('p'):
            txt = p.get_text(strip=True)
            if EDITORIAL_PATTERN.search(txt) and not p.select_one('.editorial-note'):
                p.clear()
                span = soup.new_tag('span', **{'class': 'editorial-note'})
                span.string = EDITORIAL_TEXT
                p.append(span)
                changes += 1


def process_file(path):
    global changes
    with open(path, encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    blocks = soup.select('.hadith-block')

    # -------------------------------------------------------------------------
    # File-specific fixes
    # -------------------------------------------------------------------------

    if path == 'Aqydatona/12Mutaah/1Bkhari.html':
        # b6: sn='صحيح البخاري -', bt='‏1693- حدثنا...' → extract num, move bt to ht
        b6 = blocks[5]
        bt6 = b6.select_one('.book-title')
        sn6 = b6.select_one('.scholar-name')
        if bt6 and not b6.select_one('.hadith-text'):
            bt6_txt = bt6.get_text(strip=True)
            num6 = re.match(r'[‏\s]*(\d+)\s*-', bt6_txt)
            if num6:
                hadith_num = num6.group(1)
                if sn6:
                    sn6.clear()
                    sn6.append('البخاري')
                    changes += 1
                bt6.clear()
                bt6.append('صحيح البخاري')
                changes += 1
                ht6 = soup.new_tag('div', **{'class': 'hadith-text'})
                hn6 = soup.new_tag('span', **{'class': 'hadith-number'})
                hn6.string = hadith_num
                ht6.append(hn6)
                p6 = soup.new_tag('p')
                p6.string = bt6_txt
                ht6.append(p6)
                ref6 = b6.select_one('.ref-info')
                if ref6:
                    ref6.insert_after(ht6)
                else:
                    b6.append(ht6)
                changes += 1

        # b12: sn='صحيح البخاري', bt='‏5203', ci='- حدثنا...' → num from bt, chain from ci
        b12 = blocks[11]
        bt12 = b12.select_one('.book-title')
        sn12 = b12.select_one('.scholar-name')
        if bt12 and not b12.select_one('.hadith-text'):
            num12_str = re.sub(r'[^\d]', '', bt12.get_text())
            if num12_str:
                if sn12:
                    sn12.clear()
                    sn12.append('البخاري')
                    changes += 1
                bt12.clear()
                bt12.append('صحيح البخاري')
                changes += 1
                ci12_list = b12.select('.chapter-info')
                ht12 = soup.new_tag('div', **{'class': 'hadith-text'})
                hn12 = soup.new_tag('span', **{'class': 'hadith-number'})
                hn12.string = num12_str
                ht12.append(hn12)
                if ci12_list:
                    chain12 = ci12_list[0].get_text(strip=True).lstrip('- ')
                    ci12_list[0].decompose()
                    changes += 1
                    p12 = soup.new_tag('p')
                    p12.string = chain12
                    ht12.append(p12)
                ref12 = b12.select_one('.ref-info')
                if ref12:
                    ref12.insert_after(ht12)
                else:
                    b12.append(ht12)
                changes += 1

    elif path == 'Aqydatona/2Adhaan.html':
        # b8: sn=editorial, bt='....' → use context (ابن حزم/المحلى بالآثار from b6/b7)
        b8 = blocks[7]
        sn8 = b8.select_one('.scholar-name')
        if sn8 and EDITORIAL_PATTERN.search(sn8.get_text()):
            sn8.clear()
            sn8.append('ابن حزم')
            changes += 1
            bt8 = b8.select_one('.book-title')
            if bt8:
                bt8.clear()
                bt8.append('المحلى بالآثار')
                changes += 1
            ensure_editorial_in_ht(b8, soup)

        # b9: sn='المتقي الهندي -...', bt='23174-', no ht
        b9 = blocks[8]
        sn9 = b9.select_one('.scholar-name')
        bt9 = b9.select_one('.book-title')
        if sn9 and bt9 and not b9.select_one('.hadith-text'):
            sn9_txt = sn9.get_text(strip=True)
            bt9_txt = bt9.get_text(strip=True)
            if '-' in sn9_txt and re.match(r'[‏\s]*\d+', bt9_txt):
                m = re.match(r'^([^-]+?)\s*-+\s*(.+)', sn9_txt, re.DOTALL)
                if m:
                    scholar9 = m.group(1).strip()
                    book9 = m.group(2).strip()
                    num9 = re.sub(r'[^\d]', '', bt9_txt)
                    sn9.clear()
                    sn9.append(scholar9)
                    changes += 1
                    bt9.clear()
                    bt9.append(book9)
                    changes += 1
                    ht9 = soup.new_tag('div', **{'class': 'hadith-text'})
                    if num9:
                        hn9 = soup.new_tag('span', **{'class': 'hadith-number'})
                        hn9.string = num9
                        ht9.append(hn9)
                    ref9 = b9.select_one('.ref-info')
                    if ref9:
                        ref9.insert_after(ht9)
                    else:
                        b9.append(ht9)
                    changes += 1

    elif path == 'Aqydatona/10Twassol/5IStsqa.html':
        # b10: sn='محمود سعيد ممدوح', bt='[النص طويل...]' → fix bt, global pass handles ci
        b10 = blocks[9]
        bt10 = b10.select_one('.book-title')
        if bt10 and EDITORIAL_PATTERN.search(bt10.get_text()):
            bt10.clear()
            bt10.append('رفع المنارة')
            changes += 1

    elif path == 'Aqydatona/17Laen/7.html':
        # b2: sn='ابن أبي الحديد', bt=text → move bt to hadith-text
        b2 = blocks[1]
        bt2 = b2.select_one('.book-title')
        if bt2 and not b2.select_one('.hadith-text'):
            bt2_txt = bt2.get_text(strip=True)
            if bt2_txt and bt2_txt != 'شرح نهج البلاغة':
                bt2.clear()
                bt2.append('شرح نهج البلاغة')
                changes += 1
                ht2 = soup.new_tag('div', **{'class': 'hadith-text'})
                p2 = soup.new_tag('p')
                p2.string = bt2_txt
                ht2.append(p2)
                ref2 = b2.select_one('.ref-info')
                if ref2:
                    ref2.insert_after(ht2)
                else:
                    b2.append(ht2)
                changes += 1

    elif path == 'Aqydatona/12Mutaah/6IbiDawood.html':
        # b1/b2: sn=number, bt=chain — whole file is from سنن أبي داود
        for idx in [0, 1]:
            if idx < len(blocks):
                b = blocks[idx]
                sn = b.select_one('.scholar-name')
                if sn and not b.select_one('.hadith-text'):
                    sn_stripped = sn.get_text(strip=True).strip('‏ ')
                    if sn_stripped.isdigit():
                        fix_sn_number_bt_text(b, soup, 'أبو داود', 'سنن أبي داود', sn_stripped)

    elif path == 'Aqydatona/15Bkaa/6Saad2.html':
        # b1/b2: no context in file, both are from صحيح مسلم
        for idx in [0, 1]:
            b = blocks[idx]
            sn = b.select_one('.scholar-name')
            if sn and not b.select_one('.hadith-text'):
                sn_stripped = sn.get_text(strip=True).strip('‏ ')
                if sn_stripped.isdigit():
                    fix_sn_number_bt_text(b, soup, 'مسلم', 'صحيح مسلم', sn_stripped)

    elif path == 'Aqydatona/9Tbarrok/4Lbas.html':
        # b1: first block, next is أحمد بن حنبل - but b1 is from صحيح مسلم
        b1 = blocks[0]
        sn1 = b1.select_one('.scholar-name')
        if sn1 and not b1.select_one('.hadith-text'):
            sn1_stripped = sn1.get_text(strip=True).strip('‏ ')
            if sn1_stripped.isdigit():
                fix_sn_number_bt_text(b1, soup, 'مسلم', 'صحيح مسلم', sn1_stripped)

    # -------------------------------------------------------------------------
    # Global pass: fix EDITORIAL_SN blocks
    # -------------------------------------------------------------------------
    for i, b in enumerate(blocks):
        sn = b.select_one('.scholar-name')
        if sn and EDITORIAL_PATTERN.search(sn.get_text()):
            fix_editorial_sn_block(b, soup, blocks, i)

    # -------------------------------------------------------------------------
    # Global pass: fix sn=number + bt=chain inversions (context propagation)
    # -------------------------------------------------------------------------
    propagate_scholar_book(soup, blocks)

    # -------------------------------------------------------------------------
    # Global pass: fix HADITH_IN_CI for blocks without hadith-text
    # -------------------------------------------------------------------------
    for b in soup.select('.hadith-block'):
        if b.select_one('.hadith-text'):
            continue
        for ci in b.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b, soup, ci)
                break

    # -------------------------------------------------------------------------
    # Global pass: wrap unspanned editorial notes
    # -------------------------------------------------------------------------
    wrap_editorial_notes(soup)

    new_content = str(soup)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Updated: {path}")
    else:
        print(f"  No changes: {path}")


def main():
    global changes
    paths = sorted(
        glob.glob('Aqydatona/**/*.html', recursive=True) + glob.glob('Aqydatona/*.html')
    )
    seen = set()
    paths = [p for p in paths if not (p in seen or seen.add(p))]

    for path in paths:
        if 'Main' in path:
            continue
        prev = changes
        process_file(path)
        delta = changes - prev
        if delta:
            print(f"    {delta} changes")

    print(f"\nTotal changes: {changes}")


if __name__ == '__main__':
    main()
