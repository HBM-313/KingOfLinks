"""
Comprehensive fix script for Hywan folder.
All fixes verified against live pages fetched from kingoflinks.net.
"""
from bs4 import BeautifulSoup
import os

EDITORIAL_TEXT = 'النص طويل لذا استقطع منه موضع الشاهد'

def load(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return BeautifulSoup(f, 'html.parser')

def save(soup, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(str(soup))

def wrap_editorial_in_ht(soup):
    count = 0
    for ht in soup.find_all('div', class_='hadith-text'):
        for p in ht.find_all('p'):
            text = p.get_text(strip=True)
            if EDITORIAL_TEXT in text and not p.find('span', class_='editorial-note'):
                clean = text.strip('[]').strip()
                p.clear()
                span = soup.new_tag('span', attrs={'class': 'editorial-note'})
                span.string = clean
                p.append(span)
                count += 1
    return count

def make_editorial_p(soup):
    p = soup.new_tag('p')
    span = soup.new_tag('span', attrs={'class': 'editorial-note'})
    span.string = EDITORIAL_TEXT
    p.append(span)
    return p

# ─── 2Bqrah.html ───────────────────────────────────────────────────────────
# b1: scholar-name nested inside book-info (structural)
# b2: EDITORIAL_IN_SN → scholar=مسلم, book=صحيح مسلم (already in bt)
# b9: UNWRAPPED_EDITORIAL
print('Fixing 2Bqrah.html...')
soup = load('Hywan/2Bqrah.html')
blocks = soup.find_all('div', class_='hadith-block')

b1 = blocks[0]
bi1 = b1.find('div', class_='book-info')
sn1 = bi1.find('div', class_='scholar-name') if bi1 else None
if sn1:
    sn1.extract()
    bi1.insert_before(sn1)
    print('  b1: structural fix - scholar-name moved out of book-info')

b2 = blocks[1]
sn2 = b2.find('div', class_='scholar-name')
if sn2 and EDITORIAL_TEXT in sn2.get_text():
    sn2.string = 'مسلم'
    ht2 = b2.find('div', class_='hadith-text')
    if ht2:
        ht2.insert(0, make_editorial_p(soup))
    print('  b2: EDITORIAL_IN_SN fixed → مسلم')

n = wrap_editorial_in_ht(soup)
print(f'  {n} editorial wraps')
save(soup, 'Hywan/2Bqrah.html')

# ─── 7Qerd.html ────────────────────────────────────────────────────────────
# b1: sn = page topic "(القردة التي زنت...)" → set to البخاري; bt already = صحيح البخاري
# b4: sn = "القرطبي -تفسير القرطبي = الجامع لأحكام القرآن" (Pattern O) → split;
#     bt has "سورة البقرة : 65" → this is chapter-info not book title; book = تفسير القرطبي = الجامع لأحكام القرآن
# b5: sn = long description of عمرو بن ميمون → scholar=الأصبهاني; bt already has الأصبهاني? No:
#     bt = "الأصبهاني" + chapter. So set sn=الأصبهاني, move long text to hadith-text first p
# b7: EDITORIAL_IN_SN → scholar=المزي, bt already = المزي → set sn=المزي
# b9: EDITORIAL_IN_SN → scholar=الباجي, bt already = الباجي → set sn=الباجي
# Also: b4 UNWRAPPED_EDITORIAL (checked: no, only b2,b4,b8,b10: UNWRAPPED from inspection)
# Inspection said: b2 UNWRAPPED_EDITORIAL, b4 UNWRAPPED_EDITORIAL, b6 HADITH_IN_CI (false positive),
#   b7 EDITORIAL_IN_SN + HADITH_IN_CI (false positive), b8 UNWRAPPED_EDITORIAL,
#   b9 EDITORIAL_IN_SN, b10 HADITH_IN_CI (false positive) + UNWRAPPED_EDITORIAL
print('Fixing 7Qerd.html...')
soup = load('Hywan/7Qerd.html')
blocks = soup.find_all('div', class_='hadith-block')

# b1: page topic in sn → set to البخاري
b1 = blocks[0]
sn1 = b1.find('div', class_='scholar-name')
if sn1 and 'القردة' in sn1.get_text():
    sn1.string = 'البخاري'
    print('  b1: page topic removed, set scholar=البخاري')

# b4 (index 3): COMBINED sn "القرطبي -تفسير القرطبي = الجامع لأحكام القرآن"
b4 = blocks[3]
sn4 = b4.find('div', class_='scholar-name')
bt4 = b4.find('span', class_='book-title')
ci4_tags = b4.find_all('span', class_='chapter-info')
if sn4 and ' -' in sn4.get_text():
    full4 = sn4.get_text(strip=True)
    idx4 = full4.index(' -')
    sn4.string = full4[:idx4].strip()       # القرطبي
    book_part4 = full4[idx4+2:].strip()     # تفسير القرطبي = الجامع لأحكام القرآن
    # bt4 currently has "سورة البقرة : 65" which is chapter context
    if bt4:
        old_bt4 = bt4.get_text(strip=True)  # سورة البقرة : 65
        bt4.string = book_part4
        # Move old bt to chapter-info
        bi4 = b4.find('div', class_='book-info')
        new_ci4 = soup.new_tag('span', attrs={'class': 'chapter-info'})
        new_ci4.string = '- ' + old_bt4
        # Insert before existing chapter-infos or at end of book-info
        if ci4_tags:
            ci4_tags[0].insert_before(new_ci4)
        else:
            bi4.append(new_ci4)
    print('  b4: COMBINED_SN fixed → القرطبي / تفسير القرطبي...')

# b5 (index 4): sn = long biography text, real scholar = الأصبهاني
b5 = blocks[4]
sn5 = b5.find('div', class_='scholar-name')
bt5 = b5.find('span', class_='book-title')
if sn5 and 'أدرك الجاهلية' in sn5.get_text():
    # The long bio text was originally in sn; bt has "الأصبهاني"
    bio_text = sn5.get_text(strip=True)
    bt5_text = bt5.get_text(strip=True) if bt5 else ''
    sn5.string = bt5_text  # set scholar = الأصبهاني
    # bt5 should be the book title: معرفة الصحابة (from chapter-info context)
    if bt5:
        bt5.string = 'معرفة الصحابة'
    # Move bio text to hadith-text as first p (it's part of the entry context)
    ht5 = b5.find('div', class_='hadith-text')
    if ht5:
        bio_p = soup.new_tag('p')
        bio_p.string = bio_text
        ht5.insert(0, bio_p)
    print('  b5: EDITORIAL_IN_SN fixed → الأصبهاني / معرفة الصحابة')

# b7 (index 6): EDITORIAL_IN_SN → scholar=المزي, bt already = المزي
b7 = blocks[6]
sn7 = b7.find('div', class_='scholar-name')
bt7 = b7.find('span', class_='book-title')
if sn7 and EDITORIAL_TEXT in sn7.get_text():
    bt7_text = bt7.get_text(strip=True) if bt7 else ''
    sn7.string = bt7_text  # المزي
    if bt7:
        bt7.string = 'تهذيب الكمال في أسماء الرجال'
    ht7 = b7.find('div', class_='hadith-text')
    if ht7:
        ht7.insert(0, make_editorial_p(soup))
    print('  b7: EDITORIAL_IN_SN fixed → المزي / تهذيب الكمال')

# b9 (index 8): EDITORIAL_IN_SN → scholar=الباجي, bt already = الباجي
b9 = blocks[8]
sn9 = b9.find('div', class_='scholar-name')
bt9 = b9.find('span', class_='book-title')
if sn9 and EDITORIAL_TEXT in sn9.get_text():
    bt9_text = bt9.get_text(strip=True) if bt9 else ''
    sn9.string = bt9_text  # الباجي
    if bt9:
        bt9.string = 'التعديل والتجريح لمن خرج له البخاري في الجامع الصحيح'
    ht9 = b9.find('div', class_='hadith-text')
    if ht9:
        ht9.insert(0, make_editorial_p(soup))
    print('  b9: EDITORIAL_IN_SN fixed → الباجي / التعديل والتجريح')

n = wrap_editorial_in_ht(soup)
print(f'  {n} editorial wraps')
save(soup, 'Hywan/7Qerd.html')

# ─── 11Ghanam.html ─────────────────────────────────────────────────────────
print('Fixing 11Ghanam.html...')
soup = load('Hywan/11Ghanam.html')
blocks = soup.find_all('div', class_='hadith-block')

# b1: sn = "المقريزي- إمتاع الأسماع..." (Pattern O combined in sn)
b1 = blocks[0]
sn1 = b1.find('div', class_='scholar-name')
if sn1 and '- ' in sn1.get_text(strip=True):
    full = sn1.get_text(strip=True)
    parts = full.split('- ', 1)
    sn1.string = parts[0].strip()         # المقريزي
    bt1 = b1.find('span', class_='book-title')
    bi1 = b1.find('div', class_='book-info')
    if bt1:
        old_bt1 = bt1.get_text(strip=True)  # فصل : جامع في معجزات...
        bt1.string = parts[1].strip()       # إمتاع الأسماع...
        new_ci1 = soup.new_tag('span', attrs={'class': 'chapter-info'})
        new_ci1.string = '- ' + old_bt1
        ci1s = b1.find_all('span', class_='chapter-info')
        if ci1s:
            ci1s[0].insert_before(new_ci1)
        else:
            bi1.append(new_ci1)
    print('  b1: COMBINED_SN fixed → المقريزي / إمتاع الأسماع')

# b2: bt = "البداية والنهاية -سنة احدى عشرة من الهجرة" → split
b2 = blocks[1]
bt2 = b2.find('span', class_='book-title')
if bt2 and ' -' in bt2.get_text(strip=True):
    bt2_text = bt2.get_text(strip=True)
    idx2 = bt2_text.index(' -')
    book2 = bt2_text[:idx2].strip()
    chap2 = bt2_text[idx2:].strip()
    bt2.string = book2
    bi2 = b2.find('div', class_='book-info')
    new_ci2 = soup.new_tag('span', attrs={'class': 'chapter-info'})
    new_ci2.string = chap2
    ci2s = b2.find_all('span', class_='chapter-info')
    if ci2s:
        ci2s[0].insert_before(new_ci2)
    else:
        bi2.append(new_ci2)
    print('  b2: COMBINED_BT fixed → البداية والنهاية / سنة احدى عشرة')

# b6: sn = "الصالحي الشامي- سبل الهدى..." (Pattern O)
b6 = blocks[5]
sn6 = b6.find('div', class_='scholar-name')
if sn6 and '- ' in sn6.get_text(strip=True):
    full6 = sn6.get_text(strip=True)
    parts6 = full6.split('- ', 1)
    sn6.string = parts6[0].strip()
    bt6 = b6.find('span', class_='book-title')
    bi6 = b6.find('div', class_='book-info')
    if bt6:
        old_bt6 = bt6.get_text(strip=True)
        bt6.string = parts6[1].strip()
        new_ci6 = soup.new_tag('span', attrs={'class': 'chapter-info'})
        new_ci6.string = '- ' + old_bt6
        ci6s = b6.find_all('span', class_='chapter-info')
        if ci6s:
            ci6s[0].insert_before(new_ci6)
        else:
            bi6.append(new_ci6)
    print('  b6: COMBINED_SN fixed → الصالحي الشامي / سبل الهدى')

# b7: EDITORIAL_IN_SN → bt = "الحلبي- السيرة الحلبية" → split
b7 = blocks[6]
sn7 = b7.find('div', class_='scholar-name')
bt7 = b7.find('span', class_='book-title')
if sn7 and EDITORIAL_TEXT in sn7.get_text():
    bt7_text = bt7.get_text(strip=True) if bt7 else ''
    if '- ' in bt7_text:
        p7 = bt7_text.split('- ', 1)
        sn7.string = p7[0].strip()
        if bt7: bt7.string = p7[1].strip()
    else:
        sn7.string = bt7_text
    ht7 = b7.find('div', class_='hadith-text')
    if ht7:
        ht7.insert(0, make_editorial_p(soup))
    print('  b7: EDITORIAL_IN_SN fixed → الحلبي / السيرة الحلبية')

n = wrap_editorial_in_ht(soup)
print(f'  {n} editorial wraps')
save(soup, 'Hywan/11Ghanam.html')

# ─── 3Dhab.html: only UNWRAPPED_EDITORIAL (HADITH_IN_CI are false positives) ──
print('Fixing 3Dhab.html...')
soup = load('Hywan/3Dhab.html')
n = wrap_editorial_in_ht(soup)
print(f'  {n} editorial wraps')
save(soup, 'Hywan/3Dhab.html')

# ─── Pure editorial-only files ──────────────────────────────────────────────
for fn in ['Hywan/1Asd.html', 'Hywan/4Dhbyah.html', 'Hywan/5Hmar.html',
           'Hywan/6Jmal.html', 'Hywan/8Theb.html', 'Hywan/9Tyoor.html',
           'Hywan/12Other.html']:
    soup = load(fn)
    n = wrap_editorial_in_ht(soup)
    if n:
        save(soup, fn)
        print(f'Fixed {fn}: {n} editorial wraps')
    else:
        print(f'No changes needed: {fn}')

print('\nAll Hywan fixes applied.')
