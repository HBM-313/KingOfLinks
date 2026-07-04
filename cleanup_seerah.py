#!/usr/bin/env python3
"""Cleanup script for Seerah folder - fix all data quality issues."""

import glob
import re
from bs4 import BeautifulSoup, Tag

EDITORIAL_TEXT = 'النص طويل لذا استقطع منه موضع الشاهد'
EDITORIAL_PATTERN = re.compile(
    r'\[?\s*النص طويل\s*(?:جدا\s*)?لذا استقطع منه موضع الشاهد\s*\]?'
)
HADITH_IN_CI_RE = re.compile(r'^-\s*(\d+)\s*-\s*(.{10,})', re.DOTALL)
REF_RE = re.compile(r'(?:الجزء|رقم الصفحة)\s*[::(]', re.IGNORECASE)

changes = 0


def make_editorial_p(soup):
    p = soup.new_tag('p')
    span = soup.new_tag('span', **{'class': 'editorial-note'})
    span.string = EDITORIAL_TEXT
    p.append(span)
    return p


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


def ensure_editorial_in_ht(block, soup):
    """Add editorial note to hadith-text if missing; create ht div if needed."""
    global changes
    ht = block.select_one('.hadith-text')
    if ht:
        has_editorial = any(
            p.select_one('.editorial-note') or EDITORIAL_PATTERN.search(p.get_text())
            for p in ht.select('p')
        )
        if not has_editorial:
            ht.insert(0, make_editorial_p(soup))
            changes += 1
    else:
        ref = block.select_one('.ref-info')
        ht_div = soup.new_tag('div', **{'class': 'hadith-text'})
        ht_div.append(make_editorial_p(soup))
        if ref:
            ref.insert_after(ht_div)
        else:
            block.append(ht_div)
        changes += 1


def fix_typos(text):
    text = re.sub(r'مجمعالزوائد', 'مجمع الزوائد', text)
    text = re.sub(r'مجمعالأمثال', 'مجمع الأمثال', text)
    text = re.sub(r'معجمما', 'معجم ما', text)
    text = re.sub(r'تنويرالحوالك', 'تنوير الحوالك', text)
    return text


def parse_scholar_book(bt_text, ci_texts):
    """Extract (scholar, book, updated_ci0) from bt and ci fields.

    Returns (scholar, book, new_chapter_for_ci0) where new_chapter_for_ci0
    is the chapter text to replace ci0 with (None = leave ci unchanged).
    """
    CHAPTER_PAT = re.compile(
        r'\s*-+\s*(?:كتاب|باب|فصل|حرف|الطبقة|المجلد|من اسمه|تتمة|تراجم|سنة'
        r'|عدد|مسائل|مناقب|سورة|شرح|صفة|ذكر|الصاد|الجيم|العين|التاء|اللام'
        r'|الياء|الهاء|الشين|الراء|القاف|الفاء|الغين|الخاء|الثاء|الباء|الألف'
        r'|ج\s*\d|أمر\s|تتمة\s)',
        re.IGNORECASE
    )

    scholar = ''
    book = ''
    new_ci0 = None

    # Parse from bt
    bt = bt_text.strip()
    m = re.match(r'^([^-]+?)\s*-+\s*(.+)$', bt, re.DOTALL)
    if m:
        scholar = m.group(1).strip()
        rest = m.group(2).strip()
        # Try to find where book ends and chapter begins
        ch_m = CHAPTER_PAT.search(rest)
        if ch_m:
            book = fix_typos(rest[:ch_m.start()].strip())
            chapter_part = rest[ch_m.start():].strip().lstrip('- ')
            # This chapter came from bt — we'll create a new ci for it if no ci exists
            new_ci0 = '- ' + chapter_part
        else:
            book = fix_typos(rest)
    else:
        scholar = bt

    # If no book yet, look in ci1
    if not book and ci_texts:
        ci_txt = ci_texts[0].lstrip('- ')
        # Split on first '-' (either ' - ' or '-') to separate book from chapter
        parts = re.split(r'\s*-+\s*', ci_txt, 1)
        if len(parts) == 2:
            book = fix_typos(parts[0].strip())
            new_ci0 = '- ' + parts[1].strip()
        else:
            book = fix_typos(ci_txt)

    return scholar, book, new_ci0


def fix_editorial_sn_block(block, soup):
    """Auto-detect scholar/book from bt+ci and fix editorial-note in scholar-name."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not sn or not bt:
        return

    bt_text = bt.get_text(strip=True)
    cis = block.select('.chapter-info')
    ci_texts = [ci.get_text(strip=True).lstrip('- ') for ci in cis]

    scholar, book, new_ci0 = parse_scholar_book(bt_text, ci_texts)

    if not scholar or not book:
        print(f"  WARNING: could not parse scholar/book from bt={repr(bt_text[:40])}")
        return

    sn.clear()
    sn.append(scholar)
    changes += 1

    bt.clear()
    bt.append(book)
    changes += 1

    # Update ci0 if we extracted a book prefix from it
    if new_ci0 and cis and not bt_text.count('-'):
        # Only update ci0 if book came from ci (bt had no dash = scholar only)
        cis[0].clear()
        cis[0].append(new_ci0)
        changes += 1

    ensure_editorial_in_ht(block, soup)


def move_bt_to_ht(block, soup, scholar=None, book=None, hadith_num=None):
    """Move book-title content to hadith-text (bt has the hadith text)."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not bt:
        return

    bt_text = bt.get_text(strip=True)
    bt.clear()
    if book:
        bt.append(book)
    changes += 1

    if scholar and sn:
        sn.clear()
        sn.append(scholar)
        changes += 1

    ref = block.select_one('.ref-info')
    ht = block.select_one('.hadith-text')
    if not ht:
        ht = soup.new_tag('div', **{'class': 'hadith-text'})
        if ref:
            ref.insert_after(ht)
        else:
            block.append(ht)
        changes += 1

    if hadith_num and not ht.select_one('.hadith-number'):
        hn = soup.new_tag('span', **{'class': 'hadith-number'})
        hn.string = hadith_num
        ht.insert(0, hn)
        changes += 1

    p = soup.new_tag('p')
    p.string = bt_text
    ht.append(p)
    changes += 1


def move_ci_to_ht(block, soup, ci_element, hadith_num=None):
    """Move chapter-info chain to hadith-text (ci has the hadith text, no number prefix)."""
    global changes
    ci_text = ci_element.get_text(strip=True).lstrip('- ')
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

    if hadith_num and not ht.select_one('.hadith-number'):
        hn = soup.new_tag('span', **{'class': 'hadith-number'})
        hn.string = hadith_num
        ht.insert(0, hn)
        changes += 1

    p = soup.new_tag('p')
    p.string = ci_text
    ht.append(p)
    changes += 1


def fix_sn_number_bt_text(block, soup, scholar, book):
    """Fix block where sn=hadith_number, bt=hadith_text."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not sn or not bt:
        return

    num_text = re.sub(r'[^\d]', '', sn.get_text())
    sn.clear()
    sn.append(scholar)
    changes += 1

    move_bt_to_ht(block, soup, book=book, hadith_num=num_text)


def fix_sn_combined_bt_text(block, soup):
    """Fix block where sn='scholar- book', bt=hadith_text."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    if not sn or not bt:
        return

    sn_text = sn.get_text(strip=True)
    m = re.match(r'^([^-]+?)\s*-+\s*(.+)$', sn_text, re.DOTALL)
    if m:
        scholar = m.group(1).strip()
        book = m.group(2).strip()
    else:
        scholar = sn_text
        book = ''

    sn.clear()
    sn.append(scholar)
    changes += 1

    move_bt_to_ht(block, soup, book=book)


def parse_footnote_source(items):
    scholar = book = ''
    for item in items:
        txt = item.get_text(strip=True)
        if not txt or item.select_one('.fn-num') and len(txt) < 80:
            continue
        if not scholar:
            m = re.match(r'^([^-]+?)\s*-+\s*(.+)$', txt, re.DOTALL)
            if m:
                scholar = m.group(1).strip()
                rest = m.group(2).strip()
                ch_pat = re.compile(
                    r'\s*-\s*(?:كتاب|باب|فصل|حرف|الطبقة|المجلد|تتمة|أمر\s|من اسمه)'
                )
                cm = ch_pat.search(rest)
                book = fix_typos(rest[:cm.start()].strip() if cm else rest)
    return scholar, book


def convert_footnote_to_block(soup, sec):
    global changes
    items = sec.select('.footnote-item')
    if not items:
        return

    ref_idx = None
    ref_text = ''
    for i, item in enumerate(items):
        txt = item.get_text(strip=True)
        if REF_RE.search(txt) and not item.select_one('.fn-num'):
            ref_idx = i
            ref_text = txt
            break

    if ref_idx is None:
        ref_idx = 0

    source_items = items[:ref_idx]
    scholar, book = parse_footnote_source(source_items)
    # Extract chapters from source items
    chapters = []
    for item in source_items:
        txt = item.get_text(strip=True)
        if item.select_one('.fn-num'):
            continue
        if scholar and book and txt not in (scholar, book):
            item_text = txt.lstrip('- ')
            if item_text != (scholar + ' - ' + book).lstrip('- '):
                if not any(item_text == (scholar + c).lstrip('- ') for c in ['', ' ']):
                    chapters.append(item_text)

    hadith_items = []
    for item in items[ref_idx + 1:]:
        txt = item.get_text(strip=True)
        if not txt:
            continue
        fn = item.select_one('.fn-num')
        if EDITORIAL_PATTERN.search(txt):
            hadith_items.append(('editorial',))
        elif fn:
            num = fn.get_text(strip=True)
            rest = txt[len(num):].strip()
            hadith_items.append(('numbered', num, rest))
        else:
            hadith_items.append(('text', txt))

    if not scholar:
        print(f"  WARNING: could not parse scholar from footnote-section; skipping")
        return

    block = soup.new_tag('div', **{'class': 'hadith-block'})
    bi = soup.new_tag('div', **{'class': 'book-info'})
    sn = soup.new_tag('span', **{'class': 'scholar-name'})
    sn.string = scholar
    bt = soup.new_tag('span', **{'class': 'book-title'})
    bt.string = book
    bi.append(sn)
    bi.append(bt)
    block.append(bi)

    for ch in chapters:
        ci_tag = soup.new_tag('span', **{'class': 'chapter-info'})
        ci_tag.string = ('- ' + ch) if not ch.startswith('-') else ch
        block.append(ci_tag)

    if ref_text:
        ri = soup.new_tag('div', **{'class': 'ref-info'})
        ri.string = ref_text
        block.append(ri)

    if hadith_items:
        ht = soup.new_tag('div', **{'class': 'hadith-text'})
        for item in hadith_items:
            if item[0] == 'editorial':
                ht.append(make_editorial_p(soup))
            elif item[0] == 'numbered':
                p = soup.new_tag('p')
                hn = soup.new_tag('span', **{'class': 'hadith-number'})
                hn.string = item[1]
                p.append(hn)
                p.append(' ' + item[2])
                ht.append(p)
            else:
                p = soup.new_tag('p')
                p.string = item[1]
                ht.append(p)
        block.append(ht)

    sec.replace_with(block)
    changes += 1


def process_file(path):
    global changes
    with open(path, encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    blocks = soup.select('.hadith-block')

    # -------------------------------------------------------------------------
    # File-specific fixes for MISSING_HT / structural inversions
    # -------------------------------------------------------------------------

    if path == 'Seerah/13Ytboon.html':
        # b2: sn=‏2669 (num), bt=hadith chain → scholar=مسلم, book=صحيح مسلم
        fix_sn_number_bt_text(blocks[1], soup, 'مسلم', 'صحيح مسلم')

    elif path == 'Seerah/23Tefatan.html':
        # b1: sn=‏2691 (num), bt=hadith chain → البخاري
        fix_sn_number_bt_text(blocks[0], soup, 'البخاري', 'صحيح البخاري')
        # b2: sn=‏1799 (num), bt=hadith chain → مسلم
        fix_sn_number_bt_text(blocks[1], soup, 'مسلم', 'صحيح مسلم')

    elif path == 'Seerah/7LaYrown.html':
        # b8: sn=يعقوب بن شيبة, bt=hadith text (no book title)
        b8 = blocks[7]
        bt8 = b8.select_one('.book-title')
        if bt8 and not b8.select_one('.hadith-text'):
            bt_text = bt8.get_text(strip=True)
            # Move bt to hadith-text, leave bt empty
            bt8.clear()
            changes += 1
            ht8 = soup.new_tag('div', **{'class': 'hadith-text'})
            p8 = soup.new_tag('p')
            p8.string = bt_text
            ht8.append(p8)
            ref8 = b8.select_one('.ref-info')
            if ref8:
                ref8.insert_after(ht8)
            else:
                b8.append(ht8)
            changes += 1

    elif path == 'Seerah/9Hodhyfa.html':
        # b1 & b2: sn=7113/7114 (num), bt=hadith chain → البخاري
        fix_sn_number_bt_text(blocks[0], soup, 'البخاري', 'صحيح البخاري')
        fix_sn_number_bt_text(blocks[1], soup, 'البخاري', 'صحيح البخاري')

    elif path == 'Seerah/1Zahf/OM/1uhod/1.html':
        # b21: sn='ابن أبي الحديد- شرح نهج البلاغة', bt=text
        fix_sn_combined_bt_text(blocks[20], soup)

    elif path == 'Seerah/1Zahf/OTH/17IbnAbielHadeed.html':
        # b1: sn='ابن أبي الحديد- شرح نهج البلاغة', bt=text
        fix_sn_combined_bt_text(blocks[0], soup)

    elif path == 'Seerah/24Mkhnthon/3Mate.html':
        # b12: sn='السيوطي -الديباج على صحيح مسلم بن الحجاج-2180', bt=None, ci='- 2180 - أ'
        b12 = blocks[11]
        sn12 = b12.select_one('.scholar-name')
        if sn12 and not b12.select_one('.hadith-text'):
            sn_text = sn12.get_text(strip=True)
            # Parse: 'السيوطي -الديباج على صحيح مسلم بن الحجاج-2180'
            parts = re.split(r'\s*-+\s*', sn_text, 2)
            if len(parts) >= 2:
                scholar12 = parts[0].strip()
                book12 = parts[1].strip() if len(parts) > 1 else ''
                entry12 = parts[2].strip() if len(parts) > 2 else ''
                sn12.clear()
                sn12.append(scholar12)
                changes += 1
                bt12 = b12.select_one('.book-title')
                if not bt12:
                    bi12 = b12.select_one('.book-info')
                    if bi12:
                        bt12 = soup.new_tag('span', **{'class': 'book-title'})
                        bt12.string = book12
                        bi12.insert(0, bt12)
                        changes += 1
                else:
                    bt12.clear()
                    bt12.append(book12)
                    changes += 1
                # Remove truncated ci1 ('- 2180 - أ') - it's incomplete
                cis12 = b12.select('.chapter-info')
                for ci in cis12:
                    ci_txt = ci.get_text(strip=True)
                    m = re.match(r'^-\s*\d+\s*-\s*.{0,5}$', ci_txt)
                    if m:
                        ci.decompose()
                        changes += 1
                        break
                # Create hadith-text with hadith-number
                if entry12:
                    ht12 = soup.new_tag('div', **{'class': 'hadith-text'})
                    hn12 = soup.new_tag('span', **{'class': 'hadith-number'})
                    hn12.string = entry12
                    ht12.append(hn12)
                    ensure_editorial_in_ht(b12, soup)
                else:
                    ensure_editorial_in_ht(b12, soup)

    # -------------------------------------------------------------------------
    # Convert footnotes-sections to hadith-blocks
    # -------------------------------------------------------------------------
    for sec in soup.select('.footnotes-section'):
        convert_footnote_to_block(soup, sec)

    # -------------------------------------------------------------------------
    # Global: fix EDITORIAL_SN blocks (auto-detect scholar/book)
    # -------------------------------------------------------------------------
    for b in soup.select('.hadith-block'):
        sn = b.select_one('.scholar-name')
        if sn and EDITORIAL_PATTERN.search(sn.get_text()):
            fix_editorial_sn_block(b, soup)

    # -------------------------------------------------------------------------
    # Global: fix HADITH_IN_CI blocks without hadith-text
    # -------------------------------------------------------------------------
    for b in soup.select('.hadith-block'):
        ht = b.select_one('.hadith-text')
        if ht:
            continue
        for ci in b.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b, soup, ci)
                break

    # -------------------------------------------------------------------------
    # Global: wrap editorial notes
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
        glob.glob('Seerah/*.html') + glob.glob('Seerah/**/*.html', recursive=True)
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
