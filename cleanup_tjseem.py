#!/usr/bin/env python3
"""Cleanup script for Tjseem folder - fix all data quality issues."""

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
    r'القسم|النوع|الفصل|الباب)',
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
    'البداية والنهاية': 'ابن كثير',
    'تاريخ دمشق': 'ابن عساكر',
    'سير أعلام النبلاء': 'الذهبي',
}

changes = 0


def make_editorial_p(soup):
    p = soup.new_tag('p')
    span = soup.new_tag('span', **{'class': 'editorial-note'})
    span.string = EDITORIAL_TEXT
    p.append(span)
    return p


def ensure_editorial_in_ht(block, soup):
    """Add editorial note to hadith-text if missing, create ht div if absent."""
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


def fix_editorial_sn_block(block, soup):
    """Fix EDITORIAL_SN block: parse scholar/book, update sn+bt, add editorial note."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not sn or not bt:
        return

    bt_text = bt.get_text(strip=True)
    ci_elements = block.select('.chapter-info')
    ci_texts = [c.get_text(strip=True) for c in ci_elements]

    scholar = None
    book = None
    new_ci0 = None

    # Pattern C: bt is a known book title → infer scholar
    if bt_text in BOOK_TO_SCHOLAR:
        scholar = BOOK_TO_SCHOLAR[bt_text]
        book = bt_text

    # Pattern B: bt has dash → "scholar - book [- chapter...]"
    elif '-' in bt_text:
        m = re.match(r'^([^-]+?)\s*-+\s*(.+)', bt_text, re.DOTALL)
        if m:
            scholar = m.group(1).strip()
            rest = m.group(2).strip()
            ch_m = CHAPTER_SPLIT_RE.search(rest)
            book = rest[:ch_m.start()].strip() if ch_m else rest
        else:
            scholar = bt_text
            book = bt_text

    # Pattern A: bt=scholar, get book from first chapter-info
    else:
        scholar = bt_text
        if ci_texts:
            ci_raw = ci_texts[0].lstrip('- ')
            ch_m = CHAPTER_SPLIT_RE.search(ci_raw)
            if ch_m:
                book = ci_raw[:ch_m.start()].strip()
                new_ci0 = '- ' + ci_raw[ch_m.start():].lstrip('- ').strip()
            else:
                parts = re.split(r'\s*-+\s*', ci_raw, 1)
                book = parts[0].strip()
                new_ci0 = '- ' + parts[1].strip() if len(parts) > 1 else None
        else:
            book = bt_text

    # Update scholar-name
    sn_text = sn.get_text(strip=True)
    if sn_text != scholar:
        sn.clear()
        sn.append(scholar)
        changes += 1

    # Update book-title
    if bt_text != book:
        bt.clear()
        bt.append(book)
        changes += 1

    # Update first chapter-info if needed (Pattern A stripped book prefix)
    if new_ci0 and ci_elements:
        ci_elements[0].clear()
        ci_elements[0].append(new_ci0)
        changes += 1

    ensure_editorial_in_ht(block, soup)


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


def move_bt_to_ht(block, soup, scholar, book, hadith_num):
    """Move bt content (hadith text) to hadith-text div; set sn=scholar, bt=book."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not bt:
        return

    hadith_body = bt.get_text(strip=True)

    # Fix scholar-name
    if sn:
        sn.clear()
        sn.append(scholar)
        changes += 1

    # Fix book-title
    bt.clear()
    bt.append(book)
    changes += 1

    # Create hadith-text
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

    if path == 'Tjseem/1ShabAmrad.html':
        # b21/b22/b23: sn=editorial note, bt='السيوطي'
        # scholar=السيوطي, book=اللآلي المصنوعة في الأحاديث الموضوعة
        for idx in [20, 21, 22]:
            if idx < len(blocks):
                b = blocks[idx]
                sn = b.select_one('.scholar-name')
                if sn and EDITORIAL_PATTERN.search(sn.get_text()):
                    fix_editorial_sn_block(b, soup)

    elif path == 'Tjseem/2Atraf.html':
        # b19: sn=editorial, bt='الحاكم النيسابوري', ci='- المستدرك...'
        b19 = blocks[18]
        sn19 = b19.select_one('.scholar-name')
        if sn19 and EDITORIAL_PATTERN.search(sn19.get_text()):
            fix_editorial_sn_block(b19, soup)

    elif path == 'Tjseem/3Hyah.html':
        # b13: sn='الترمذي', bt='‏3279' (hadith num), ci='- حدثنا...' (chain)
        b13 = blocks[12]
        bt13 = b13.select_one('.book-title')
        sn13 = b13.select_one('.scholar-name')
        if bt13 and sn13 and not b13.select_one('.hadith-text'):
            num_text = re.sub(r'[^\d]', '', bt13.get_text())
            # Fix book-title to proper book name
            bt13.clear()
            bt13.append('سنن الترمذي')
            changes += 1
            # Move first chapter-info (chain) to hadith-text
            ci_list = b13.select('.chapter-info')
            if ci_list:
                ci = ci_list[0]
                chain_text = ci.get_text(strip=True).lstrip('- ')
                ci.decompose()
                changes += 1
                ref13 = b13.select_one('.ref-info')
                ht13 = soup.new_tag('div', **{'class': 'hadith-text'})
                if num_text:
                    hn = soup.new_tag('span', **{'class': 'hadith-number'})
                    hn.string = num_text
                    ht13.append(hn)
                p13 = soup.new_tag('p')
                p13.string = chain_text
                ht13.append(p13)
                if ref13:
                    ref13.insert_after(ht13)
                else:
                    b13.append(ht13)
                changes += 1

    elif path == 'Tjseem/4Yad.html':
        # b1: sn=editorial, bt='صحيح البخاري' (Pattern C)
        b1 = blocks[0]
        sn1 = b1.select_one('.scholar-name')
        if sn1 and EDITORIAL_PATTERN.search(sn1.get_text()):
            fix_editorial_sn_block(b1, soup)

        # b6/b7/b8: sn=number (2654/2786/2788), bt=hadith chain → scholar=مسلم
        for idx, num in [(5, '2654'), (6, '2786'), (7, '2788')]:
            if idx < len(blocks):
                b = blocks[idx]
                sn = b.select_one('.scholar-name')
                if sn:
                    sn_txt = re.sub(r'[^\d]', '', sn.get_text())
                    if sn_txt in (num, num.strip()):
                        move_bt_to_ht(b, soup, 'مسلم', 'صحيح مسلم', sn_txt)

    elif path == 'Tjseem/9Ydhak.html':
        # b2: sn=editorial, bt='صحيح مسلم' (Pattern C)
        b2 = blocks[1]
        sn2 = b2.select_one('.scholar-name')
        if sn2 and EDITORIAL_PATTERN.search(sn2.get_text()):
            fix_editorial_sn_block(b2, soup)

    # -------------------------------------------------------------------------
    # Global pass: fix any remaining EDITORIAL_SN blocks
    # -------------------------------------------------------------------------
    for b in soup.select('.hadith-block'):
        sn = b.select_one('.scholar-name')
        if sn and EDITORIAL_PATTERN.search(sn.get_text()):
            fix_editorial_sn_block(b, soup)

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
        glob.glob('Tjseem/*.html') + glob.glob('Tjseem/**/*.html', recursive=True)
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
