#!/usr/bin/env python3
"""Cleanup script for Hywan folder - fix all data quality issues."""

import glob
import re
from bs4 import BeautifulSoup, Tag

EDITORIAL_TEXT = 'النص طويل لذا استقطع منه موضع الشاهد'
EDITORIAL_PATTERN = re.compile(r'\[?\s*النص طويل لذا استقطع منه موضع الشاهد\s*\]?')
HADITH_IN_CI_RE = re.compile(r'^-\s*(\d+)\s*-\s*(.+)', re.DOTALL)

BOOK_TO_SCHOLAR = {
    'مجمع الزوائد ومنبع الفوائد': 'الهيثمي',
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
    'كتاب السنة': 'ابن أبي عاصم',
}

changes = 0


def new_tag(soup, name, class_=None, string=None):
    t = soup.new_tag(name)
    if class_:
        t['class'] = class_
    if string:
        t.string = string
    return t


def make_editorial_p(soup):
    """Create <p><span class="editorial-note">النص طويل...</span></p>"""
    p = soup.new_tag('p')
    span = soup.new_tag('span', **{'class': 'editorial-note'})
    span.string = EDITORIAL_TEXT
    p.append(span)
    return p


def fix_editorial_sn(block, soup, scholar, book, keep_ci_index=None):
    """Fix block where scholar-name contains editorial note.
    Sets scholar-name to scholar, book-title to book.
    If keep_ci_index is set, re-use the first chapter-info for the book (splits off book part).
    Adds editorial note to hadith-text if not already present.
    """
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    ht = block.select_one('.hadith-text')

    # Fix scholar-name
    sn.clear()
    sn.append(scholar)
    changes += 1

    # Fix book-title
    bt.clear()
    bt.append(book)
    changes += 1

    # Add editorial note to hadith-text
    if ht:
        # Check if editorial note already exists
        has_editorial = any(
            p.select_one('.editorial-note') or EDITORIAL_PATTERN.search(p.get_text())
            for p in ht.select('p')
        )
        if not has_editorial:
            ep = make_editorial_p(soup)
            ht.insert(0, ep)
            changes += 1
    else:
        # Create hadith-text div with editorial note
        ref = block.select_one('.ref-info')
        ht_div = soup.new_tag('div', **{'class': 'hadith-text'})
        ep = make_editorial_p(soup)
        ht_div.append(ep)
        if ref:
            ref.insert_after(ht_div)
        else:
            block.append(ht_div)
        changes += 1


def fix_hadith_in_ci(block, soup, ci_element):
    """Fix block where chapter-info contains the actual hadith text.
    Extracts number and text, creates hadith-text div, removes the bad chapter-info.
    """
    global changes
    ci_text = ci_element.get_text(strip=True)
    m = HADITH_IN_CI_RE.match(ci_text)
    if not m:
        print(f"  WARNING: could not parse hadith from ci: {ci_text[:60]}")
        return

    hadith_num = m.group(1).strip()
    hadith_text = m.group(2).strip()

    # Remove the chapter-info
    ci_element.decompose()
    changes += 1

    # Check if hadith-text div already exists
    ht = block.select_one('.hadith-text')
    if not ht:
        ref = block.select_one('.ref-info')
        ht = soup.new_tag('div', **{'class': 'hadith-text'})
        if ref:
            ref.insert_after(ht)
        else:
            block.append(ht)
        changes += 1

    # Add hadith-number span if not present
    if not ht.select_one('.hadith-number'):
        hn = soup.new_tag('span', **{'class': 'hadith-number'})
        hn.string = hadith_num
        ht.insert(0, hn)
        changes += 1

    # Add hadith text as <p> (insert before existing content or append)
    p = soup.new_tag('p')
    p.string = hadith_text
    ht.append(p)
    changes += 1


def wrap_editorial_notes(soup):
    """Global pass: wrap unspanned النص طويل in editorial-note spans."""
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

    if path == 'Hywan/10Hayyah.html':
        # b3: sn=[النص طويل], bt="الحلبي- السيرة الحلبية"
        b = blocks[2]
        fix_editorial_sn(b, soup, 'الحلبي', 'السيرة الحلبية')

    elif path == 'Hywan/11Ghanam.html':
        # b7: sn=[النص طويل], bt="الحلبي- السيرة الحلبية"
        b = blocks[6]
        fix_editorial_sn(b, soup, 'الحلبي', 'السيرة الحلبية')

    elif path == 'Hywan/2Bqrah.html':
        # b2: sn=[النص طويل], bt="صحيح مسلم" → scholar=مسلم
        b = blocks[1]
        fix_editorial_sn(b, soup, 'مسلم', 'صحيح مسلم')

        # b7: الألباني + إرواء الغليل, 2nd chapter-info has hadith text
        b7 = blocks[6]
        cis = b7.select('.chapter-info')
        # Find the chapter-info with hadith text (starts with - NUMBER -)
        for ci in cis:
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b7, soup, ci)
                break

    elif path == 'Hywan/3Dhab.html':
        # b2: الهيثمي, chapter-info has hadith text
        b2 = blocks[1]
        for ci in b2.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b2, soup, ci)
                break

        # b9: المتقي الهندي, chapter-info has hadith text
        b9 = blocks[8]
        for ci in b9.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b9, soup, ci)
                break

    elif path == 'Hywan/7Qerd.html':
        # b6: ابن الأثير + أسد الغابة, 2nd chapter-info has full entry text
        b6 = blocks[5]
        cis = b6.select('.chapter-info')
        for ci in cis:
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b6, soup, ci)
                break

        # b7: sn=[النص طويل], bt="المزي", 1st ci="تهذيب الكمال...", 2nd ci="- 4457 - ..."
        b7 = blocks[6]
        # First fix the scholar-name (EDITORIAL_SN)
        # Book title should be extracted from first chapter-info
        bt7 = b7.select_one('.book-title')
        bt7_text = bt7.get_text(strip=True) if bt7 else ''
        # bt is "المزي" (scholar name). Book is in first chapter-info.
        first_ci = b7.select('.chapter-info')[0] if b7.select('.chapter-info') else None
        if first_ci:
            ci_text = first_ci.get_text(strip=True).lstrip('- ')
            # Split off the book title from the chapter-info
            # first ci = "- تهذيب الكمال في أسماء الرجال - باب : العين - من اسمه عمرو"
            parts = re.split(r'\s+-\s*(?:باب|كتاب|فصل|ذكر|حرف|من اسمه)', ci_text, 1)
            book_title = parts[0].strip()
        else:
            book_title = bt7_text  # fallback

        fix_editorial_sn(b7, soup, bt7_text, book_title)

        # Now fix the first chapter-info to remove the book title (it's been moved)
        if first_ci:
            ci_text = first_ci.get_text(strip=True).lstrip('- ')
            parts = re.split(r'\s+-\s*(?:باب|كتاب|فصل|ذكر|حرف|من اسمه)', ci_text, 1)
            if len(parts) > 1:
                # Keep only the chapter part in the chapter-info
                remaining_parts = ci_text[len(parts[0]):].strip()
                # Re-split remaining into separate chapter-info spans
                remaining_parts = remaining_parts.lstrip('- ')
                sub_parts = re.split(r'\s+-\s*(?:باب|كتاب|فصل|ذكر|حرف|من اسمه)', remaining_parts)
                # For now just set the first ci to the chapter part
                first_ci.clear()
                # Rebuild: get what comes after the book title
                remaining = ci_text[len(parts[0]):].strip()
                first_ci.append(remaining)
                changes += 1

        # Fix the second chapter-info "- 4457 - ..." - this is entry number + entry header
        # For b7, the hadith-text div has the actual content. The 2nd ci is just the entry ID.
        # We'll keep it as-is since hadith-text exists (only entry ID in ci, not full text).
        # Actually the entry number should move to hadith-number in hadith-text.
        remaining_cis = b7.select('.chapter-info')
        for ci in remaining_cis:
            m = HADITH_IN_CI_RE.match(ci.get_text(strip=True))
            if m:
                hadith_num = m.group(1).strip()
                entry_name = m.group(2).strip()
                # Update ci to just have the entry name (remove number prefix)
                ci.clear()
                ci.append(f'- {entry_name}')
                changes += 1
                # Add hadith-number to hadith-text
                ht7 = b7.select_one('.hadith-text')
                if ht7 and not ht7.select_one('.hadith-number'):
                    hn = soup.new_tag('span', **{'class': 'hadith-number'})
                    hn.string = hadith_num
                    ht7.insert(0, hn)
                    changes += 1
                break

        # b9: sn=[النص طويل], bt="الباجي", ci="- التعديل والتجريح..."
        b9 = blocks[8]
        bt9 = b9.select_one('.book-title')
        bt9_text = bt9.get_text(strip=True) if bt9 else ''
        # bt = "الباجي" (scholar name). Book is in first chapter-info.
        first_ci9 = b9.select('.chapter-info')[0] if b9.select('.chapter-info') else None
        if first_ci9:
            ci9_text = first_ci9.get_text(strip=True).lstrip('- ')
            parts9 = re.split(r'\s+-\s*(?:باب|كتاب|فصل|ذكر|حرف)', ci9_text, 1)
            book_title9 = parts9[0].strip()
        else:
            book_title9 = bt9_text

        fix_editorial_sn(b9, soup, bt9_text, book_title9)

        # Update first ci to remove book title prefix
        if first_ci9:
            ci9_text = first_ci9.get_text(strip=True).lstrip('- ')
            parts9 = re.split(r'\s+-\s*(?:باب|كتاب|فصل|ذكر|حرف)', ci9_text, 1)
            if len(parts9) > 1:
                remaining9 = ci9_text[len(parts9[0]):].strip()
                first_ci9.clear()
                first_ci9.append(remaining9)
                changes += 1

    elif path == 'Hywan/8Theb.html':
        # b8: الألباني + إرواء الغليل, 2nd chapter-info has hadith text
        b8 = blocks[7]
        cis = b8.select('.chapter-info')
        for ci in cis:
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b8, soup, ci)
                break

    # Global pass: wrap all unspanned النص طويل in editorial-note spans
    wrap_editorial_notes(soup)

    # Write back
    new_content = str(soup)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Updated: {path}")
    else:
        print(f"  No changes: {path}")


def main():
    global changes
    paths = sorted(glob.glob('Hywan/*.html') + glob.glob('Hywan/**/*.html', recursive=True))
    # Deduplicate
    seen = set()
    paths = [p for p in paths if not (p in seen or seen.add(p))]

    for path in paths:
        if 'Main124' in path:
            continue  # no blocks, skip
        prev = changes
        process_file(path)
        print(f"    {changes - prev} changes")

    print(f"\nTotal changes: {changes}")


if __name__ == '__main__':
    main()
