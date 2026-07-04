#!/usr/bin/env python3
"""Cleanup script for Daeefa folder - fix all data quality issues."""

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
    """Global pass: wrap unspanned editorial notes in .editorial-note spans."""
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


def fix_editorial_sn(block, soup, scholar, book):
    """Set scholar-name to scholar, book-title to book; add editorial note if needed."""
    global changes
    sn = block.select_one('.scholar-name')
    bt = block.select_one('.book-title')
    ht = block.select_one('.hadith-text')

    if sn:
        sn.clear()
        sn.append(scholar)
        changes += 1

    if bt:
        bt.clear()
        bt.append(book)
        changes += 1

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


def fix_hadith_in_ci(block, soup, ci_element):
    """Move hadith content from chapter-info to hadith-text."""
    global changes
    ci_text = ci_element.get_text(strip=True)
    m = HADITH_IN_CI_RE.match(ci_text)
    if not m:
        print(f"  WARNING: could not parse hadith from ci: {ci_text[:60]}")
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


def parse_footnote_source(items):
    """Parse scholar, book, chapters from footnote-item list (before ref item).

    Returns (scholar, book, chapters_list).
    """
    scholar = book = ''
    chapters = []

    for item in items:
        txt = item.get_text(strip=True)
        if not txt:
            continue
        # Skip fn-num-only items (subject annotations)
        fn = item.select_one('.fn-num')
        if fn and len(txt) < 80:
            continue

        if not scholar:
            # Try to split on first dash (Scholar-Book or Scholar - Book)
            m = re.match(r'^([^-]+?)\s*-+\s*(.+)$', txt, re.DOTALL)
            if m:
                scholar = m.group(1).strip()
                rest = m.group(2).strip()
                # Split book from chapter by chapter keywords
                ch_pat = re.compile(
                    r'\s*-\s*(?:كتاب|باب|فصل|حرف|الطبقة|المجلد|من اسمه|تراجم|الموتى|سنة)'
                )
                cm = ch_pat.search(rest)
                if cm:
                    book = rest[:cm.start()].strip()
                    chapters.append(rest[cm.start():].strip().lstrip('- '))
                else:
                    book = rest
        else:
            # Additional chapter info line
            if not REF_RE.search(txt):
                chapters.append(txt)

    return scholar, book, chapters


def convert_footnote_to_block(soup, sec):
    """Convert a footnotes-section div to a hadith-block div in place."""
    global changes
    items = sec.select('.footnote-item')
    if not items:
        return

    # Find ref item
    ref_idx = None
    ref_text = ''
    for i, item in enumerate(items):
        txt = item.get_text(strip=True)
        if REF_RE.search(txt) and not item.select_one('.fn-num'):
            ref_idx = i
            ref_text = txt
            break

    if ref_idx is None:
        # No ref → use all as hadith text, try to extract scholar from first item
        ref_idx = 0
        ref_text = ''

    source_items = items[:ref_idx]
    scholar, book, chapters = parse_footnote_source(source_items)

    # Collect hadith text items (after ref)
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

    # Build hadith-block
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
    # File-specific fixes
    # -------------------------------------------------------------------------

    if path == 'Daeefa/1.html':
        # b3: bt contains editorial/analysis about narrator → move to hadith-text
        b3 = blocks[2]
        bt3 = b3.select_one('.book-title')
        if bt3:
            bt_text = bt3.get_text(strip=True)
            bt3.clear()  # leave bt empty; no clean book title available
            changes += 1
            ht = b3.select_one('.hadith-text')
            if not ht:
                ref = b3.select_one('.ref-info')
                ht = soup.new_tag('div', **{'class': 'hadith-text'})
                p = soup.new_tag('p')
                p.string = bt_text
                ht.append(p)
                if ref:
                    ref.insert_after(ht)
                else:
                    b3.append(ht)
                changes += 1

    elif path == 'Daeefa/10.html':
        # b2: سيد الخوئي, bt=معجم رجال الحديث, ci=HADITH_IN_CI → create hadith-text
        b2 = blocks[1]
        for ci in b2.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b2, soup, ci)
                break

    elif path == 'Daeefa/13.html':
        # b3: sn=narrator name, bt=العلامة الحلي (scholar!), ci1=book name, ci2=HADITH_IN_CI
        b3 = blocks[2]
        sn3 = b3.select_one('.scholar-name')
        bt3 = b3.select_one('.book-title')
        if sn3 and bt3:
            scholar_name = bt3.get_text(strip=True)
            sn3.clear()
            sn3.append(scholar_name)
            changes += 1
            # Get book title from first chapter-info
            cis3 = b3.select('.chapter-info')
            if cis3:
                ci1_text = cis3[0].get_text(strip=True).lstrip('- ')
                bt3.clear()
                bt3.append(ci1_text)
                changes += 1
                cis3[0].decompose()
                changes += 1
            # Move HADITH_IN_CI (now first ci) to hadith-text
            cis3 = b3.select('.chapter-info')
            for ci in cis3:
                if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                    fix_hadith_in_ci(b3, soup, ci)
                    break

        # b4: sn='التفرشي- نقد الرجال' (combined), bt='3108 / 148' (entry ref)
        b4 = blocks[3]
        sn4 = b4.select_one('.scholar-name')
        bt4 = b4.select_one('.book-title')
        if sn4:
            sn4_text = sn4.get_text(strip=True)
            if '- ' in sn4_text:
                parts = sn4_text.split('- ', 1)
                sn4.clear()
                sn4.append(parts[0].strip())
                changes += 1
                if bt4:
                    bt4.clear()
                    bt4.append(parts[1].strip())
                    changes += 1
        # bt='3108 / 148' looks like entry/page ref → move to ref-info or note
        # ci1 has the actual entry text → HADITH_IN_CI
        for ci in b4.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b4, soup, ci)
                break
        # Fix the remaining bt if it still has the old number ref
        bt4 = b4.select_one('.book-title')
        if bt4:
            bt4_txt = bt4.get_text(strip=True)
            if re.match(r'^\d+\s*/\s*\d+$', bt4_txt):
                bt4.clear()
                changes += 1

        # b6: sn='السيد علي البروجردي- طرائف المقال' (combined), bt=None
        b6 = blocks[5]
        sn6 = b6.select_one('.scholar-name')
        if sn6:
            sn6_text = sn6.get_text(strip=True)
            if '- ' in sn6_text:
                parts = sn6_text.split('- ', 1)
                sn6.clear()
                sn6.append(parts[0].strip())
                changes += 1
                # Add book-title if not present
                bt6 = b6.select_one('.book-title')
                bi6 = b6.select_one('.book-info')
                if not bt6 and bi6:
                    bt6 = soup.new_tag('span', **{'class': 'book-title'})
                    bt6.string = parts[1].strip()
                    bi6.append(bt6)
                    changes += 1
                elif bt6:
                    bt6.clear()
                    bt6.append(parts[1].strip())
                    changes += 1
        # ci1 is HADITH_IN_CI
        for ci in b6.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b6, soup, ci)
                break

    elif path == 'Daeefa/14.html':
        # b3: الرازي, ci2=HADITH_IN_CI → create hadith-text
        b3 = blocks[2]
        cis3 = b3.select('.chapter-info')
        for ci in cis3:
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b3, soup, ci)
                break
        # Convert all footnotes-sections to hadith-blocks
        for sec in soup.select('.footnotes-section'):
            convert_footnote_to_block(soup, sec)

    elif path == 'Daeefa/15/7.html':
        # b2: EDITORIAL_SN, bt='الشوكاني', ci has chapter but no book name
        # Shawkani's main hadith jurisprudence work is 'نيل الأوطار'
        b2 = blocks[1]
        fix_editorial_sn(b2, soup, 'الشوكاني', 'نيل الأوطار')

        # b8: المتقي الهندي, ci1=HADITH_IN_CI → create hadith-text
        b8 = blocks[7]
        for ci in b8.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b8, soup, ci)
                break

        # b9: ابن الأثير, ci2=HADITH_IN_CI → create hadith-text; ci1 is book+chapter
        b9 = blocks[8]
        cis9 = b9.select('.chapter-info')
        for ci in cis9:
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b9, soup, ci)
                break

        # b13: EDITORIAL_SN, bt='الحلبي', ci1 starts with book name
        b13 = blocks[12]
        ci13 = b13.select('.chapter-info')
        book13 = 'السيرة الحلبية'
        if ci13:
            ci_txt = ci13[0].get_text(strip=True).lstrip('- ')
            m = re.match(r'^([؀-ۿ\s]+?)\s*-', ci_txt)
            if m:
                book13 = m.group(1).strip()
        fix_editorial_sn(b13, soup, 'الحلبي', book13)

    elif path == 'Daeefa/15/8.html':
        # b2: EDITORIAL_SN, bt='ابن حبان', book from ci1, ci2=HADITH_IN_CI
        b2 = blocks[1]
        ci2_list = b2.select('.chapter-info')
        book2 = 'الثقات'
        if ci2_list:
            ci1_txt = ci2_list[0].get_text(strip=True).lstrip('- ')
            m = re.match(r'^([؀-ۿ\s]+?)\s*-', ci1_txt)
            if m:
                book2 = m.group(1).strip()
        fix_editorial_sn(b2, soup, 'ابن حبان', book2)
        # ci2 → HADITH_IN_CI
        for ci in b2.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b2, soup, ci)
                break

        # b6: EDITORIAL_SN, bt='الهيثمي', book from ci1, ci2=HADITH_IN_CI
        b6 = blocks[5]
        ci6_list = b6.select('.chapter-info')
        book6 = 'مجمع الزوائد ومنبع الفوائد'
        if ci6_list:
            ci1_txt = ci6_list[0].get_text(strip=True).lstrip('- ')
            # ci1 text: 'مجمعالزوائد ومنبع الفوائد - كتاب...' (typo: no space)
            # Try to extract book name
            m = re.match(r'^([؀-ۿ\s]+?)\s*-', ci1_txt)
            if m:
                raw = m.group(1).strip()
                # Fix the typo مجمعالزوائد → مجمع الزوائد
                raw = re.sub(r'مجمعالزوائد', 'مجمع الزوائد', raw)
                book6 = raw
        fix_editorial_sn(b6, soup, 'الهيثمي', book6)
        # ci2 → HADITH_IN_CI
        for ci in b6.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b6, soup, ci)
                break

        # b8: EDITORIAL_SN, bt='النسائي', book from ci1, ht already exists
        b8 = blocks[7]
        ci8_list = b8.select('.chapter-info')
        book8 = 'سنن النسائي'
        if ci8_list:
            ci1_txt = ci8_list[0].get_text(strip=True).lstrip('- ')
            m = re.match(r'^([؀-ۿ\s]+?)\s*-', ci1_txt)
            if m:
                raw = m.group(1).strip()
                # Fix typo سننالنسائي → سنن النسائي
                raw = re.sub(r'سننالنسائي', 'سنن النسائي', raw)
                raw = re.sub(r'سننال', 'سنن ال', raw)
                book8 = raw
        fix_editorial_sn(b8, soup, 'النسائي', book8)

    elif path == 'Daeefa/15/10.html':
        # b7: EDITORIAL_SN, bt='ابن الأثير', book=أسد الغابة, ci1=book+chapter
        # ci2 and ci3 are short/long versions of entry 4601 → keep short ci2 as chapter context
        b7 = blocks[6]
        fix_editorial_sn(b7, soup, 'ابن الأثير', 'أسد الغابة')
        # Handle ci2/ci3: remove the long duplicate ci3
        cis7 = b7.select('.chapter-info')
        # ci3 is the long version of ci2; remove ci3 (if exists, index 2)
        if len(cis7) >= 3:
            # Remove the long ci3 (duplicate entry)
            cis7[2].decompose()
            changes += 1
        # ci2 looks like '- 4601 - مالك بن سنان بن عبيد' which is an entry number+name
        # Extract number, add as hadith-number, clean ci2 to just entry name
        cis7 = b7.select('.chapter-info')
        for ci in cis7:
            txt = ci.get_text(strip=True)
            m = re.match(r'^-\s*(\d+)\s*-\s*(.+)$', txt, re.DOTALL)
            if m:
                hadith_num = m.group(1).strip()
                entry_name = m.group(2).strip()
                ht7 = b7.select_one('.hadith-text')
                if ht7 and not ht7.select_one('.hadith-number'):
                    hn = soup.new_tag('span', **{'class': 'hadith-number'})
                    hn.string = hadith_num
                    ht7.insert(0, hn)
                    changes += 1
                ci.clear()
                ci.append('- ' + entry_name)
                changes += 1
                break

    elif path == 'Daeefa/15/11.html':
        # b2: EDITORIAL_SN, bt='صحيحمسلم' (typo) → scholar=مسلم, book=صحيح مسلم
        b2 = blocks[1]
        fix_editorial_sn(b2, soup, 'مسلم', 'صحيح مسلم')

        # b7: EDITORIAL_SN, bt='الطبراني', book=المعجم الكبير from ci1
        b7 = blocks[6]
        cis7 = b7.select('.chapter-info')
        book7 = 'المعجم الكبير'
        if cis7:
            ci_txt = cis7[0].get_text(strip=True).lstrip('- ')
            m = re.match(r'^([؀-ۿ\s]+?)\s*-', ci_txt)
            if m:
                book7 = m.group(1).strip()
        fix_editorial_sn(b7, soup, 'الطبراني', book7)

    elif path == 'Daeefa/20.html':
        # Convert footnotes-sections to hadith-blocks
        for sec in soup.select('.footnotes-section'):
            convert_footnote_to_block(soup, sec)

    elif path == 'Daeefa/21.html':
        # Convert footnotes-sections to hadith-blocks
        for sec in soup.select('.footnotes-section'):
            convert_footnote_to_block(soup, sec)

    elif path == 'Daeefa/3.html':
        # b13: HADITH_IN_CI ci1 → create hadith-text
        b13 = blocks[12]
        for ci in b13.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b13, soup, ci)
                break

        # b15: HADITH_IN_CI ci1 → create hadith-text
        b15 = blocks[14]
        for ci in b15.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b15, soup, ci)
                break

    elif path == 'Daeefa/6.html':
        # b2, b5, b7: all HADITH_IN_CI with no hadith-text
        for bi in [1, 4, 6]:
            b = blocks[bi]
            for ci in b.select('.chapter-info'):
                if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                    fix_hadith_in_ci(b, soup, ci)
                    break

    elif path == 'Daeefa/8.html':
        # b5, b6, b10: all HADITH_IN_CI with no hadith-text
        for bi in [4, 5, 9]:
            b = blocks[bi]
            for ci in b.select('.chapter-info'):
                if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                    fix_hadith_in_ci(b, soup, ci)
                    break

    elif path == 'Daeefa/9.html':
        # b3: HADITH_IN_CI ci1 → create hadith-text
        b3 = blocks[2]
        for ci in b3.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b3, soup, ci)
                break

    elif path == 'Daeefa/15/1.html':
        # 4 loose <p> in article-body → wrap in analysis-note
        article = soup.select_one('.article-body')
        if article:
            loose = [t for t in article.children
                     if isinstance(t, Tag) and t.name == 'p']
            if loose:
                note = soup.new_tag('div', **{'class': 'analysis-note'})
                loose[0].insert_before(note)
                for p in loose:
                    note.append(p.extract())
                changes += 1

    elif path == 'Daeefa/15/3.html':
        # 7 loose <p>: metadata + السيد السيستاني + الاستفتاءات + ref + text
        # Build a hadith-block for the source citation
        article = soup.select_one('.article-body')
        if article:
            loose = [t for t in article.children
                     if isinstance(t, Tag) and t.name == 'p']
            if loose:
                # Identify scholar-book item (contains ' - ')
                scholar_p_idx = None
                for i, p in enumerate(loose):
                    txt = p.get_text(strip=True)
                    if ' - ' in txt and not txt.startswith('مكتبة') and not txt.startswith('جميع'):
                        scholar_p_idx = i
                        break

                if scholar_p_idx is not None:
                    scholar_line = loose[scholar_p_idx].get_text(strip=True)
                    parts = scholar_line.split(' - ', 1)
                    scholar_name = parts[0].strip()
                    book_name = parts[1].strip() if len(parts) > 1 else ''

                    # Find ref item (contains رقم الصفحة)
                    ref_p_idx = None
                    for i, p in enumerate(loose):
                        if 'رقم الصفحة' in p.get_text():
                            ref_p_idx = i
                            break
                    ref_txt = loose[ref_p_idx].get_text(strip=True) if ref_p_idx else ''

                    # Build hadith-block
                    hblock = soup.new_tag('div', **{'class': 'hadith-block'})
                    bi = soup.new_tag('div', **{'class': 'book-info'})
                    sn = soup.new_tag('span', **{'class': 'scholar-name'})
                    sn.string = scholar_name
                    bt = soup.new_tag('span', **{'class': 'book-title'})
                    bt.string = book_name
                    bi.append(sn)
                    bi.append(bt)
                    hblock.append(bi)

                    if ref_txt:
                        ri = soup.new_tag('div', **{'class': 'ref-info'})
                        ri.string = ref_txt
                        hblock.append(ri)

                    ht_div = soup.new_tag('div', **{'class': 'hadith-text'})
                    for i, p in enumerate(loose):
                        if i in (scholar_p_idx,) or (ref_p_idx and i == ref_p_idx):
                            continue
                        if i < (scholar_p_idx or 99):
                            continue  # skip metadata before source
                        new_p = soup.new_tag('p')
                        new_p.string = p.get_text(strip=True)
                        ht_div.append(new_p)
                    if len(ht_div.select('p')) > 0:
                        hblock.append(ht_div)

                    # Replace first loose p with hblock, remove rest
                    loose[0].replace_with(hblock)
                    for p in loose[1:]:
                        p.decompose()
                    changes += 1
                else:
                    # Fallback: wrap all in analysis-note
                    note = soup.new_tag('div', **{'class': 'analysis-note'})
                    loose[0].insert_before(note)
                    for p in loose:
                        note.append(p.extract())
                    changes += 1

    elif path == 'Daeefa/15/4.html':
        # 11 loose <p>: online debate content → wrap in analysis-note
        article = soup.select_one('.article-body')
        if article:
            loose = [t for t in article.children
                     if isinstance(t, Tag) and t.name == 'p']
            if loose:
                note = soup.new_tag('div', **{'class': 'analysis-note'})
                loose[0].insert_before(note)
                for p in loose:
                    note.append(p.extract())
                changes += 1

    elif path == 'Daeefa/15/6.html':
        # 6 loose <p>: news article content → wrap in analysis-note
        article = soup.select_one('.article-body')
        if article:
            loose = [t for t in article.children
                     if isinstance(t, Tag) and t.name == 'p']
            if loose:
                note = soup.new_tag('div', **{'class': 'analysis-note'})
                loose[0].insert_before(note)
                for p in loose:
                    note.append(p.extract())
                changes += 1

    elif path == 'Daeefa/18.html':
        # 8 loose <p> after last hadith-block → analysis commentary
        # These are inside the article-body (or container) after all hadith-blocks
        # Find last hadith-block and append analysis-note div after it
        all_blocks = soup.select('.hadith-block')
        if all_blocks:
            last_block = all_blocks[-1]
            # Collect loose p siblings after last block
            loose = []
            for sib in last_block.next_siblings:
                if isinstance(sib, Tag) and sib.name == 'p':
                    loose.append(sib)
            if loose:
                note = soup.new_tag('div', **{'class': 'analysis-note'})
                loose[0].insert_before(note)
                for p in loose:
                    note.append(p.extract())
                changes += 1

    # Also run HADITH_IN_CI for remaining blocks in files with many instances
    # (other files where global pass handles them)
    if path in ('Daeefa/2.html', 'Daeefa/4.html', 'Daeefa/5.html', 'Daeefa/7.html',
                'Daeefa/11.html', 'Daeefa/12.html', 'Daeefa/16.html', 'Daeefa/17.html',
                'Daeefa/19.html'):
        # These files had HADITH_IN_CI where ht already exists → add hadith-number if missing
        for b in soup.select('.hadith-block'):
            ht = b.select_one('.hadith-text')
            if not ht:
                continue
            if ht.select_one('.hadith-number'):
                continue
            for ci in b.select('.chapter-info'):
                txt = ci.get_text(strip=True)
                m = re.match(r'^-\s*(\d+)\s*-', txt)
                if m:
                    hadith_num = m.group(1).strip()
                    hn = soup.new_tag('span', **{'class': 'hadith-number'})
                    hn.string = hadith_num
                    ht.insert(0, hn)
                    changes += 1
                    # Update ci to remove number prefix
                    rest = re.sub(r'^-\s*\d+\s*-\s*', '', txt).strip()
                    if rest:
                        ci.clear()
                        ci.append('- ' + rest)
                        changes += 1
                    break

    # Global pass: wrap all unspanned editorial notes
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
    paths = sorted(
        glob.glob('Daeefa/*.html') + glob.glob('Daeefa/15/*.html')
    )
    # Deduplicate
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
