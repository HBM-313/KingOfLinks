#!/usr/bin/env python3
"""Cleanup script for ImamHasan folder."""

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
}

AUTHOR_TO_BOOK = {
    'الطبراني': 'المعجم الكبير',
    'الهيثمي': 'مجمع الزوائد ومنبع الفوائد',
    'البيهقي': 'السنن الكبرى',
    'المباركفوري': 'تحفة الأحوذي',
    'النووي': 'شرح مسلم',
    'ابن حجر العسقلاني': 'فتح الباري',
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

    scholar = bt_text
    book = AUTHOR_TO_BOOK.get(scholar, scholar)
    new_ci0 = None

    if ci_texts:
        ci_raw = ci_texts[0].lstrip('- ')
        if not CHAPTER_STARTS_RE.match(ci_raw.strip()):
            ch_m = CHAPTER_SPLIT_RE.search(ci_raw)
            if ch_m:
                book = ci_raw[:ch_m.start()].strip()
                new_ci0 = '- ' + ci_raw[ch_m.start():].lstrip('- ').strip()

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

    if path == 'ImamHasan/1Hob.html':
        # b24/b25: sn=num(142/143), bt=chain, from سنن ابن ماجه (كتاب المقدمة)
        for idx in [23, 24]:
            if idx < len(blocks):
                b = blocks[idx]
                sn = b.select_one('.scholar-name')
                if sn and not b.select_one('.hadith-text'):
                    num = sn.get_text(strip=True).strip('‏ ')
                    if num.isdigit():
                        fix_sn_number_bt_text(b, soup, 'ابن ماجه', 'سنن ابن ماجه', num)

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
        glob.glob('ImamHasan/**/*.html', recursive=True) + glob.glob('ImamHasan/*.html')
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
