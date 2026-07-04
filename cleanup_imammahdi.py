#!/usr/bin/env python3
"""Cleanup script for ImamMahdi folder."""

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
    'سنن أبي داود': 'أبو داود',
    'سنن الترمذي': 'الترمذي',
    'سنن ابن ماجه': 'ابن ماجه',
    'السنن الكبرى': 'البيهقي',
    'المستدرك على الصحيحين': 'الحاكم النيسابوري',
    'مجمع الزوائد ومنبع الفوائد': 'الهيثمي',
    'مسند الامام أحمد بن حنبل': 'أحمد بن حنبل',
    'صحيح ابن حبان': 'ابن حبان',
    'المعجم الكبير': 'الطبراني',
    'الجامع الصغير وزيادته': 'السيوطي',
    'الدر المنثور في التفسير بالمأثور': 'السيوطي',
    'كنز العمال في سنن الأقوال والأفعال': 'المتقي الهندي',
    'ينابيع المودة لذوي القربى': 'القندوزي',
}

AUTHOR_TO_BOOK = {
    'الطبراني': 'المعجم الكبير',
    'الهيثمي': 'مجمع الزوائد ومنبع الفوائد',
    'البيهقي': 'السنن الكبرى',
    'ابن حجر العسقلاني': 'فتح الباري',
    'النووي': 'شرح مسلم',
    'السيوطي': 'الجامع الصغير وزيادته',
    'ابن ماجه': 'سنن ابن ماجه',
    'العيني': 'عمدة القاري',
    'القندوزي': 'ينابيع المودة لذوي القربى',
    'السيد أبو الحسن اليماني الصنعاني': 'أبواب الهدى',
    'جمال الدين الحسيني المعروف ( بابن عنبه )': 'عمدة الطالب',
    'العلامة عبد الله الشبراوي الشافعي': 'الإتحاف بحب الأشراف',
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
        if not any(p.select_one('.editorial-note') or EDITORIAL_PATTERN.search(p.get_text())
                   for p in ht.select('p')):
            ht.insert(0, make_editorial_p(soup))
            changes += 1
    else:
        ref = block.select_one('.ref-info')
        ht_div = soup.new_tag('div', **{'class': 'hadith-text'})
        ht_div.append(make_editorial_p(soup))
        (ref.insert_after(ht_div) if ref else block.append(ht_div))
        changes += 1


def parse_scholar_book(bt_text, ci_texts=None):
    """Parse scholar/book from bt field. Return (scholar, book, new_ci0)."""
    bt_clean = bt_text.rstrip('- ')
    if bt_clean in BOOK_TO_SCHOLAR:
        return BOOK_TO_SCHOLAR[bt_clean], bt_clean, None
    if '-' in bt_text:
        m = re.match(r'^([^-]+?)\s*-+\s*(.+)', bt_text, re.DOTALL)
        if m:
            scholar = m.group(1).strip()
            rest = m.group(2).strip()
            ch_m = CHAPTER_SPLIT_RE.search(rest)
            book = rest[:ch_m.start()].strip() if ch_m else rest.rstrip('- ')
            return scholar, book or bt_text, None
    scholar = bt_text
    if ci_texts:
        ci_raw = ci_texts[0].lstrip('- ')
        if not CHAPTER_STARTS_RE.match(ci_raw.strip()):
            ch_m = CHAPTER_SPLIT_RE.search(ci_raw)
            if ch_m:
                book = ci_raw[:ch_m.start()].strip()
                return scholar, book, '- ' + ci_raw[ch_m.start():].lstrip('- ').strip()
            parts = re.split(r'\s*-+\s*', ci_raw, 1)
            if len(parts) > 1:
                return scholar, parts[0].strip(), '- ' + parts[1].strip()
    return scholar, AUTHOR_TO_BOOK.get(scholar, scholar), None


def fix_editorial_sn_block(block, soup):
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not sn or not bt:
        return
    bt_text = bt.get_text(strip=True)
    ci_texts = [c.get_text(strip=True) for c in block.select('.chapter-info')]
    scholar, book, new_ci0 = parse_scholar_book(bt_text, ci_texts)
    if new_ci0:
        ci_els = block.select('.chapter-info')
        if ci_els:
            ci_els[0].clear()
            ci_els[0].append(new_ci0)
            changes += 1
    sn.clear()
    sn.append(scholar)
    changes += 1
    if bt_text != book:
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
    if sn:
        sn.clear()
        sn.append(scholar)
        changes += 1
    bt.clear()
    bt.append(book)
    changes += 1
    ht = block.select_one('.hadith-text')
    if not ht:
        ref = block.select_one('.ref-info')
        ht = soup.new_tag('div', **{'class': 'hadith-text'})
        (ref.insert_after(ht) if ref else block.append(ht))
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
        if (sn_stripped.isdigit() or sn_txt.startswith('.') or not sn_txt
                or EDITORIAL_PATTERN.search(sn_txt)
                or sn_txt in ('المصادر :', 'المصدر :')):
            continue
        s, bk, _ = parse_scholar_book(sn_txt, [bt_txt] if bt_txt else None)
        # use sn as scholar if bt is clearly the book title
        if sn_txt != s:
            # parse_scholar_book used sn_txt as scholar (Pattern A)
            pass
        # Store as sn=scholar, bt=book
        scholar_ctx = sn_txt.rstrip('- ')
        book_ctx = bt_txt
        if scholar_ctx in BOOK_TO_SCHOLAR:
            scholar_ctx = BOOK_TO_SCHOLAR[scholar_ctx]
            book_ctx = sn_txt.rstrip('- ')
        elif '-' in sn_txt:
            m = re.match(r'^([^-]+?)\s*-+\s*(.+)', sn_txt, re.DOTALL)
            if m:
                scholar_ctx = m.group(1).strip()
                book_ctx = m.group(2).rstrip('- ').strip() or bt_txt
        contexts[i] = (scholar_ctx, book_ctx)

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
        bt_is_chain = len(bt_txt) > 30 and ('حدثنا' in bt_txt or 'أخبرنا' in bt_txt or 'قال' in bt_txt)
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
            print('  WARNING: no context at block ' + str(i + 1))
            continue
        fix_sn_number_bt_text(b, soup, scholar, book, sn_stripped)


def fix_hadith_in_ci(block, soup, ci_element):
    global changes
    m = HADITH_IN_CI_RE.match(ci_element.get_text(strip=True))
    if not m:
        return
    hadith_num, hadith_body = m.group(1).strip(), m.group(2).strip()
    ci_element.decompose()
    changes += 1
    ht = block.select_one('.hadith-text')
    if not ht:
        ref = block.select_one('.ref-info')
        ht = soup.new_tag('div', **{'class': 'hadith-text'})
        (ref.insert_after(ht) if ref else block.append(ht))
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
            if EDITORIAL_PATTERN.search(p.get_text()) and not p.select_one('.editorial-note'):
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

    if path == 'ImamMahdi/3Mna/26Qndoozi.html':
        # b16: sn='القندوزي', bt=text content → bt='ينابيع المودة', move bt to hadith-text
        b16 = blocks[15] if len(blocks) > 15 else None
        if b16 and not b16.select_one('.hadith-text'):
            bt16 = b16.select_one('.book-title')
            if bt16:
                bt16_txt = bt16.get_text(strip=True)
                if bt16_txt and 'وفيه' in bt16_txt:
                    bt16.clear()
                    bt16.append('ينابيع المودة لذوي القربى')
                    changes += 1
                    ht16 = soup.new_tag('div', **{'class': 'hadith-text'})
                    p16 = soup.new_tag('p')
                    p16.string = bt16_txt
                    ht16.append(p16)
                    ref16 = b16.select_one('.ref-info')
                    (ref16.insert_after(ht16) if ref16 else b16.append(ht16))
                    changes += 1

    # Global: fix EDITORIAL_SN
    for b in blocks:
        sn = b.select_one('.scholar-name')
        if sn and EDITORIAL_PATTERN.search(sn.get_text()):
            fix_editorial_sn_block(b, soup)

    # Global: propagate scholar/book for sn=number blocks
    propagate_scholar_book(soup, blocks)

    # Global: fix HADITH_IN_CI
    for b in soup.select('.hadith-block'):
        if b.select_one('.hadith-text'):
            continue
        for ci in b.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b, soup, ci)
                break

    # Global: wrap editorial notes
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
        glob.glob('ImamMahdi/**/*.html', recursive=True) + glob.glob('ImamMahdi/*.html')
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
