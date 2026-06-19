#!/usr/bin/env python3
"""Fetch Roman-Urdu verse meanings (Maududi id 831) + Urdu-script word meanings
   for all 114 surahs -> quran_urdu.json"""
import requests, json, re, time
from pathlib import Path

OUT = Path(__file__).parent / 'quran_urdu.json'
S = requests.Session(); S.headers['User-Agent']='Mozilla/5.0'

def get(url, tries=5):
    for k in range(tries):
        try:
            r=S.get(url,timeout=45)
            if r.status_code==200: return r.json()
        except Exception: pass
        time.sleep(1+k)
    raise RuntimeError('fail '+url)

def clean(s):
    s=re.sub(r'<sup[^>]*>.*?</sup>','',s or '',flags=re.S)
    s=re.sub(r'<[^>]+>','',s)
    return s.replace('  ',' ').strip()

data={'verses':{}}
for ch in range(1,115):
    page=1
    while True:
        url=(f'https://api.quran.com/api/v4/verses/by_chapter/{ch}'
             f'?words=true&word_fields=text_uthmani&language=ur'
             f'&translations=831&per_page=50&page={page}')
        d=get(url)
        for v in d['verses']:
            vk=v['verse_key']
            words=[]
            for w in v.get('words',[]):
                if w.get('char_type_name')!='word': continue
                words.append((w.get('text_uthmani',''),
                              (w.get('translation',{}) or {}).get('text','') or ''))
            vm=clean(v['translations'][0]['text']) if v.get('translations') else ''
            data['verses'][vk]={'wu':words,'mu':vm}
        nxt=d['pagination'].get('next_page')
        if not nxt: break
        page=nxt
    if ch%15==0 or ch==114: print(f'  through chapter {ch} ({len(data["verses"])} verses)')

OUT.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
print(f'Saved {OUT.name}: {len(data["verses"])} verses, {OUT.stat().st_size//1024//1024} MB')
