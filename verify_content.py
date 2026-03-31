"""
Phase 1: Verify local content against live cached pages.
Compares block counts and numeric signatures.

Usage:
  python -X utf8 verify_content.py                   # All folders
  python -X utf8 verify_content.py --folder Abawalnabi  # One folder
"""
import json, os, re, sys
from pathlib import Path
from bs4 import BeautifulSoup

CACHE_DIR = '_live_cache'
URL_MAP = '_url_map.json'
RESULTS_FILE = '_audit_results.json'

def load_url_map():
    with open(URL_MAP, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_live_cached(live_path):
    """Read cached live page as raw bytes -> decode windows-1256."""
    cache_file = os.path.join(CACHE_DIR, live_path)
    if not os.path.isfile(cache_file):
        return None
    with open(cache_file, 'rb') as f:
        raw = f.read()
    return raw.decode('windows-1256', errors='replace')

def extract_live_ref_lines(html):
    """Extract all ref-line tuples from live page in order.
    
    Returns list of dicts with 'juz' and/or 'page' keys.
    Each dict represents one content block's ref info.
    
    Ref lines in live pages look like:
      الجزء : ( N ) - رقم الصفحة : ( M )    -> garbled as ÇáÌÒÁ : ( N ) - ÑÞã ÇáÕÝÍÉ : ( M )
      رقم الصفحة : ( M )                     -> garbled as ÑÞã ÇáÕÝÍÉ : ( M )
    These appear in <font color="#FF0000" size="2"> tags, centered.
    """
    # Strip HTML tags and normalize whitespace for ref extraction
    clean = re.sub(r'<[^>]+>', ' ', html)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean)
    
    # Remove inline citations in parentheses (pattern: (Scholar - Book - ref) inside analysis)
    # These are inline refs within text like: ( الآلوسي - تفسير الآلوسي - الجزء : ( N ) - رقم الصفحة : ( M ) )
    # Remove them so they don't get counted as block refs
    clean = re.sub(r'\(\s*[^()]{1,80}\s*-\s*[^()]{1,80}\s*-\s*الجزء\s*:\s*\(\s*\d+\s*\)\s*-\s*رقم\s*الصفحة\s*:\s*\(\s*[\d/]+\s*\)\s*\)', ' ', clean)
    
    refs = []
    
    # Collect positions of all juz+page matches to exclude their page parts
    juz_page_ranges = []
    for m in re.finditer(r'الجزء\s*:\s*\(\s*(\d+)\s*\)\s*-\s*رقم\s*الصفحة\s*:\s*\(\s*([\d\s/]+?)\s*\)', clean):
        juz = m.group(1).strip()
        page = re.sub(r'\s+', '', m.group(2).strip())
        refs.append((m.start(), {'juz': juz, 'page': page}))
        juz_page_ranges.append((m.start(), m.end()))
    
    # Page-only refs - exclude those within juz+page ranges
    for m in re.finditer(r'رقم\s*الصفحة\s*:\s*\(\s*([\d\s/]+?)\s*\)', clean):
        in_juz_page = any(start <= m.start() <= end for start, end in juz_page_ranges)
        if not in_juz_page:
            page = re.sub(r'\s+', '', m.group(1).strip())
            refs.append((m.start(), {'page': page}))
    
    # Sort by position in document
    refs.sort(key=lambda x: x[0])
    return [r[1] for r in refs]

def count_live_blocks_hr(html):
    """Count content blocks using HR splitting as secondary metric."""
    segments = re.split(r'<hr[^>]*/?>',  html, flags=re.IGNORECASE)
    count = 0
    for seg in segments:
        seg_clean = re.sub(r'<[^>]+>', ' ', seg)
        seg_clean = re.sub(r'\s+', ' ', seg_clean).strip()
        if len(seg_clean) < 50:
            continue
        # Skip nav-only segments
        if 'العودة' in seg_clean and len(seg_clean) < 300:
            continue
        count += 1
    return count

def extract_local_refs(block):
    """Extract numeric refs from a local hadith-block BeautifulSoup element."""
    nums = {}
    ref = block.find('div', class_='ref-info')
    if ref:
        for span in ref.find_all('span', class_='ref-label'):
            val_span = span.find_next_sibling('span', class_='ref-value')
            if val_span:
                label = span.get_text(strip=True)
                value = val_span.get_text(strip=True)
                if 'الجزء' in label:
                    nums['juz'] = value
                elif 'الصفحة' in label:
                    nums['page'] = value
    
    hn = block.find('span', class_='hadith-number')
    if hn:
        nums['hadith_num'] = hn.get_text(strip=True)
    
    return nums

def check_hadith_text(block):
    """Check if hadith-text div exists and has content."""
    ht = block.find('div', class_='hadith-text')
    if not ht:
        return False, 'MISSING_HADITH_TEXT_DIV'
    text = ht.get_text(strip=True)
    if not text:
        return False, 'EMPTY_HADITH_TEXT'
    return True, 'OK'

def verify_page(entry):
    """Compare one local file against its live cached page."""
    local_path = entry['local_path']
    live_path = entry['live_path']
    
    result = {
        'local_path': local_path,
        'live_url': entry['live_url'],
        'live_path': live_path,
        'status': 'pending',
        'issues': []
    }
    
    # Read live
    live_html = read_live_cached(live_path)
    if live_html is None:
        result['status'] = 'NO_CACHE'
        result['issues'].append('Live page not cached')
        return result
    
    # Read local
    if not os.path.isfile(local_path):
        result['status'] = 'MISSING_LOCAL'
        result['issues'].append('Local file does not exist')
        return result
    
    with open(local_path, encoding='utf-8', errors='replace') as f:
        local_html = f.read()
    
    soup = BeautifulSoup(local_html, 'html.parser')
    local_blocks = soup.find_all('div', class_='hadith-block')
    
    # Extract live refs sequentially
    live_refs_list = extract_live_ref_lines(live_html)
    live_block_count_hr = count_live_blocks_hr(live_html)
    
    result['live_ref_count'] = len(live_refs_list)
    result['live_block_count_hr'] = live_block_count_hr
    result['local_block_count'] = len(local_blocks)
    
    # Use ref count as primary block count (more reliable than HR)
    live_count = len(live_refs_list)
    local_count = len(local_blocks)
    
    # Block count comparison
    if live_count > local_count:
        result['issues'].append(f'MISSING_BLOCKS: live_refs={live_count} > local={local_count}')
    elif live_count < local_count:
        result['issues'].append(f'EXTRA_BLOCKS: local={local_count} > live_refs={live_count}')
    
    # Compare numeric refs block by block
    min_blocks = min(live_count, local_count)
    ref_mismatches = []
    empty_hadith = []
    
    for i in range(min_blocks):
        live_refs = live_refs_list[i]
        local_refs = extract_local_refs(local_blocks[i])
        
        # Compare refs (normalize spaces around / for comparison)
        for key in ['juz', 'page']:
            if key in live_refs and key in local_refs:
                live_val = re.sub(r'\s*/\s*', '/', live_refs[key])
                local_val = re.sub(r'\s*/\s*', '/', local_refs[key])
                if live_val != local_val:
                    ref_mismatches.append(f'b{i+1} {key}: live={live_refs[key]} local={local_refs[key]}')
            elif key in live_refs and key not in local_refs:
                ref_mismatches.append(f'b{i+1} MISSING_{key.upper()}_LOCAL (live={live_refs[key]})')
        
        # Check hadith text
        has_text, text_status = check_hadith_text(local_blocks[i])
        if not has_text:
            empty_hadith.append(f'b{i+1} {text_status}')
    
    # Also check remaining local blocks (beyond live range) for empty hadith-text
    for i in range(min_blocks, local_count):
        has_text, text_status = check_hadith_text(local_blocks[i])
        if not has_text:
            empty_hadith.append(f'b{i+1} {text_status}')
    
    if ref_mismatches:
        result['issues'].extend(ref_mismatches)
    if empty_hadith:
        result['issues'].extend(empty_hadith)
    
    # Determine overall status
    if not result['issues']:
        result['status'] = 'OK'
    elif any('MISSING_BLOCKS' in i for i in result['issues']):
        result['status'] = 'MISSING_BLOCKS'
    elif any('EXTRA_BLOCKS' in i for i in result['issues']):
        result['status'] = 'EXTRA_BLOCKS'
    elif ref_mismatches:
        result['status'] = 'REF_MISMATCH'
    elif empty_hadith:
        result['status'] = 'MISSING_HADITH_TEXT'
    else:
        result['status'] = 'NEEDS_MANUAL'
    
    return result

def main():
    entries = load_url_map()
    
    # Filter by folder if specified
    folder_filter = None
    if '--folder' in sys.argv:
        idx = sys.argv.index('--folder')
        if idx + 1 < len(sys.argv):
            folder_filter = sys.argv[idx + 1]
    
    if folder_filter:
        entries = [e for e in entries if e['folder'] == folder_filter]
    
    # Skip non-content entries (empty folder = root pages like Images/)
    entries = [e for e in entries if e['folder'] and e['folder'] not in ('Images', '')]
    
    print(f'Verifying {len(entries)} pages...\n')
    
    results = []
    stats = {}
    
    for entry in entries:
        r = verify_page(entry)
        results.append(r)
        
        folder = entry['folder']
        if folder not in stats:
            stats[folder] = {'OK': 0, 'MISSING_BLOCKS': 0, 'EXTRA_BLOCKS': 0, 
                           'REF_MISMATCH': 0, 'MISSING_HADITH_TEXT': 0, 
                           'NO_CACHE': 0, 'MISSING_LOCAL': 0, 'NEEDS_MANUAL': 0}
        stats[folder][r['status']] = stats[folder].get(r['status'], 0) + 1
        
        if r['status'] != 'OK':
            print(f"  {r['status']:20s} {r['local_path']}")
            for iss in r['issues'][:5]:
                print(f"    -> {iss}")
    
    # Summary
    print(f'\n{"="*60}')
    print(f'SUMMARY')
    print(f'{"="*60}')
    
    total_ok = 0
    total_issues = 0
    
    for folder in sorted(stats):
        s = stats[folder]
        ok = s['OK']
        total = sum(s.values())
        total_ok += ok
        total_issues += (total - ok)
        
        if ok == total:
            print(f'  ✅ {folder}: {total} pages all OK')
        else:
            issues_str = ', '.join(f'{k}={v}' for k, v in s.items() if v > 0 and k != 'OK')
            print(f'  ⚠️  {folder}: {ok}/{total} OK | {issues_str}')
    
    print(f'\nTotal: {total_ok} OK, {total_issues} with issues')
    
    # Save results
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\nWrote {RESULTS_FILE}')

if __name__ == '__main__':
    main()
