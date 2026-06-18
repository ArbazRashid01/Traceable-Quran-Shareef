#!/usr/bin/env python3
"""Fetch complete Quran word-by-word data for all 114 surahs -> quran_data.json"""
import requests, json, re, time
from pathlib import Path

OUT = Path(__file__).parent / 'quran_data.json'
PAREN = re.compile(r'[\(\[][^\)\]]*[\)\]]')
def clean(s): return PAREN.sub('', s or '').replace('  ', ' ').strip(' ,;:.')

S = requests.Session()
S.headers['User-Agent'] = 'Mozilla/5.0'

def get(url, tries=4):
    for k in range(tries):
        try:
            r = S.get(url, timeout=40)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(1.0 + k)
    raise RuntimeError(f'failed: {url}')

# 1) Chapter metadata
chapters = {}
cj = get('https://api.quran.com/api/v4/chapters')
for c in cj['chapters']:
    chapters[str(c['id'])] = {
        'name_ar': c['name_arabic'],
        'name_en': c['name_simple'],
        'meaning': c['translated_name']['name'],
        'revealed': 'Makkah' if c['revelation_place'] == 'makkah' else 'Madinah',
        'verses': c['verses_count'],
    }

# 2) Verses with words, transliteration, meaning, ruku
data = {'chapters': chapters, 'verses': {}}
for ch in range(1, 115):
    page = 1
    while True:
        url = (f'https://api.quran.com/api/v4/verses/by_chapter/{ch}'
               f'?words=true&word_fields=text_uthmani,transliteration,translation'
               f'&fields=ruku_number&translations=20&per_page=50&page={page}')
        d = get(url)
        for v in d['verses']:
            vk = v['verse_key']
            words = []
            for w in v.get('words', []):
                if w.get('char_type_name') != 'word':
                    continue
                words.append([
                    w.get('text_uthmani', ''),
                    (w.get('transliteration', {}) or {}).get('text', '') or '',
                    (w.get('translation', {}) or {}).get('text', '') or '',
                ])
            mn = clean(v['translations'][0]['text']) if v.get('translations') else ''
            data['verses'][vk] = {'w': words, 'r': v.get('ruku_number'), 'm': mn}
        nxt = d['pagination'].get('next_page')
        if not nxt:
            break
        page = nxt
    if ch % 10 == 0 or ch == 114:
        print(f'  fetched through chapter {ch} ({len(data["verses"])} verses)')

OUT.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
print(f'Saved {OUT.name}: {len(data["verses"])} verses, {OUT.stat().st_size//1024//1024} MB')
