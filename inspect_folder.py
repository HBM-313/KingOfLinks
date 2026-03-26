import os, re, sys
from bs4 import BeautifulSoup, Tag
from pathlib import Path

EDITORIAL = 'النص طويل لذا استقطع منه موضع الشاهد'
CI_HADITH = re.compile(r'^-\s*\d+\s*-\s*.{10,}')
NUMBER_ONLY = re.compile(r'^\s*[‏\d\u0660-\u0669]+\s*$')
GARBLED = re.compile(r'^م{1,3}$')
BOOK_NAMES = {'صحيح البخاري','صحيح مسلم','السنن الكبرى','المعجم الكبير','المعجم الأوسط',
              'المعجم الصغير','المستدرك على الصحيحين','مسند الامام أحمد بن حنبل',
              'صحيح ابن حبان','سير أعلام النبلاء','البداية والنهاية','تاريخ دمشق','كتاب السنة'}

folder = sys.argv[1] if len(sys.argv) > 1 else 'Abdulmtalib'
all_clean = True

for path in sorted(Path(folder).rglob('*.html')):
    if 'Main' in path.name: continue
    
    with open(path, encoding='utf-8', errors='replace') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    issues = []
    ab = soup.find(class_='article-body')
    if ab:
        for child in ab.children:
            if isinstance(child, Tag):
                if 'analysis-note' in (child.get('class') or []):
                    issues.append('FLOATING_NOTE')
                # Ignore loose <p> if they are just spaces
                if child.name == 'p' and child.get_text(strip=True):
                    issues.append(f'LOOSE_P: {child.get_text(strip=True)[:50]}')
    
    if soup.find('div', class_='footnotes-section'):
        issues.append('FOOTNOTES_SECTION')
        
    for i, blk in enumerate(soup.find_all('div', class_='hadith-block')):
        bn = f'b{i+1}'
        sn = blk.find('div', class_='scholar-name')
        bt = blk.find('span', class_='book-title')
        ref = blk.find('div', class_='ref-info')
        ht = blk.find('div', class_='hadith-text')
        sn_t = sn.get_text(strip=True) if sn else ''
        bt_t = bt.get_text(strip=True) if bt else ''
        
        if ref:
            labels = [s.get_text(strip=True) for s in ref.find_all('span', class_='ref-label')]
            if not any('الصفحة' in l for l in labels): issues.append(f'{bn} MISSING_PAGE')
            
        if not sn_t: issues.append(f'{bn} EMPTY_SN')
        elif NUMBER_ONLY.match(sn_t): issues.append(f'{bn} NUMBER_IN_SN: {sn_t}')
        elif GARBLED.match(sn_t): issues.append(f'{bn} GARBLED_SN: {sn_t}')
        elif sn_t in BOOK_NAMES: issues.append(f'{bn} BOOK_AS_SN: {sn_t}')
        elif EDITORIAL in sn_t: issues.append(f'{bn} EDITORIAL_IN_SN')
        
        if sn_t and sn_t == bt_t: issues.append(f'{bn} SN_EQ_BT: {sn_t}')
        
        if bt_t and ' -' in bt_t and 'كتاب' not in bt_t and 'تاريخ' not in bt_t: 
             issues.append(f'{bn} COMBINED_BT: {bt_t[:60]}')
             
        for ci in blk.find_all('span', class_='chapter-info'):
            if CI_HADITH.match(ci.get_text(strip=True)):
                issues.append(f'{bn} HADITH_IN_CI: {ci.get_text(strip=True)[:80]}')
                
        if ht:
            for p in ht.find_all('p'):
                if EDITORIAL in p.get_text(strip=True) and not p.find('span', class_='editorial-note'):
                    issues.append(f'{bn} UNWRAPPED_EDITORIAL')
                    
        if len(blk.find_all('div', class_='analysis-note')) > 1:
            issues.append(f'{bn} FRAG_ANALYSIS')
        if len(blk.find_all('div', class_='scholar-name')) > 1:
            issues.append(f'{bn} DUP_SN')

    if issues:
        all_clean = False
        print(f'⚠️  {path.as_posix()}:')
        for iss in issues: print(f'   → {iss}')
    else:
        print(f'✅ {path.as_posix()}')

print(f"\n{'✅ ALL CLEAN' if all_clean else '❌ ISSUES REMAIN'}")
