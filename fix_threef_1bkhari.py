"""
Fix Threef/1Bkhari.html - complex multi-block issues verified against live page.

Live page structure:
b1: صحيح البخاري - كتاب الأحكام - باب : الشهادة تكون عند الحاكم... ج9/ص69
b2: صحيح البخاري - كتاب فضائل الصحابة - باب : مناقب عمار وحذيفة (ر) ج5/ص25 [hadith #3743]
b3: صحيح البخاري - كتاب فضائل الصحابة - باب : مناقب عبد الله بن مسعود (ر) ج5/ص28 [hadith #3761]
b4: صحيح البخاري - كتاب تفسير القرآن - سورة : { وَاللَّيْلِ... (الليل:1-2)} ج6/ص170 [hadith #4943]
b5: صحيح البخاري - كتاب تفسير القرآن - سورة : { قُلْ أَعُوذُ... (الناس:1) } ج6/ص181 [hadith #4977]
b6: صحيح البخاري - كتاب فضائل القرآن - باب : أنزل القرآن على سبعة أحرف ج6/ص184 [hadith #4992]
b7: صحيح البخاري - كتاب فضائل القرآن - باب : إقرءوا القرآن ما ائتلفت... ج6/ص198 [hadith #5060]
b8: صحيح البخاري - كتاب الحدود - باب : الاعتراف بالزنا ج8/ص168 [hadith #6829]
b9: صحيح البخاري - كتاب الحدود - باب : رجم الحبلى من الزنا إذا أحصنت ج8/ص168 [editorial + hadith #6830]
b10: صحيح البخاري - كتاب الاعتصام - باب : ما ذكر النبي (ص)... ج9/ص103 [hadith #7323]
b11: صحيح البخاري - كتاب التوحيد - باب : قول الله تعالى { فَاقْرَءُوا... (المزمل:20)} ج9/ص159 [hadith #7550]
"""
from bs4 import BeautifulSoup

EDITORIAL_TEXT = 'النص طويل لذا استقطع منه موضع الشاهد'

with open('Threef/1Bkhari.html', encoding='utf-8', errors='replace') as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')
blocks = soup.find_all('div', class_='hadith-block')
print(f'Total blocks: {len(blocks)}')

article = soup.find('div', class_='article-body')

def make_block(soup, scholar, book, chapter_info, ref_j, ref_s, hadith_num=None, hadith_text_paras=None, editorial=False):
    """Build a clean hadith-block from scratch."""
    block = soup.new_tag('div', attrs={'class': 'hadith-block'})
    
    sn = soup.new_tag('div', attrs={'class': 'scholar-name'})
    sn.string = scholar
    block.append(sn)
    
    bi = soup.new_tag('div', attrs={'class': 'book-info'})
    bt = soup.new_tag('span', attrs={'class': 'book-title'})
    bt.string = book
    bi.append(bt)
    if chapter_info:
        ci = soup.new_tag('span', attrs={'class': 'chapter-info'})
        ci.string = '- ' + chapter_info if not chapter_info.startswith('-') else chapter_info
        bi.append(ci)
    block.append(bi)
    
    ri = soup.new_tag('div', attrs={'class': 'ref-info'})
    j_span = soup.new_tag('span')
    jl = soup.new_tag('span', attrs={'class': 'ref-label'}); jl.string = 'الجزء: '
    jv = soup.new_tag('span', attrs={'class': 'ref-value'}); jv.string = ref_j
    j_span.append(jl); j_span.append(jv)
    s_span = soup.new_tag('span')
    sl = soup.new_tag('span', attrs={'class': 'ref-label'}); sl.string = 'الصفحة: '
    sv = soup.new_tag('span', attrs={'class': 'ref-value'}); sv.string = ref_s
    s_span.append(sl); s_span.append(sv)
    ri.append(j_span); ri.append(s_span)
    block.append(ri)
    
    ht = soup.new_tag('div', attrs={'class': 'hadith-text'})
    if hadith_num:
        hn = soup.new_tag('span', attrs={'class': 'hadith-number'})
        hn.string = hadith_num
        ht.append(hn)
    if editorial:
        ep = soup.new_tag('p')
        es = soup.new_tag('span', attrs={'class': 'editorial-note'})
        es.string = EDITORIAL_TEXT
        ep.append(es)
        ht.append(ep)
    if hadith_text_paras:
        for text in hadith_text_paras:
            p = soup.new_tag('p')
            p.string = text
            ht.append(p)
    block.append(ht)
    return block

# Extract existing hadith texts from current blocks
def get_ht_text(block):
    ht = block.find('div', class_='hadith-text')
    if not ht: return []
    return [p.get_text(strip=True) for p in ht.find_all('p') if p.get_text(strip=True)]

def get_hadith_num(block):
    hn = block.find('span', class_='hadith-number')
    return hn.get_text(strip=True) if hn else None

# Gather texts from existing blocks
b1_text = get_ht_text(blocks[0])
b2_text = get_ht_text(blocks[1]) if len(blocks) > 1 else []
b3_text = get_ht_text(blocks[2]) if len(blocks) > 2 else []
b4_text = get_ht_text(blocks[3]) if len(blocks) > 3 else []
b5_text = get_ht_text(blocks[4]) if len(blocks) > 4 else []
b6_text = get_ht_text(blocks[5]) if len(blocks) > 5 else []
b7_text = get_ht_text(blocks[6]) if len(blocks) > 6 else []
b8_text = get_ht_text(blocks[7]) if len(blocks) > 7 else []
b9_text = get_ht_text(blocks[8]) if len(blocks) > 8 else []
b10_text = get_ht_text(blocks[9]) if len(blocks) > 9 else []
b11_text = get_ht_text(blocks[10]) if len(blocks) > 10 else []

# b2 has its hadith text split across bt/ci - reconstruct from local:
# the bt had the full hadith text starting with "حدثنا : ‏ ‏سليمان..." up to chapter-info
b2 = blocks[1]
b2_bt = b2.find('span', class_='book-title')
b2_ci_tags = b2.find_all('span', class_='chapter-info')
# bt has first part: "حدثنا : سليمان بن حرب... والليل إذا يغشى @ والنهار إذا تجلى @ ( الليل : 1"
# ci[0] = "- باب : مناقب عمار وحذيفة (ر)"  <- this is the real chapter-info
# ci[1] = "- 2 ) }قلت :والذكر والأنثى ، قال : ما زال..." <- continuation of hadith text
b2_chapter = b2_ci_tags[0].get_text(strip=True).lstrip('- ').strip() if b2_ci_tags else ''
b2_hadith_full_text = (b2_bt.get_text(strip=True) if b2_bt else '') + (b2_ci_tags[1].get_text(strip=True).lstrip('- ').strip() if len(b2_ci_tags) > 1 else '')

# b4: sn has the Quranic verse (chapter context), bt has "2 ) }" (fragment)
# reconstruct: chapter = سورة : { وَاللَّيْلِ إِذَا يَغْشَى @ وَالنَّهَارِ إِذَا تَجَلَّى @ ( الليل : 1 - 2 ) }
# Live confirms chapter = "سورة : { وَاللَّيْلِ إِذَا يَغْشَى ... ( الليل : 1 - 2 ) }"
b4 = blocks[3]
b4_sn = b4.find('div', class_='scholar-name')
b4_bt = b4.find('span', class_='book-title')
b4_chapter = (b4_sn.get_text(strip=True) if b4_sn else '') + ' ' + (b4_bt.get_text(strip=True) if b4_bt else '')

# b5: sn=`صحيح البخاري -`, bt has editorial note, hadith text has the actual hadith
# bt has: "كعادته البخاري استبدل قول ابن مسعود : ( كنا نحك المعوذتين ) بكلمة : ( كذا وكذا )"
# This is actually an editorial comment, NOT hadith text in bt
b5 = blocks[4]
b5_bt = b5.find('span', class_='book-title')
b5_editorial_comment = b5_bt.get_text(strip=True) if b5_bt else ''  # this goes to hadith-text as context p
b5_hadith_text = get_ht_text(b5)

# b8: bt has editorial "[النص طويل...]" - move to hadith-text
b8 = blocks[7]
b8_bt = b8.find('span', class_='book-title')
b8_has_editorial = EDITORIAL_TEXT in (b8_bt.get_text() if b8_bt else '')

print('b2 chapter:', b2_chapter)
print('b4 chapter (reconstructed):', b4_chapter[:80])
print('b5 editorial comment:', b5_editorial_comment[:60])
print('b8 editorial in bt:', b8_has_editorial)

# Now rebuild all blocks
new_blocks = []

# b1: البخاري / صحيح البخاري / كتاب الأحكام - باب : الشهادة... / ج9/ص69
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب الأحكام - باب : الشهادة تكون عند الحاكم في ولايته القضاء أو قبل ذلك للخصم',
    '9', '69', hadith_text_paras=b1_text))

# b2: البخاري / صحيح البخاري / كتاب فضائل الصحابة - باب : مناقب عمار وحذيفة (ر) / ج5/ص25
# hadith text was split across bt+ci[1]
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب فضائل الصحابة - باب : مناقب عمار وحذيفة (ر)',
    '5', '25', hadith_num='3743',
    hadith_text_paras=[b2_hadith_full_text] if b2_hadith_full_text else []))

# b3: البخاري / صحيح البخاري / كتاب فضائل الصحابة - باب : مناقب عبد الله بن مسعود (ر) / ج5/ص28
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب فضائل الصحابة - باب : مناقب عبد الله بن مسعود (ر)',
    '5', '28', hadith_num='3761', hadith_text_paras=b3_text))

# b4: البخاري / صحيح البخاري / كتاب تفسير القرآن - سورة {...} / ج6/ص170
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب تفسير القرآن - سورة : { وَاللَّيْلِ إِذَا يَغْشَى وَالنَّهَارِ إِذَا تَجَلَّى ( الليل : 1 - 2 ) }',
    '6', '170', hadith_num='4943', hadith_text_paras=b4_text))

# b5: البخاري / صحيح البخاري / كتاب تفسير القرآن - سورة : { قُلْ أَعُوذُ... } / ج6/ص181
# editorial comment from bt goes into hadith-text as first p
b5_all_text = []
if b5_editorial_comment and EDITORIAL_TEXT not in b5_editorial_comment:
    b5_all_text.append(b5_editorial_comment)
b5_all_text.extend(b5_hadith_text)
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب تفسير القرآن - سورة : { قُلْ أَعُوذُ بِرَبِّ النَّاسِ ( الناس : 1 ) }',
    '6', '181', hadith_num='4977', hadith_text_paras=b5_all_text))

# b6: البخاري / صحيح البخاري / كتاب فضائل القرآن - باب : أنزل القرآن على سبعة أحرف / ج6/ص184
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب فضائل القرآن - باب : أنزل القرآن على سبعة أحرف',
    '6', '184', hadith_num='4992', hadith_text_paras=b6_text))

# b7: البخاري / صحيح البخاري / كتاب فضائل القرآن - باب : إقرءوا القرآن ما ائتلفت... / ج6/ص198
# Current b7 bt has the hadith text embedded in it - move to hadith-text
b7 = blocks[6]
b7_bt = b7.find('span', class_='book-title')
b7_ht_p = b7_bt.get_text(strip=True) if b7_bt else ''  # this is the hadith text
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب فضائل القرآن - باب : إقرءوا القرآن ما ائتلفت قلوبكم',
    '6', '198', hadith_num='5060',
    hadith_text_paras=[b7_ht_p] if b7_ht_p else []))

# b8: البخاري / صحيح البخاري / كتاب الحدود - باب : الاعتراف بالزنا / ج8/ص168
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب الحدود - باب : الاعتراف بالزنا',
    '8', '168', hadith_num='6829', hadith_text_paras=b8_text))

# b9: البخاري / صحيح البخاري / كتاب الحدود - باب : رجم الحبلى... / ج8/ص168 [editorial + hadith]
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب الحدود - باب : رجم الحبلى من الزنا إذا أحصنت',
    '8', '168', hadith_num='6830', editorial=True, hadith_text_paras=b9_text))

# b10: البخاري / صحيح البخاري / كتاب الاعتصام - باب : ما ذكر النبي (ص)... / ج9/ص103
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب الاعتصام بالكتاب والسنة - باب : ما ذكر النبي (ص) وحض على اتفاق أهل العلم وما أجمع عليه الحرمان مكة والمدينة',
    '9', '103', hadith_num='7323', hadith_text_paras=b10_text))

# b11: البخاري / صحيح البخاري / كتاب التوحيد - باب : قول الله تعالى { فَاقْرَءُوا... } / ج9/ص159
new_blocks.append(make_block(soup, 'البخاري', 'صحيح البخاري',
    'كتاب التوحيد - باب : قول الله تعالى : { فَاقْرَءُوا مَا تَيَسَّرَ مِنَ الْقُرْآنِ ( المزمل : 20 ) }',
    '9', '159', hadith_num='7550', hadith_text_paras=b11_text))

# Replace all blocks in article-body
for b in blocks:
    b.decompose()

for nb in new_blocks:
    article.append(nb)

with open('Threef/1Bkhari.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))

print('Done. Written', len(new_blocks), 'clean blocks.')
