#!/usr/bin/env python3
"""
Generate Traceable Quran workbook HTML for any Juz (1-30) using the same
engine/design as Juz 1. Reads quran_data.json. Outputs juz/Juz-NN.html.

Layout rules (identical to Juz 1):
  * Continuous dense flow — next ayah continues on the same line
  * 20pt traceable Arabic, transliteration above, meaning below
  * Left panel shows each ayah meaning once, on the page it completes
  * Ruku-end markers (green ain + number)
  * Pre-computed pagination, no clipping, no horizontal overflow
"""
import json, base64, re, math
from pathlib import Path

BASE = Path(__file__).parent
FONT_DIR = BASE / 'fonts'
OUTDIR = BASE / 'juz'
OUTDIR.mkdir(exist_ok=True)

DATA = json.loads((BASE / 'quran_data.json').read_text(encoding='utf-8'))
CH   = DATA['chapters']
VS   = DATA['verses']

# Juz -> {chapter: 'start-end'}
JUZ_MAP = {
    1:{'1':'1-7','2':'1-141'}, 2:{'2':'142-252'}, 3:{'2':'253-286','3':'1-92'},
    4:{'3':'93-200','4':'1-23'}, 5:{'4':'24-147'}, 6:{'4':'148-176','5':'1-81'},
    7:{'5':'82-120','6':'1-110'}, 8:{'6':'111-165','7':'1-87'}, 9:{'7':'88-206','8':'1-40'},
    10:{'8':'41-75','9':'1-92'}, 11:{'9':'93-129','10':'1-109','11':'1-5'},
    12:{'11':'6-123','12':'1-52'}, 13:{'12':'53-111','13':'1-43','14':'1-52'},
    14:{'15':'1-99','16':'1-128'}, 15:{'17':'1-111','18':'1-74'},
    16:{'18':'75-110','19':'1-98','20':'1-135'}, 17:{'21':'1-112','22':'1-78'},
    18:{'23':'1-118','24':'1-64','25':'1-20'}, 19:{'25':'21-77','26':'1-227','27':'1-55'},
    20:{'27':'56-93','28':'1-88','29':'1-45'},
    21:{'29':'46-69','30':'1-60','31':'1-34','32':'1-30','33':'1-30'},
    22:{'33':'31-73','34':'1-54','35':'1-45','36':'1-27'},
    23:{'36':'28-83','37':'1-182','38':'1-88','39':'1-31'},
    24:{'39':'32-75','40':'1-85','41':'1-46'},
    25:{'41':'47-54','42':'1-53','43':'1-89','44':'1-59','45':'1-37'},
    26:{'46':'1-35','47':'1-38','48':'1-29','49':'1-18','50':'1-45','51':'1-30'},
    27:{'51':'31-60','52':'1-49','53':'1-62','54':'1-55','55':'1-78','56':'1-96','57':'1-29'},
    28:{'58':'1-22','59':'1-24','60':'1-13','61':'1-14','62':'1-11','63':'1-11','64':'1-18','65':'1-12','66':'1-12'},
    29:{'67':'1-30','68':'1-52','69':'1-52','70':'1-44','71':'1-28','72':'1-28','73':'1-20','74':'1-56','75':'1-40','76':'1-31','77':'1-50'},
    30:{'78':'1-40','79':'1-46','80':'1-42','81':'1-29','82':'1-19','83':'1-36','84':'1-25','85':'1-22','86':'1-17','87':'1-19','88':'1-26','89':'1-30','90':'1-20','91':'1-15','92':'1-21','93':'1-11','94':'1-8','95':'1-8','96':'1-19','97':'1-5','98':'1-8','99':'1-8','100':'1-11','101':'1-11','102':'1-8','103':'1-3','104':'1-9','105':'1-5','106':'1-4','107':'1-7','108':'1-3','109':'1-6','110':'1-3','111':'1-5','112':'1-4','113':'1-5','114':'1-6'},
}

_AR = str.maketrans('0123456789', '\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669')
def ar(n): return str(n).translate(_AR)



# ─── GEOMETRY (identical to Juz 1) ───────────────────────────────
PAGE_W, PAGE_H = 210, 297
PAD = 12; FRAME_W = 0.5; HEADER_H = 14; FOOTER_H = 10
BODY_W = PAGE_W - 2*PAD - 2*FRAME_W
BODY_H = PAGE_H - 2*PAD - 2*FRAME_W - HEADER_H - FOOTER_H
PANEL_PCT = 24
WORD_W = BODY_W * (100 - PANEL_PCT) / 100

AR_PT=20; TR_PT=10; MN_PT=10; PANEL_NUM_PT=12; PANEL_TXT_PT=11
AR_CHAR_MM=3.3; TR_CHAR_MM=1.7; MN_CHAR_MM=1.7
CELL_PAD_MM=3; CELL_MIN_MM=12
ROW_BASE_MM=23; ROW_LINE_MM=4.4

_DIAC = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]')
_PAREN = re.compile(r'[\(\[][^\)\]]*[\)\]]')
def ar_base_len(s): return sum(1 for c in _DIAC.sub('', s or '') if '\u0600' <= c <= '\u06FF')
def clean_m(s): return _PAREN.sub('', s or '').replace('  ',' ').strip(' ,;:.')
def _esc(s): return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def longest_tok(t, mm):
    ts=(t or '').split(); return (max(len(x) for x in ts)*mm) if ts else 0

def cell_w(a,t,m):
    w=max(ar_base_len(a)*AR_CHAR_MM, longest_tok(t,TR_CHAR_MM), longest_tok(clean_m(m),MN_CHAR_MM))+CELL_PAD_MM
    return max(CELL_MIN_MM, min(WORD_W, w))

def cell_h(a,t,m,w):
    usable=w-CELL_PAD_MM
    tl=max(1, math.ceil(len(t or '')*TR_CHAR_MM/usable))
    ml=max(1, math.ceil(len(clean_m(m))*MN_CHAR_MM/usable))
    return ROW_BASE_MM + (tl-1+ml-1)*ROW_LINE_MM


# ─── RUKU ENDINGS (computed from data) ───────────────────────────
def ruku_end_map(verse_keys):
    """verse_key -> sequential ruku number within this juz, for verses that end a ruku."""
    end = {}; prev=None; count=0
    for i,vk in enumerate(verse_keys):
        rn = VS[vk].get('r')
        nxt = VS[verse_keys[i+1]].get('r') if i+1 < len(verse_keys) else None
        if nxt != rn:   # ruku changes after this verse (or juz ends)
            count += 1
            end[vk] = count
    return end



# ─── ITEMS / PACKING / PAGINATION ────────────────────────────────
def make_items(verse_keys, rmap):
    items=[]
    for vk in verse_keys:
        for a,t,m in VS[vk]['w']:
            w=cell_w(a,t,m); h=cell_h(a,t,m,w)
            items.append({'k':'w','vk':vk,'a':a,'t':t,'m':clean_m(m),'w':w,'h':h})
        ruku=rmap.get(vk)
        items.append({'k':'M','vk':vk,'n':int(vk.split(':')[1]),'ruku':ruku,
                       'w':CELL_MIN_MM+(8 if ruku else 0),'h':ROW_BASE_MM})
    return items

def pack(items):
    rows,cur,cw=[],[],0.0
    for it in items:
        if cur and cw+it['w']>WORD_W:
            rows.append(cur); cur,cw=[],0.0
        cur.append(it); cw+=it['w']
    if cur: rows.append(cur)
    return rows

def row_h(r): return max(it['h'] for it in r)

def paginate(rows):
    limit=BODY_H-2; pages,cur,ch=[],[],0.0
    for r in rows:
        h=row_h(r)
        if cur and ch+h>limit:
            pages.append(cur); cur,ch=[],0.0
        cur.append(r); ch+=h
    if cur: pages.append(cur)
    return pages


# ─── HTML EMIT ───────────────────────────────────────────────────
def em_word(it):
    return (f'<div class="cell" style="flex:0 1 {it["w"]:.1f}mm">'
            f'<div class="tr">{_esc(it["t"])}</div>'
            f'<div class="ar">{it["a"]}</div>'
            f'<div class="mn">{_esc(it["m"])}</div></div>')

def em_marker(it):
    glyph=f'&#1757;{ar(it["n"])}'
    ruku=it.get('ruku')
    rh=(f'<div class="ruku">&#1593;<span class="ruku-n">{ruku}</span></div>' if ruku else '')
    return (f'<div class="cell marker" style="flex:0 0 {it["w"]:.0f}mm">'
            f'<div class="tr">{("Ruku "+str(ruku)) if ruku else "&nbsp;"}</div>'
            f'<div class="ar mk">{glyph}{rh}</div>'
            f'<div class="mn">&nbsp;</div></div>')

def em_row(r):
    return '<div class="row">'+''.join(em_marker(it) if it['k']=='M' else em_word(it) for it in r)+'</div>'

def panel(page_rows):
    done=[]
    for r in page_rows:
        for it in r:
            if it['k']=='M' and it['vk'] not in done:
                done.append(it['vk'])
    out=[]
    for vk in done:
        out.append(f'<div class="pslot"><div class="pnum">{ar(int(vk.split(":")[1]))}</div>'
                   f'<div class="ptxt">{_esc(clean_m(VS[vk]["m"]))}</div></div>')
    return '<div class="panel">'+''.join(out)+'</div>'

def header(juz,mid,pg):
    return (f'<div class="header"><span class="h-side">JUZ {juz}</span>'
            f'<span class="h-mid">&#10022; {mid} &#10022;</span>'
            f'<span class="h-side h-r">PAGE {pg}</span></div>')

def footer(left,pg,juz):
    return (f'<div class="footer"><span>{left}</span>'
            f'<span>Page {pg} &middot; Juz {juz}</span></div>')

def page_std(juz,pg,label,rows):
    return (f'<div class="page"><div class="inner">{header(juz,label,pg)}'
            f'<div class="body">{panel(rows)}<div class="words">'
            f'{"".join(em_row(r) for r in rows)}</div></div>'
            f'{footer(label,pg,juz)}</div></div>')



def page_juz_opener(juz,pg):
    intro=(f'This is Juz {juz} (Para {juz}) of the Holy Qur&apos;an. Trace each word, '
           f'read its transliteration and meaning, and reflect as you write.')
    return (f'<div class="page"><div class="inner">{header(juz,"JUZ OPENING",pg)}'
            f'<div class="open open-juz">'
            f'<div class="o-eyebrow">PARA &middot; JUZ</div>'
            f'<div class="o-rule">&middot; &middot; &middot;</div>'
            f'<div class="o-bignum">{juz}</div>'
            f'<div class="o-arlabel">&#1575;&#1604;&#1580;&#1586;&#1569; {ar(juz)}</div>'
            f'<div class="o-rule">&middot; &middot; &middot;</div>'
            f'<div class="o-intro">{intro}</div>'
            f'</div>{footer("Juz Opening",pg,juz)}</div></div>')

def page_surah_opener(juz,pg,ch):
    m=CH[ch]
    bism=('&#1576;&#1616;&#1587;&#1618;&#1605;&#1616; &#1649;&#1604;&#1604;&#1617;&#1614;&#1607;&#1616; '
          '&#1649;&#1604;&#1585;&#1617;&#1614;&#1581;&#1618;&#1605;&#1614;&#1648;&#1606;&#1616; '
          '&#1649;&#1604;&#1585;&#1617;&#1614;&#1581;&#1616;&#1610;&#1605;&#1616;')
    bism_html = '' if ch=='9' else f'<div class="s-bism">{bism}</div>'
    return (f'<div class="page"><div class="inner">{header(juz,m["name_en"].upper(),pg)}'
            f'<div class="open open-surah">'
            f'<div class="s-orn">&#10022; &#10022; &#10022;</div>'
            f'<div class="s-ar">{m["name_ar"]}</div>'
            f'<div class="s-en">{m["name_en"]}</div>'
            f'<div class="s-meta">Surah {ch} &middot; {m["meaning"]} &middot; '
            f'{m["revealed"]} &middot; {m["verses"]} Verses</div>'
            f'<div class="s-rule">&middot; &middot; &middot;</div>'
            f'{bism_html}'
            f'<div class="s-orn">&#10022; &#10022; &#10022;</div>'
            f'</div>{footer(m["name_en"]+" Opening",pg,juz)}</div></div>')


# ─── BUILD ONE JUZ ───────────────────────────────────────────────
def juz_verse_keys(juz):
    keys=[]
    for ch,rng in JUZ_MAP[juz].items():
        a,b=rng.split('-')
        for v in range(int(a),int(b)+1):
            keys.append(f'{ch}:{v}')
    return keys

def chapter_segments(juz):
    """Ordered list of (chapter, [verse_keys]) within the juz."""
    segs=[]
    for ch,rng in JUZ_MAP[juz].items():
        a,b=rng.split('-')
        segs.append((ch,[f'{ch}:{v}' for v in range(int(a),int(b)+1)]))
    return segs

def build_juz(juz):
    rmap = ruku_end_map(juz_verse_keys(juz))
    pages=[]; pno=0
    pno+=1; pages.append(page_juz_opener(juz,pno))
    for ch,vks in chapter_segments(juz):
        m=CH[ch]
        # surah opener only when the surah STARTS in this juz (verse 1 present)
        if vks and vks[0].endswith(':1'):
            pno+=1; pages.append(page_surah_opener(juz,pno,ch))
        rows=pack(make_items(vks,rmap))
        for pr in paginate(rows):
            pno+=1; pages.append(page_std(juz,pno,m['name_en'].upper(),pr))
    return pages



# ─── CSS + FONTS + WRITER ────────────────────────────────────────
def fonts_block():
    def b(n): return base64.b64encode((FONT_DIR/n).read_bytes()).decode()
    faces=[('Amiri',400,'normal','Amiri-Regular.woff2'),
           ('Amiri',700,'normal','Amiri-Bold.woff2'),
           ('EB Garamond',400,'normal','EBGaramond-Regular.woff2'),
           ('EB Garamond',400,'italic','EBGaramond-Italic.woff2'),
           ('EB Garamond',600,'normal','EBGaramond-SemiBold.woff2')]
    s='<style>'
    for fam,wt,st,fn in faces:
        s+=(f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};"
            f"src:url('data:font/woff2;base64,{b(fn)}') format('woff2')}}")
    return s+'</style>'

def css():
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#9e8f72;font-family:'EB Garamond','Georgia',serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{display:flex;flex-direction:column;align-items:center;padding:28px 0;gap:28px}}
.page{{position:relative;width:{PAGE_W}mm;height:{PAGE_H}mm;padding:{PAD}mm;
  background:#fdf7ed;border:{FRAME_W}mm solid #c9a84c;
  box-shadow:0 0 0 1.5mm #fdf7ed,0 0 0 2mm #c9a84c,0 12px 50px rgba(0,0,0,.30);overflow:hidden}}
.page::before{{content:'';position:absolute;top:4.5mm;right:4.5mm;bottom:4.5mm;left:4.5mm;
  border:0.3mm solid rgba(201,168,76,.4);pointer-events:none}}
.inner{{position:relative;width:100%;height:100%;display:flex;flex-direction:column}}
.header{{flex:0 0 {HEADER_H}mm;display:flex;align-items:center;justify-content:space-between;
  background:#f8f0dc;border-top:0.6mm solid #8b6c14;border-bottom:0.6mm solid #8b6c14;
  box-shadow:inset 0 0.6mm 0 #e8d49a,inset 0 -0.6mm 0 #e8d49a;padding:0 5mm}}
.h-side{{font-size:9pt;font-weight:700;color:#8b6c14;letter-spacing:1.2px;width:24mm}}
.h-r{{text-align:right}}
.h-mid{{font-size:12pt;font-weight:700;letter-spacing:2px;color:#1a0e04;text-transform:uppercase}}
.footer{{flex:0 0 {FOOTER_H}mm;display:flex;align-items:center;justify-content:space-between;
  border-top:0.6mm solid #8b6c14;padding:0 5mm;font-size:9pt;font-weight:600;color:#8b6c14}}
.body{{flex:1 1 auto;display:flex;flex-direction:row;border:0.3mm solid #d4b870;overflow:hidden}}
.panel{{flex:0 0 {PANEL_PCT}%;background:#f6ead6;border-right:0.4mm solid #d4b870;
  display:flex;flex-direction:column;padding:2mm}}
.pslot{{padding:2mm 1.5mm;border-bottom:0.3mm dashed #d8c9a8}}
.pslot:last-child{{border-bottom:none}}
.pnum{{font-family:'Amiri',serif;font-size:{PANEL_NUM_PT}pt;font-weight:700;color:#8b6c14;
  direction:rtl;line-height:1.3;margin-bottom:0.5mm}}
.ptxt{{font-size:{PANEL_TXT_PT}pt;font-style:italic;color:#2a1a06;line-height:1.5;
  word-wrap:break-word;overflow-wrap:break-word}}
.words{{flex:1 1 auto;display:flex;flex-direction:column}}
.row{{display:flex;flex-direction:row-reverse;align-items:stretch;flex-wrap:nowrap;
  border-bottom:0.25mm solid #ece0c4;page-break-inside:avoid;break-inside:avoid}}
.row:last-child{{border-bottom:none}}
.cell{{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0.6mm 1mm}}
.tr{{font-size:{TR_PT}pt;font-style:italic;color:#a07830;text-align:center;line-height:1.2;
  width:100%;margin-bottom:1.2mm;word-break:break-word;overflow-wrap:break-word}}
.ar{{font-family:'Amiri',serif;font-size:{AR_PT}pt;color:rgba(0,0,0,.18);direction:rtl;
  text-align:center;line-height:1.4;width:100%;white-space:nowrap;padding:0.4mm 0}}
.mn{{font-size:{MN_PT}pt;color:#1e1206;text-align:center;line-height:1.2;width:100%;
  margin-top:1.2mm;word-break:break-word;overflow-wrap:break-word}}
.marker .ar.mk{{color:#c9a84c;font-size:18pt;display:flex;align-items:center;gap:1mm}}
.ruku{{display:inline-flex;align-items:center;justify-content:center;font-family:'Amiri',serif;
  font-size:13pt;color:#1a7a4a;border:0.3mm solid #1a7a4a;border-radius:50%;width:7mm;height:7mm;
  position:relative;line-height:1}}
.ruku-n{{position:absolute;bottom:-2.2mm;font-size:6pt;font-style:normal;color:#1a7a4a;
  font-family:'EB Garamond',serif;font-weight:700}}
.marker .tr{{color:#1a7a4a;font-weight:700;font-size:7pt}}
.open{{flex:1 1 auto;display:flex;flex-direction:column;align-items:center;
  border:0.3mm solid #d4b870}}
.open-juz{{justify-content:flex-start;padding:20mm 16mm}}
.o-eyebrow{{font-size:11pt;font-weight:700;letter-spacing:8px;color:#8b6c14;text-transform:uppercase;margin-bottom:4mm}}
.o-rule{{font-size:13pt;color:#c9a84c;letter-spacing:10px;margin:3mm 0}}
.o-bignum{{font-family:'Amiri',serif;font-size:78pt;font-weight:700;color:#1a0e04;line-height:1}}
.o-arlabel{{font-family:'Amiri',serif;font-size:22pt;color:#8b6c14;direction:rtl;margin-top:3mm}}
.o-intro{{font-size:12pt;font-style:italic;color:#2a1a06;text-align:center;line-height:1.7;padding:0 8mm;margin-top:6mm}}
.open-surah{{justify-content:center;padding:16mm;background:linear-gradient(180deg,#fdf7ed,#faedc6 50%,#fdf7ed)}}
.s-orn{{font-size:16pt;color:#c9a84c;letter-spacing:12px;margin:4mm 0}}
.s-ar{{font-family:'Amiri',serif;font-size:40pt;font-weight:700;color:#1a0e04;direction:rtl;text-align:center;margin:2mm 0}}
.s-en{{font-size:20pt;font-weight:700;letter-spacing:6px;color:#8b6c14;text-transform:uppercase;margin:2mm 0}}
.s-meta{{font-size:11pt;color:#8b6c14;letter-spacing:1px;margin:2mm 0}}
.s-rule{{font-size:14pt;color:#c9a84c;letter-spacing:8px;margin:4mm 0}}
.s-bism{{font-family:'Amiri',serif;font-size:26pt;color:rgba(0,0,0,.18);direction:rtl;margin:5mm 0 3mm}}
@media print{{@page{{size:A4;margin:0}}body{{background:#fdf7ed;padding:0;gap:0}}
  .page{{box-shadow:none;margin:0;page-break-after:always;break-after:page;overflow:visible}}
  .page:last-of-type{{page-break-after:auto;break-after:auto}}
  .body,.words,.panel{{overflow:visible}}.row{{page-break-inside:avoid;break-inside:avoid}}}}
"""

def write_juz(juz):
    pages=build_juz(juz)
    html=(f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>'
          f'<meta name="viewport" content="width=device-width,initial-scale=1.0"/>'
          f'<title>Traceable Quran &mdash; Juz {juz}</title>'
          f'{fonts_block()}<style>{css()}</style></head><body>'
          f'{"".join(pages)}</body></html>')
    out=OUTDIR/f'Juz-{juz:02d}.html'
    out.write_text(html,encoding='utf-8')
    return out,len(pages),out.stat().st_size

if __name__=='__main__':
    import sys
    targets=range(2,31) if len(sys.argv)<2 else [int(x) for x in sys.argv[1:]]
    total=0
    for j in targets:
        out,n,sz=write_juz(j); total+=n
        print(f'Juz {j:2d}: {n:3d} pages, {sz//1024} KB -> {out.name}')
    print(f'Total pages: {total}')
