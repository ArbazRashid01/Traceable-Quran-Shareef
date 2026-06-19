#!/usr/bin/env python3
"""
Generate the ROMAN URDU version of every Juz (Juz-NN-Urdu.html).
  * Word meaning  -> Roman Urdu (transliterated from quran.com Urdu glosses)
  * Verse meaning -> Roman Urdu (Maududi, translation id 831)
  * Arabic + Arabic-transliteration -> unchanged
English versions (Juz-NN.html) are left untouched.
"""
import json, re
from pathlib import Path
from urdu_roman import to_roman
import build_all as B

BASE = Path(__file__).parent
en = json.loads((BASE/'quran_data.json').read_text(encoding='utf-8'))
ur = json.loads((BASE/'quran_urdu.json').read_text(encoding='utf-8'))

# Build Roman-Urdu verses dict with same schema as quran_data.json
verses = {}
for vk, ev in en['verses'].items():
    uv = ur['verses'][vk]
    wen = ev['w']; wur = uv['wu']
    w = []
    for i in range(len(wen)):
        ar, tr, _ = wen[i]
        urdu_meaning = wur[i][1] if i < len(wur) else ''
        w.append([ar, tr, to_roman(urdu_meaning)])
    verses[vk] = {'w': w, 'm': uv['mu'], 'r': ev.get('r')}

# ── Swap dataset into the engine ──
B.VS = verses
B._PAREN = re.compile(r'$^')   # keep parentheses in Roman Urdu meanings
B.VARIANT = '-Urdu'
B.TITLE_SUFFIX = ' (Roman Urdu)'

if __name__ == '__main__':
    import sys
    targets = range(1,31) if len(sys.argv)<2 else [int(x) for x in sys.argv[1:]]
    total=0
    for j in targets:
        out,n,sz = B.write_juz(j); total+=n
        print(f'Juz {j:2d} (Roman Urdu): {n:3d} pages, {sz//1024} KB -> {out.name}')
    print(f'Total Roman-Urdu pages: {total}')
