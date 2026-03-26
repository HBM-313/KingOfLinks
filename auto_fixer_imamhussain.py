import os, glob, re
from bs4 import BeautifulSoup
from pathlib import Path

def create_or_get_hadith_text(soup, block):
    ht = block.find('div', class_='hadith-text')
    if not ht:
        ht = soup.new_tag('div', attrs={'class': 'hadith-text'})
        ref_info = block.find('div', class_='ref-info')
        if ref_info:
            ref_info.insert_after(ht)
            ref_info.insert_after("\n")
        else:
            block.append(ht)
    return ht

def fix_all_html(folder):
    for path in Path(folder).rglob('*.html'):
        if 'Main' in path.name: continue
        
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')
        modified = False

        # Fix LOOSE_P tags inside article-body
        ab = soup.find('div', class_='article-body')
        if ab:
            loose_elements = []
            for child in ab.children:
                if child.name in ['p', 'div'] and child.get('class') != ['hadith-block'] and child.get('class') != ['footnotes-section']:
                    if isinstance(child, str) and not child.strip(): continue
                    # Collect loose elements
                    loose_elements.append(child)
            
            if loose_elements:
                new_block = soup.new_tag('div', attrs={'class': 'hadith-block'})
                ht = soup.new_tag('div', attrs={'class': 'hadith-text'})
                # Wait, if they are before the first hadith-block, it's an intro
                
                # To be safer, just skip automatic loose_p because it varies if they are intro vs hadith.
                pass
                
        for block in soup.find_all('div', class_='hadith-block'):
            # Fix EDITORIAL_IN_SN
            sns = block.find_all('div', class_='scholar-name')
            for sn in sns:
                if 'النص طويل' in sn.get_text():
                    # Move to hadith-text
                    ht = create_or_get_hadith_text(soup, block)
                    p = soup.new_tag('p')
                    span = soup.new_tag('span', attrs={'class': 'editorial-note'})
                    span.string = 'النص طويل لذا استقطع منه موضع الشاهد'
                    p.append(span)
                    if ht.contents:
                        ht.insert(0, "\n")
                        ht.insert(0, p)
                        ht.insert(0, "\n")
                    else:
                        ht.append("\n")
                        ht.append(p)
                        ht.append("\n")
                    sn.decompose()
                    modified = True

            # Fix COMBINED_BT
            bt = block.find('span', class_='book-title')
            if bt:
                bt_text = bt.get_text(strip=True)
                if ' -' in bt_text and 'كتاب' not in bt_text and 'تاريخ' not in bt_text and bt_text not in ['الترمذي -سنن الترمذي', 'ابن ماجه -سنن ابن ماجه', 'البداية والنهاية -ثم دخلت سنة احدى وستين']:
                     parts = bt_text.split(' -', 1)
                     bt.string = parts[0].strip()
                     ci = soup.new_tag('span', attrs={'class': 'chapter-info'})
                     ci.string = '- ' + parts[1].strip()
                     bt.insert_after("\n")
                     bt.insert_after(ci)
                     modified = True
                # specific hardcoded replacements
                if bt_text == 'الترمذي -سنن الترمذي':
                     bt.string = 'سنن الترمذي'
                     modified = True
                if bt_text == 'ابن ماجه -سنن ابن ماجه':
                     bt.string = 'سنن ابن ماجه'
                     modified = True
                if bt_text.startswith('البداية والنهاية -'):
                     parts = bt_text.split('-', 1)
                     bt.string = parts[0].strip()
                     ci = soup.new_tag('span', attrs={'class': 'chapter-info'})
                     ci.string = '- ' + parts[1].strip()
                     bt.insert_after("\n")
                     bt.insert_after(ci)
                     modified = True

            # Fix HADITH_IN_CI
            cis = block.find_all('span', class_='chapter-info')
            for ci in cis:
                text = ci.get_text(strip=True)
                match = re.match(r'^-\s*(\d+)\s*-\s*(.+)$', text)
                if match:
                    # we ignore length check now to catch the shorter ones
                    number = match.group(1)
                    hadith_text_val = match.group(0)[1:].strip()
                    ht = create_or_get_hadith_text(soup, block)
                    
                    hn_tag = soup.new_tag('span', attrs={'class': 'hadith-number'})
                    hn_tag.string = number
                    p_tag = soup.new_tag('p')
                    p_tag.string = hadith_text_val
                    
                    ht.append(hn_tag)
                    ht.append("\n")
                    ht.append(p_tag)
                    ht.append("\n")

                    ci.decompose()
                    modified = True

        if modified:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(str(soup).replace('></p>', '>\n\n</p>').replace('</div></div', '</div>\n</div'))

fix_all_html('ImamHussain')
