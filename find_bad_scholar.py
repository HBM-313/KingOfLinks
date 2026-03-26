import glob
import re
from bs4 import BeautifulSoup

def find_bad_scholars():
    folders = ['SwR', 'ImamHasan', 'ImamHussain']
    bad_files = {} # filename -> list of block indices
    for folder in folders:
        for file in glob.glob(f"{folder}/*.html"):
            if 'Main' in file: continue
            with open(file, 'r', encoding='utf-8') as f:
                html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            blocks = soup.find_all('div', class_='hadith-block')
            issues = []
            for i, block in enumerate(blocks):
                sn = block.find('div', class_='scholar-name')
                if sn:
                    text = sn.get_text(strip=True)
                    # if it's just numbers and maybe some symbols like '-' or '‏', and < 15 chars
                    if re.match(r'^[\s\d\-\u200f]+$', text) or text.isnumeric() or 'حدثنا' in block.find('span', class_='book-title').get_text(strip=True) if block.find('span', class_='book-title') else False:
                        issues.append(i)
            if issues:
                bad_files[file] = issues
    
    for f, blocks in bad_files.items():
        print(f"{f}: blocks {blocks}")

find_bad_scholars()
