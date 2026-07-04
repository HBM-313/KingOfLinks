#!/usr/bin/env python3
"""Cleanup script for ImamHussain folder."""

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
    'تهذيب الكمال في أسماء الرجال': 'المزي',
    'تهذيب التهذيب': 'ابن حجر العسقلاني',
    'فضائل الصحابة': 'أحمد بن حنبل',
}

AUTHOR_TO_BOOK = {
    'الطبراني': 'المعجم الكبير',
    'الهيثمي': 'مجمع الزوائد ومنبع الفوائد',
    'البيهقي': 'السنن الكبرى',
    'ابن حجر العسقلاني': 'فتح الباري',
    'المزي': 'تهذيب الكمال في أسماء الرجال',
    'النووي': 'شرح مسلم',
    'الذهبي': 'سير أعلام النبلاء',
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
            ep = make_editorial_p(soup)
            ht.insert(0, ep)
            changes += 1
    else:
        ref = block.select_one('.ref-info')
        ht_div = soup.new_tag('div', **{'class': 'hadith-text'})
        ht_div.append(make_editorial_p(soup))
        (ref.insert_after(ht_div) if ref else block.append(ht_div))
        changes += 1


def fix_editorial_sn_block(block, soup):
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not sn or not bt:
        return
    bt_text = bt.get_text(strip=True)
    ci_texts = [c.get_text(strip=True) for c in block.select('.chapter-info')]

    scholar, book, new_ci0 = None, None, None

    bt_clean = bt_text.rstrip('- ')
    if bt_clean in BOOK_TO_SCHOLAR:
        scholar, book = BOOK_TO_SCHOLAR[bt_clean], bt_clean
    elif '-' in bt_text:
        m = re.match(r'^([^-]+?)\s*-+\s*(.+)', bt_text, re.DOTALL)
        if m:
            scholar = m.group(1).strip()
            rest = m.group(2).strip()
            ch_m = CHAPTER_SPLIT_RE.search(rest)
            book = rest[:ch_m.start()].strip() if ch_m else rest.rstrip('- ')
    else:
        scholar = bt_text
        if ci_texts:
            ci_raw = ci_texts[0].lstrip('- ')
            if not CHAPTER_STARTS_RE.match(ci_raw.strip()):
                ch_m = CHAPTER_SPLIT_RE.search(ci_raw)
                if ch_m:
                    book = ci_raw[:ch_m.start()].strip()
                    new_ci0 = '- ' + ci_raw[ch_m.start():].lstrip('- ').strip()
        if not book:
            book = AUTHOR_TO_BOOK.get(scholar, scholar)

    if new_ci0:
        ci_els = block.select('.chapter-info')
        if ci_els:
            ci_els[0].clear()
            ci_els[0].append(new_ci0)
            changes += 1

    sn.clear()
    sn.append(scholar or bt_text)
    changes += 1
    if bt_text != book:
        bt.clear()
        bt.append(book or bt_text)
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

    if path == 'ImamHussain/1Hob.html':
        # b13: sn=num=143, bt=chain → from سنن ابن ماجه (same hadith as ImamHasan)
        b13 = blocks[12] if len(blocks) > 12 else None
        if b13:
            sn13 = b13.select_one('.scholar-name')
            if sn13 and not b13.select_one('.hadith-text'):
                num = sn13.get_text(strip=True).strip('‏ ')
                if num.isdigit():
                    fix_sn_number_bt_text(b13, soup, 'ابن ماجه', 'سنن ابن ماجه', num)

    elif path == 'ImamHussain/9Estshhadoh/1IbnHanbal.html':
        # b8: sn='أحمد بن حنبل-فضائل الصحابة-...', bt='1170- chain'
        b8 = blocks[7] if len(blocks) > 7 else None
        if b8 and not b8.select_one('.hadith-text'):
            sn8 = b8.select_one('.scholar-name')
            bt8 = b8.select_one('.book-title')
            if sn8 and bt8:
                sn8_txt = sn8.get_text(strip=True)
                bt8_txt = bt8.get_text(strip=True)
                # Extract num from bt start
                num_m = re.match(r'[‏\s]*(\d+)\s*-\s*(.*)', bt8_txt, re.DOTALL)
                if num_m:
                    num8 = num_m.group(1)
                    chain8 = num_m.group(2).strip()
                    # Fix sn: extract scholar from combined sn
                    parts = sn8_txt.split('-', 1)
                    scholar8 = parts[0].strip()
                    book8 = 'فضائل الصحابة'
                    sn8.clear()
                    sn8.append(scholar8)
                    changes += 1
                    bt8.clear()
                    bt8.append(book8)
                    changes += 1
                    ht8 = soup.new_tag('div', **{'class': 'hadith-text'})
                    hn8 = soup.new_tag('span', **{'class': 'hadith-number'})
                    hn8.string = num8
                    ht8.append(hn8)
                    p8 = soup.new_tag('p')
                    p8.string = chain8
                    ht8.append(p8)
                    ref8 = b8.select_one('.ref-info')
                    (ref8.insert_after(ht8) if ref8 else b8.append(ht8))
                    changes += 1

    # Global passes
    for i, b in enumerate(blocks):
        sn = b.select_one('.scholar-name')
        if sn and EDITORIAL_PATTERN.search(sn.get_text()):
            fix_editorial_sn_block(b, soup)

    for b in soup.select('.hadith-block'):
        if b.select_one('.hadith-text'):
            continue
        for ci in b.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b, soup, ci)
                break

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
        glob.glob('ImamHussain/**/*.html', recursive=True) + glob.glob('ImamHussain/*.html')
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
