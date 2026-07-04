#!/usr/bin/env python3
"""Cleanup script for Threef folder - fix all data quality issues."""

import glob
import re
from bs4 import BeautifulSoup, NavigableString, Tag

EDITORIAL_TEXT = 'النص طويل لذا استقطع منه موضع الشاهد'
EDITORIAL_PATTERN = re.compile(r'\[?\s*النص طويل لذا استقطع منه موضع الشاهد\s*\]?')
HADITH_IN_CI_RE = re.compile(r'^-\s*(\d+)\s*-\s*(.+)', re.DOTALL)

changes = 0


def new_tag(soup, name, **attrs):
    return soup.new_tag(name, **attrs)


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
    """Extract hadith number+text from ci, create/extend hadith-text div."""
    global changes
    ci_text = ci_element.get_text(strip=True)
    m = HADITH_IN_CI_RE.match(ci_text)
    if not m:
        print(f"  WARNING: no match for: {ci_text[:60]}")
        return
    hadith_num = m.group(1).strip()
    hadith_text_content = m.group(2).strip()
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
    p.string = hadith_text_content
    ht.append(p)
    changes += 1


def move_bt_to_hadith_text(block, soup, new_book_title):
    """Move book-title content to hadith-text, set book-title to new_book_title."""
    global changes
    bt = block.select_one('.book-title')
    if not bt:
        return
    bt_content = bt.get_text(strip=True)
    bt.clear()
    bt.append(new_book_title)
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
    p = soup.new_tag('p')
    p.string = bt_content
    ht.append(p)
    changes += 1


def make_hadith_block(soup, scholar, book, chapter_infos, juz, page, hadith_num, hadith_paras):
    """Build a complete hadith-block div."""
    block = soup.new_tag('div', **{'class': 'hadith-block'})
    # scholar-name
    sn_div = soup.new_tag('div', **{'class': 'scholar-name'})
    sn_div.string = scholar
    block.append(sn_div)
    # book-info
    bi_div = soup.new_tag('div', **{'class': 'book-info'})
    bt_span = soup.new_tag('span', **{'class': 'book-title'})
    bt_span.string = book
    bi_div.append(bt_span)
    for ci_text in chapter_infos:
        ci_span = soup.new_tag('span', **{'class': 'chapter-info'})
        ci_span.string = ci_text
        bi_div.append(ci_span)
    block.append(bi_div)
    # ref-info
    if juz or page:
        ri_div = soup.new_tag('div', **{'class': 'ref-info'})
        if juz:
            outer = soup.new_tag('span')
            rl = soup.new_tag('span', **{'class': 'ref-label'})
            rl.string = 'الجزء: '
            rv = soup.new_tag('span', **{'class': 'ref-value'})
            rv.string = str(juz)
            outer.append(rl); outer.append(rv)
            ri_div.append(outer)
        if page:
            outer = soup.new_tag('span')
            rl = soup.new_tag('span', **{'class': 'ref-label'})
            rl.string = 'الصفحة: '
            rv = soup.new_tag('span', **{'class': 'ref-value'})
            rv.string = str(page)
            outer.append(rl); outer.append(rv)
            ri_div.append(outer)
        block.append(ri_div)
    # hadith-text
    if hadith_paras:
        ht_div = soup.new_tag('div', **{'class': 'hadith-text'})
        if hadith_num:
            hn = soup.new_tag('span', **{'class': 'hadith-number'})
            hn.string = str(hadith_num)
            ht_div.append(hn)
        for para in hadith_paras:
            p = soup.new_tag('p')
            p.string = para
            ht_div.append(p)
        block.append(ht_div)
    return block


def fix_1bkhari(soup):
    """Fix 1Bkhari.html specific blocks."""
    global changes
    blocks = soup.select('.hadith-block')

    # b2: sn=3743; scholar=البخاري, book=صحيح البخاري
    b = blocks[1]
    sn = b.select_one('.scholar-name')
    bt = b.select_one('.book-title')
    bt_text = bt.get_text(strip=True)
    cis = b.select('.chapter-info')

    # Merge bt + ci2 into hadith text (ci2 continues the Quran verse)
    full_text = bt_text
    if len(cis) >= 2:
        ci2_text = cis[1].get_text(strip=True).lstrip('- ')
        full_text = bt_text + ' ' + ci2_text
        cis[1].decompose()
        changes += 1

    sn.clear(); sn.append('البخاري'); changes += 1
    bt.clear(); bt.append('صحيح البخاري'); changes += 1
    ref = b.select_one('.ref-info')
    ht = soup.new_tag('div', **{'class': 'hadith-text'})
    hn = soup.new_tag('span', **{'class': 'hadith-number'}); hn.string = '3743'
    p = soup.new_tag('p'); p.string = full_text
    ht.append(hn); ht.append(p)
    if ref: ref.insert_after(ht)
    else: b.append(ht)
    changes += 2

    # b7: sn=صحيح البخاري; bt=hadith text starting with 5060
    b = blocks[6]
    sn = b.select_one('.scholar-name')
    bt = b.select_one('.book-title')
    bt_text = bt.get_text(strip=True)
    # Extract number from start: "‏5060- حدثنا..."
    m = re.match(r'[‏\s]*(\d+)\s*-\s*(.+)', bt_text, re.DOTALL)
    hadith_num = m.group(1) if m else '5060'
    hadith_content = m.group(2) if m else bt_text

    sn.clear(); sn.append('البخاري'); changes += 1
    bt.clear(); bt.append('صحيح البخاري'); changes += 1
    ref = b.select_one('.ref-info')
    ht = soup.new_tag('div', **{'class': 'hadith-text'})
    hn = soup.new_tag('span', **{'class': 'hadith-number'}); hn.string = hadith_num
    p = soup.new_tag('p'); p.string = hadith_content
    ht.append(hn); ht.append(p)
    if ref: ref.insert_after(ht)
    else: b.append(ht)
    changes += 2


def fix_2muslem(soup):
    """Fix 2Muslem.html b2: sn=629, bt=hadith text."""
    global changes
    blocks = soup.select('.hadith-block')
    b = blocks[1]  # b2
    sn = b.select_one('.scholar-name')
    bt = b.select_one('.book-title')
    bt_text = bt.get_text(strip=True)

    sn.clear(); sn.append('مسلم'); changes += 1
    bt.clear(); bt.append('صحيح مسلم'); changes += 1
    ref = b.select_one('.ref-info')
    ht = soup.new_tag('div', **{'class': 'hadith-text'})
    hn = soup.new_tag('span', **{'class': 'hadith-number'}); hn.string = '629'
    p = soup.new_tag('p'); p.string = bt_text
    ht.append(hn); ht.append(p)
    if ref: ref.insert_after(ht)
    else: b.append(ht)
    changes += 2


def fix_4termithee(soup):
    """Fix 4Termithee.html b1: scholar-name inside book-info, HADITH_IN_CI."""
    global changes
    blocks = soup.select('.hadith-block')
    b = blocks[0]  # b1
    bi = b.select_one('.book-info')
    sn_inside = bi.select_one('.scholar-name') if bi else None

    if sn_inside:
        # Move scholar-name before book-info
        sn_inside.extract()
        bi.insert_before(sn_inside)
        changes += 1

    # Fix first chapter-info: "- سنن الترمذي - كتابالرضاع" → "- كتاب الرضاع"
    cis = b.select('.chapter-info')
    if cis:
        ci1_text = cis[0].get_text(strip=True)
        # Remove redundant book title prefix
        m = re.match(r'-\s*سنن الترمذي\s*-\s*(.+)', ci1_text)
        if m:
            chapter_part = m.group(1).strip()
            # Fix typo: "كتابالرضاع" → "كتاب الرضاع"
            chapter_part = re.sub(r'كتاب([^\s])', r'كتاب \1', chapter_part)
            cis[0].clear()
            cis[0].append(f'- {chapter_part}')
            changes += 1

    # Fix third chapter-info: HADITH_IN_CI
    cis = b.select('.chapter-info')
    for ci in cis:
        if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
            fix_hadith_in_ci(b, soup, ci)
            break


def fix_11hythami(soup):
    """Fix 11Hythami.html b2, b3, b4: HADITH_IN_CI."""
    blocks = soup.select('.hadith-block')
    for bn in [1, 2, 3]:  # 0-indexed b2, b3, b4
        b = blocks[bn]
        for ci in b.select('.chapter-info'):
            if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
                fix_hadith_in_ci(b, soup, ci)
                break


def fix_16syooti_b21(soup):
    """Fix 16Syooti.html b21: combined sn, bt=Quran verse ref."""
    global changes
    blocks = soup.select('.hadith-block')
    b = blocks[20]  # b21
    sn = b.select_one('.scholar-name')
    bt = b.select_one('.book-title')
    bt_text = bt.get_text(strip=True)  # "الأحزاب : 25"

    # Split sn: "السيوطي -الدر المنثور في التفسير بالمأثور"
    sn_text = sn.get_text(strip=True)
    m = re.match(r'(.+?)\s*-\s*(.+)', sn_text)
    if m:
        scholar = m.group(1).strip()
        book = m.group(2).strip()
        sn.clear(); sn.append(scholar); changes += 1
        bt.clear(); bt.append(book); changes += 1
        # bt "الأحزاب : 25" → chapter-info
        bi = b.select_one('.book-info')
        ci = soup.new_tag('span', **{'class': 'chapter-info'})
        ci.string = f'تفسير سورة {bt_text}'
        bi.append(ci)
        changes += 1


def fix_22ibnasaker(soup):
    """Fix 22IbnAsaker.html b1, b2, b3: bt=narrator chain."""
    blocks = soup.select('.hadith-block')
    for bn in [0, 1, 2]:  # b1, b2, b3
        b = blocks[bn]
        bt = b.select_one('.book-title')
        if bt:
            bt_text = bt.get_text(strip=True)
            if 'أخبرنا' in bt_text or 'حدثنا' in bt_text or 'أنبأنا' in bt_text:
                move_bt_to_hadith_text(b, soup, 'تاريخ دمشق')


def fix_23mutqy(soup):
    """Fix 23MutqyAlhindy.html b1: HADITH_IN_CI."""
    blocks = soup.select('.hadith-block')
    b = blocks[0]
    for ci in b.select('.chapter-info'):
        if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
            fix_hadith_in_ci(b, soup, ci)
            break


def fix_24trteeb(soup):
    """Fix 24Trteeb.html b3 and b4."""
    global changes
    blocks = soup.select('.hadith-block')

    # b3: sn=772, bt=hadith text, scholar=مسلم
    b = blocks[2]
    sn = b.select_one('.scholar-name')
    bt = b.select_one('.book-title')
    bt_text = bt.get_text(strip=True)
    sn.clear(); sn.append('مسلم'); changes += 1
    bt.clear(); bt.append('صحيح مسلم'); changes += 1
    ref = b.select_one('.ref-info')
    ht = soup.new_tag('div', **{'class': 'hadith-text'})
    hn = soup.new_tag('span', **{'class': 'hadith-number'}); hn.string = '772'
    p = soup.new_tag('p'); p.string = bt_text
    ht.append(hn); ht.append(p)
    if ref: ref.insert_after(ht)
    else: b.append(ht)
    changes += 2

    # b4: sn=[النص طويل], bt=النووي; scholar=النووي, book=صحيح مسلم بشرح النووي
    b = blocks[3]
    sn = b.select_one('.scholar-name')
    bt = b.select_one('.book-title')
    bt_text = bt.get_text(strip=True)  # "النووي"
    # Book title comes from ci1: "- صحيح مسلم بشرح النووي - كتاب..."
    cis = b.select('.chapter-info')
    book = 'صحيح مسلم بشرح النووي'
    if cis:
        ci1_text = cis[0].get_text(strip=True).lstrip('- ')
        m = re.match(r'(.+?)\s*-\s*(كتاب|باب|فصل)', ci1_text)
        if m:
            book = m.group(1).strip()
            # Update ci1 to remove book prefix
            remaining = ci1_text[len(m.group(1)):].strip()
            cis[0].clear(); cis[0].append(remaining); changes += 1

    sn.clear(); sn.append(bt_text); changes += 1
    bt.clear(); bt.append(book); changes += 1

    # Add editorial note to hadith-text if not present
    ht = b.select_one('.hadith-text')
    if ht:
        has_editorial = any(
            p.select_one('.editorial-note') or EDITORIAL_PATTERN.search(p.get_text())
            for p in ht.select('p')
        )
        if not has_editorial:
            ep = make_editorial_p(soup)
            ht.insert(0, ep)
            changes += 1


def fix_25rayelshia(soup):
    """Fix 25RayelShia.html: b23 + 11 loose <p>."""
    global changes
    blocks = soup.select('.hadith-block')
    ab = soup.select_one('.article-body')

    # b23: sn="المحقق الكلباسي -البيان في تفسير القرآن", bt=hadith text
    b = blocks[22]  # b23
    sn = b.select_one('.scholar-name')
    bt = b.select_one('.book-title')
    sn_text = sn.get_text(strip=True)
    bt_text = bt.get_text(strip=True)

    m = re.match(r'(.+?)\s*-\s*(.+)', sn_text)
    if m:
        sn.clear(); sn.append(m.group(1).strip()); changes += 1
        bt.clear(); bt.append(m.group(2).strip()); changes += 1
    else:
        bt.clear(); bt.append('البيان في تفسير القرآن'); changes += 1

    # Move original bt text (hadith content) to hadith-text
    ref = b.select_one('.ref-info')
    ht = soup.new_tag('div', **{'class': 'hadith-text'})
    p = soup.new_tag('p'); p.string = bt_text
    ht.append(p)
    if ref: ref.insert_after(ht)
    else: b.append(ht)
    changes += 1

    # Fix loose <p> tags
    loose_ps = [c for c in ab.children if isinstance(c, Tag) and c.name == 'p']

    # We need to insert new hadith-blocks in place of loose <p> groups
    # Group A: p1, p2 (العلامة الحلي / نهاية الأصول)
    # Group B: p3 (الحر العاملي)
    # Group C: p4, p5, p6 (البلاغي / آلاء الرحمن)
    # Group D: p7(sep), p8, p9, p10, p11 (علم الهدى / السيد المرتضى)

    if len(loose_ps) >= 11:
        p1, p2 = loose_ps[0], loose_ps[1]
        p3 = loose_ps[2]
        p4, p5, p6 = loose_ps[3], loose_ps[4], loose_ps[5]
        p7, p8, p9, p10, p11 = loose_ps[6], loose_ps[7], loose_ps[8], loose_ps[9], loose_ps[10]

        # Group A: العلامة الحلي
        sn1_text = p1.get_text(strip=True)  # "العلامة الحلي -نهاية الأصول مبحث التواتر"
        m1 = re.match(r'(.+?)\s*-\s*(.+?)\s+(\S.+)', sn1_text)
        if m1:
            sn1 = m1.group(1).strip()
            bt1 = m1.group(2).strip()
            ci1_list = [m1.group(3).strip()]
        else:
            parts = sn1_text.split(' -')
            sn1 = parts[0].strip()
            bt1 = parts[1].strip() if len(parts) > 1 else ''
            ci1_list = []

        block_a = make_hadith_block(soup, sn1, bt1, ci1_list, None, None, None,
                                    [p2.get_text(strip=True)])
        p1.insert_before(block_a); changes += 1
        p1.decompose(); p2.decompose(); changes += 2

        # Group B: الحر العاملي
        p3_text = p3.get_text(strip=True)
        # Format: "- الشيخ محمد بن الحسن الحر العاملي : ومن له تتبع..."
        m3 = re.match(r'-\s*(.+?)\s*:\s*(.+)', p3_text, re.DOTALL)
        if m3:
            sn3 = m3.group(1).strip()
            ht3 = '- ' + m3.group(2).strip()
        else:
            sn3 = 'الشيخ محمد بن الحسن الحر العاملي'
            ht3 = p3_text

        block_b = make_hadith_block(soup, sn3, '', [], None, None, None, [ht3])
        p3.insert_before(block_b); changes += 1
        p3.decompose(); changes += 1

        # Group C: البلاغي
        sn4_text = p4.get_text(strip=True)  # "الشيخ البلاغي -آلاء الرحمن"
        m4 = re.match(r'(.+?)\s*-\s*(.+)', sn4_text)
        sn4 = m4.group(1).strip() if m4 else sn4_text
        bt4 = m4.group(2).strip() if m4 else ''
        ci4 = p5.get_text(strip=True)  # "الفصل الثالث من المقدمة"
        ht4 = p6.get_text(strip=True)  # "- : ومن أجل تواتر القرآن..."

        block_c = make_hadith_block(soup, sn4, bt4, [ci4], None, None, None, [ht4])
        p4.insert_before(block_c); changes += 1
        p4.decompose(); p5.decompose(); p6.decompose(); changes += 3

        # Group D: السيد المرتضى
        # p7 is "-" separator (skip but decompose)
        p8_text = p8.get_text(strip=True)
        # "المرتضى علي بن الحسين علم الهدى : المتوفي في 436 - قال : في رسالته..."
        m8 = re.match(r'(.+?)\s*[-:]\s*المتوفي.+?-\s*قال\s*:\s*(.+)', p8_text, re.DOTALL)
        if m8:
            sn8 = m8.group(1).strip()
            intro_text = m8.group(2).strip()
        else:
            sn8 = 'السيد المرتضى'
            intro_text = p8_text

        ht8_paras = [intro_text] if intro_text else []
        ht8_paras.append(p9.get_text(strip=True))
        ht8_paras.append(p10.get_text(strip=True))
        # p11: "مجمع البيان - الجزء : ( 1 ) - رقم الصفحة : ( 15 ) وهذا قول صريح واضح."
        ht8_paras.append(p11.get_text(strip=True))

        block_d = make_hadith_block(soup, sn8, 'المسائل الطرابلسيات', [], None, None, None, ht8_paras)
        p7.insert_before(block_d); changes += 1
        p7.decompose(); p8.decompose(); p9.decompose(); p10.decompose(); p11.decompose()
        changes += 5


def fix_26shia(soup):
    """Fix 26ShiaWlQuran.html: b3, b16."""
    global changes
    blocks = soup.select('.hadith-block')

    # b3: أحمد البرقي + المحاسن, HADITH_IN_CI
    b = blocks[2]
    for ci in b.select('.chapter-info'):
        if HADITH_IN_CI_RE.match(ci.get_text(strip=True)):
            fix_hadith_in_ci(b, soup, ci)
            break

    # b16: sn="الشيخ الصدوق- عيونأخبار الرضا", bt=hadith text
    if len(blocks) >= 16:
        b = blocks[15]
        sn = b.select_one('.scholar-name')
        bt = b.select_one('.book-title')
        sn_text = sn.get_text(strip=True)
        bt_text = bt.get_text(strip=True)

        # Split sn: "الشيخ الصدوق- عيونأخبار الرضا" → scholar / book
        m = re.match(r'(.+?)\s*-\s*(.+)', sn_text)
        if m:
            scholar = m.group(1).strip()
            book = m.group(2).strip()
            # Fix typo: "عيونأخبار" → "عيون أخبار"
            book = re.sub(r'([^\s])أ', r'\1 أ', book)
        else:
            scholar = sn_text
            book = 'عيون أخبار الرضا'

        sn.clear(); sn.append(scholar); changes += 1
        bt.clear(); bt.append(book); changes += 1

        # Move original bt_text to hadith-text
        ref = b.select_one('.ref-info')
        ht = soup.new_tag('div', **{'class': 'hadith-text'})
        p = soup.new_tag('p'); p.string = bt_text
        ht.append(p)
        if ref: ref.insert_after(ht)
        else: b.append(ht)
        changes += 1


def fix_27taleefat(soup):
    """Fix 27Taleefat.html: wrap 48 loose <p> in analysis-note div."""
    global changes
    ab = soup.select_one('.article-body')
    loose = [c for c in list(ab.children) if isinstance(c, Tag) and c.name == 'p']
    if not loose:
        return

    # Wrap all loose <p> in a single analysis-note div
    wrapper = soup.new_tag('div', **{'class': 'analysis-note'})
    # Insert wrapper before first loose <p>
    loose[0].insert_before(wrapper)
    for p in loose:
        p.extract()
        wrapper.append(p)
        changes += 1


def process_file(path):
    global changes
    with open(path, encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    prev = changes

    if 'Threef/1Bkhari.html' in path:
        fix_1bkhari(soup)
    elif 'Threef/2Muslem.html' in path:
        fix_2muslem(soup)
    elif 'Threef/4Termithee.html' in path:
        fix_4termithee(soup)
    elif 'Threef/11Hythami.html' in path:
        fix_11hythami(soup)
    elif 'Threef/16Syooti.html' in path:
        fix_16syooti_b21(soup)
    elif 'Threef/22IbnAsaker.html' in path:
        fix_22ibnasaker(soup)
    elif 'Threef/23MutqyAlhindy.html' in path:
        fix_23mutqy(soup)
    elif 'Threef/24Trteeb.html' in path:
        fix_24trteeb(soup)
    elif 'Threef/25RayelShia.html' in path:
        fix_25rayelshia(soup)
    elif 'Threef/26ShiaWlQuran.html' in path:
        fix_26shia(soup)
    elif 'Threef/27Taleefat.html' in path:
        fix_27taleefat(soup)

    # Global pass: wrap editorial notes
    wrap_editorial_notes(soup)

    new_content = str(soup)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Updated: {path} ({changes - prev} changes)")
    else:
        print(f"  No changes: {path}")


def main():
    paths = sorted(glob.glob('Threef/*.html') + glob.glob('Threef/**/*.html', recursive=True))
    seen = set()
    paths = [p for p in paths if not (p in seen or seen.add(p))]

    for path in paths:
        if 'Main132' in path:
            continue
        process_file(path)

    print(f"\nTotal changes: {changes}")


if __name__ == '__main__':
    main()
