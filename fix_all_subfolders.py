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

        # Fix basic replacements first
        html = html.replace('<p>النص طويل لذا استقطع منه موضع الشاهد</p>', '<p><span class="editorial-note">النص طويل لذا استقطع منه موضع الشاهد</span></p>')
        html = html.replace('<p>[النص طويل لذا استقطع منه موضع الشاهد ]</p>', '<p><span class="editorial-note">النص طويل لذا استقطع منه موضع الشاهد</span></p>')
        html = html.replace('<div class="scholar-name">النص طويل لذا استقطع منه موضع الشاهد</div>', '')
        
        soup = BeautifulSoup(html, 'html.parser')
        modified = False

        # Fix HADITH_IN_CI
        for block in soup.find_all('div', class_='hadith-block'):
            cis = block.find_all('span', class_='chapter-info')
            for ci in cis:
                text = ci.get_text(strip=True)
                match = re.match(r'^-\s*(\d+)\s*-\s*(.+)$', text)
                if match and len(text) > 40:
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
        else:
            # We still need to write the basic html replacements back
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)

fix_all_html('SwR')
fix_all_html('ImamHasan')
fix_all_html('ImamHussain')
