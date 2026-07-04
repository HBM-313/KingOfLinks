#!/usr/bin/env python3
"""Cleanup script for SwR folder - fix all data quality issues."""

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
    'صحيحمسلم': 'مسلم',
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
    'كنز العمال في سنن الأقوال والأفعال': 'المتقي الهندي',
}

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
    'ابن عساكر': 'تاريخ دمشق',
    'الذهبي': 'سير أعلام النبلاء',
    'ابن حزم': 'المحلى بالآثار',
    'ابن حجر العسقلاني': 'فتح الباري',
    'ابن حجر الهيتمي': 'تحفة المحتاج',
    'ابن نجيم': 'البحر الرائق',
    'العيني': 'عمدة القاري',
    'سيد سابق': 'فقه السنة',
    'المارديني': 'الجوهر النقي',
    'ابن المنذر': 'الإشراف',
    'المناوي': 'فيض القدير',
    'ابن رجب الحنبلي': 'فتح الباري',
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

    if sn_clean in BOOK_TO_SCHOLAR:
        return BOOK_TO_SCHOLAR[sn_clean], sn_clean, None

    if '-' in sn_txt:
        m = re.match(r'^([^-]+?)\s*-+\s*(.+)', sn_txt, re.DOTALL)
        if m:
            scholar = m.group(1).strip()
            rest = m.group(2).strip()
            ch_m = CHAPTER_SPLIT_RE.search(rest)
            book = rest[:ch_m.start()].strip() if ch_m else rest.rstrip('- ').strip()
            return scholar, book or bt_txt, None

    if bt_txt in BOOK_TO_SCHOLAR:
        return BOOK_TO_SCHOLAR[bt_txt], bt_txt, None

    if '-' in bt_txt:
        m = re.match(r'^([^-]+?)\s*-+\s*(.+)', bt_txt, re.DOTALL)
        if m:
            scholar = m.group(1).strip()
            rest = m.group(2).strip()
            ch_m = CHAPTER_SPLIT_RE.search(rest)
            book = rest[:ch_m.start()].strip() if ch_m else rest.rstrip('- ').strip()
            return scholar, book or sn_txt, None

    scholar = bt_txt or sn_clean
    if ci_texts:
        ci_raw = ci_texts[0].lstrip('- ')
        if not CHAPTER_STARTS_RE.match(ci_raw.strip()):
            ch_m = CHAPTER_SPLIT_RE.search(ci_raw)
            if ch_m:
                book = ci_raw[:ch_m.start()].strip()
                return scholar, book, '- ' + ci_raw[ch_m.start():].lstrip('- ').strip()
            else:
                parts = re.split(r'\s*-+\s*', ci_raw, 1)
                if len(parts) > 1:
                    return scholar, parts[0].strip(), '- ' + parts[1].strip()

    book = AUTHOR_TO_BOOK.get(scholar, scholar)
    return scholar, book, None


def get_nearby_context(blocks, idx):
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
            if s:
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
            if s:
                return s, b
    return None, None


def fix_editorial_sn_block(block, soup, blocks=None, block_idx=None):
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not sn:
        return

    bt_text = bt.get_text(strip=True) if bt else ''
    ci_elements = block.select('.chapter-info')
    ci_texts = [c.get_text(strip=True) for c in ci_elements]

    if not bt_text or re.match(r'^[.\s]+$', bt_text):
        scholar, book = None, None
        if blocks and block_idx is not None:
            scholar, book = get_nearby_context(blocks, block_idx)
        scholar = scholar or '?'
        book = book or '?'
        new_ci0 = None
    else:
        scholar, book, new_ci0 = parse_scholar_book_from_sn_bt(bt_text, '', ci_texts)

    if new_ci0 and ci_elements:
        ci_elements[0].clear()
        ci_elements[0].append(new_ci0)
        changes += 1

    sn_text = sn.get_text(strip=True)
    if sn_text != scholar:
        sn.clear()
        sn.append(scholar)
        changes += 1

    if bt and bt_text != book:
        bt.clear()
        bt.append(book)
        changes += 1

    ensure_editorial_in_ht(block, soup)


def fix_sn_number_bt_text(block, soup, scholar, book, hadith_num):
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
    global changes

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
        if scholar:
            contexts[i] = (scholar, book)

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

        for ci in b.select('.chapter-info'):
            ci_txt = ci.get_text(strip=True).lstrip('- ')
            ch_m = CHAPTER_SPLIT_RE.search(ci_txt)
            if ch_m:
                potential_book = ci_txt[:ch_m.start()].strip()
                if potential_book and potential_book in BOOK_TO_SCHOLAR and not CHAPTER_STARTS_RE.match(potential_book):
                    scholar = BOOK_TO_SCHOLAR[potential_book]
                    book = potential_book
                    break

        if not scholar:
            for j in range(i - 1, -1, -1):
                if j in contexts:
                    scholar, book = contexts[j]
                    break
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

    if path == 'SwR/2Elaqah/8Khafq.html':
        # b1: sn=num=2870, context doesn't propagate correctly (next is أحمد بن حنبل)
        # Chapter 'كتاب الجنة وصفة نعيمها وأهلها' is صحيح مسلم
        b1 = blocks[0]
        sn1 = b1.select_one('.scholar-name')
        if sn1 and not b1.select_one('.hadith-text'):
            num1 = sn1.get_text(strip=True).strip('‏ ')
            if num1.isdigit():
                fix_sn_number_bt_text(b1, soup, 'مسلم', 'صحيح مسلم', num1)

    # -------------------------------------------------------------------------
    # Global pass: fix EDITORIAL_SN blocks
    # -------------------------------------------------------------------------
    for i, b in enumerate(blocks):
        sn = b.select_one('.scholar-name')
        if sn and EDITORIAL_PATTERN.search(sn.get_text()):
            fix_editorial_sn_block(b, soup, blocks, i)

    # -------------------------------------------------------------------------
    # Global pass: fix sn=number + bt=chain inversions
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
        glob.glob('SwR/**/*.html', recursive=True) + glob.glob('SwR/*.html')
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
