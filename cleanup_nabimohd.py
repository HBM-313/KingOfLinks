#!/usr/bin/env python3
"""Cleanup script for NabiMohd folder - fix all data quality issues."""

import glob
import re
from bs4 import BeautifulSoup, Tag

EDITORIAL_TEXT = 'النص طويل لذا استقطع منه موضع الشاهد'
EDITORIAL_PATTERN = re.compile(
    r'\[?\s*النص طويل\s*(?:جدا\s*)?لذا استقطع منه موضع الشاهد\s*\]?'
)
HADITH_IN_CI_RE = re.compile(r'^-\s*(\d+)\s*-\s*(.{10,})', re.DOTALL)

changes = 0


def make_editorial_p(soup):
    p = soup.new_tag('p')
    span = soup.new_tag('span', **{'class': 'editorial-note'})
    span.string = EDITORIAL_TEXT
    p.append(span)
    return p


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


def fix_hadith_chain_in_ci(block, soup, ci_element, hadith_num=None):
    """Move hadith chain (no number prefix) from chapter-info to hadith-text."""
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


def process_file(path):
    global changes
    with open(path, encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    blocks = soup.select('.hadith-block')

    # -------------------------------------------------------------------------
    # File-specific fixes
    # -------------------------------------------------------------------------

    if path == 'NabiMohd/2LaYastahy.html':
        # b2: sn='‏603' (hadith number), bt=full hadith text, ci1=book+chapter
        b2 = blocks[1]
        sn2 = b2.select_one('.scholar-name')
        bt2 = b2.select_one('.book-title')
        ci2_list = b2.select('.chapter-info')
        if sn2 and bt2 and not b2.select_one('.hadith-text'):
            hadith_num = re.sub(r'[^\d]', '', sn2.get_text())
            hadith_text_content = bt2.get_text(strip=True)
            # Extract book from ci1: '- الأدب المفرد - باب: الحياء'
            if ci2_list:
                ci_txt = ci2_list[0].get_text(strip=True).lstrip('- ')
                parts = ci_txt.split(' - ', 1)
                book_name = parts[0].strip()
                chapter_text = parts[1].strip() if len(parts) > 1 else ''
            else:
                book_name = 'الأدب المفرد'
                chapter_text = ''

            # Fix scholar-name (البخاري authored الأدب المفرد)
            sn2.clear()
            sn2.append('البخاري')
            changes += 1

            # Fix book-title
            bt2.clear()
            bt2.append(book_name)
            changes += 1

            # Update chapter-info to just the chapter part
            if ci2_list and chapter_text:
                ci2_list[0].clear()
                ci2_list[0].append('- ' + chapter_text)
                changes += 1

            # Create hadith-text
            ref2 = b2.select_one('.ref-info')
            ht2 = soup.new_tag('div', **{'class': 'hadith-text'})
            if hadith_num:
                hn = soup.new_tag('span', **{'class': 'hadith-number'})
                hn.string = hadith_num
                ht2.append(hn)
            p2 = soup.new_tag('p')
            p2.string = hadith_text_content
            ht2.append(p2)
            if ref2:
                ref2.insert_after(ht2)
            else:
                b2.append(ht2)
            changes += 1

        # b6: sn='الترمذي', bt='‏1645' (hadith number), ci1=hadith chain
        b6 = blocks[5]
        bt6 = b6.select_one('.book-title')
        ci6_list = b6.select('.chapter-info')
        if bt6 and ci6_list and not b6.select_one('.hadith-text'):
            num_text = re.sub(r'[^\d]', '', bt6.get_text())
            ci6 = ci6_list[0]
            # Move bt hadith number to hadith-text number; clear bt (no book title)
            bt6.clear()
            changes += 1
            fix_hadith_chain_in_ci(b6, soup, ci6, hadith_num=num_text)

    elif path == 'NabiMohd/5BdoonWdhoo.html':
        # b1: sn='صحيح البخاري' (book title!), bt='‏138' (hadith number), ci=hadith chain
        b1 = blocks[0]
        sn1 = b1.select_one('.scholar-name')
        bt1 = b1.select_one('.book-title')
        ci1_list = b1.select('.chapter-info')
        if sn1 and bt1 and not b1.select_one('.hadith-text'):
            book_name = sn1.get_text(strip=True)
            num_text = re.sub(r'[^\d]', '', bt1.get_text())
            # Fix: sn → scholar, bt → book title
            sn1.clear()
            sn1.append('البخاري')
            changes += 1
            bt1.clear()
            bt1.append(book_name)
            changes += 1
            # Move ci hadith chain to hadith-text
            if ci1_list:
                fix_hadith_chain_in_ci(b1, soup, ci1_list[0], hadith_num=num_text)

    # -------------------------------------------------------------------------
    # Global pass: HADITH_IN_CI for all blocks without hadith-text
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
    # Global pass: wrap editorial notes
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
        glob.glob('NabiMohd/*.html') + glob.glob('NabiMohd/**/*.html', recursive=True)
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
