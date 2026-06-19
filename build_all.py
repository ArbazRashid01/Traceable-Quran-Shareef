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
_SUP  = re.compile(r'<sup[^>]*>.*?</sup>', re.S)   # footnote marker incl. its number
_TAG  = re.compile(r'<[^>]+>')                      # any other HTML tags
_PAREN = re.compile(r'[\(\[][^\)\]]*[\)\]]')
def ar_base_len(s): return sum(1 for c in _DIAC.sub('', s or '') if '\u0600' <= c <= '\u06FF')
def clean_m(s):
    s = _SUP.sub('', s or '')                       # drop footnote markers + numbers
    s = _TAG.sub('', s)                             # drop any remaining tags
    s = _PAREN.sub('', s)
    return s.replace('  ', ' ').strip(' ,;:.')
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

# ─── PANEL FLOW (meanings carry across pages; nothing truncated) ──
PANEL_W_MM        = (BODY_W * PANEL_PCT/100) - 4 - 3   # usable text width inside pslot
PANEL_CPL         = max(12, int(PANEL_W_MM / 1.95))    # chars per line @ 11pt
PANEL_LINE_MM     = 11 * 0.3528 * 1.5                   # 11pt * 1.5 line-height
PANEL_HEAD_MM     = 7.0                                  # verse-number heading + slot padding
PANEL_CONT_MM     = 3.0                                  # continuation block top padding
PANEL_USABLE_MM   = BODY_H - 8

def wrap_lines(text):
    words=(text or '').split(); lines=[]; cur=''
    for w in words:
        if len(w) > PANEL_CPL:
            if cur: lines.append(cur); cur=''
            while len(w) > PANEL_CPL:
                lines.append(w[:PANEL_CPL]); w=w[PANEL_CPL:]
            cur=w
        elif not cur:
            cur=w
        elif len(cur)+1+len(w) <= PANEL_CPL:
            cur+=' '+w
        else:
            lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines or ['']

def meaning_block(vk):
    return {'num': int(vk.split(':')[1]), 'lines': wrap_lines(clean_m(VS[vk]['m']))}

def flow_panel(new_blocks, carry):
    """Place blocks into one page's panel; return (rendered_html, leftover_carry)."""
    avail = PANEL_USABLE_MM
    queue = list(carry) + list(new_blocks)
    out = []; leftover = []
    i = 0
    while i < len(queue):
        blk = queue[i]
        head = PANEL_HEAD_MM if blk['num'] is not None else PANEL_CONT_MM
        if out and avail < head + PANEL_LINE_MM:
            leftover = queue[i:]; break
        avail -= head
        fit = int(avail // PANEL_LINE_MM)
        if fit >= len(blk['lines']):
            avail -= len(blk['lines']) * PANEL_LINE_MM
            out.append(blk); i += 1
        else:
            if fit > 0:
                out.append({'num': blk['num'], 'lines': blk['lines'][:fit]})
                leftover = [{'num': None, 'lines': blk['lines'][fit:]}] + queue[i+1:]
            else:
                leftover = queue[i:]
            break
    return render_panel(out), leftover

def render_panel(blocks):
    out = []
    for b in blocks:
        num = (f'<div class="pnum">{ar(b["num"])}</div>' if b['num'] is not None
               else '<div class="pnum pcont">&#8230;</div>')
        txt = _esc(' '.join(b['lines']))
        out.append(f'<div class="pslot">{num}<div class="ptxt">{txt}</div></div>')
    return '<div class="panel">'+''.join(out)+'</div>'

def header(juz,mid,pg):
    return (f'<div class="header"><span class="h-side">JUZ {juz}</span>'
            f'<span class="h-mid">&#10022; {mid} &#10022;</span>'
            f'<span class="h-side h-r">PAGE {pg}</span></div>')

def footer(left,pg,juz):
    return (f'<div class="footer"><span>{left}</span>'
            f'<span>Page {pg} &middot; Juz {juz}</span></div>')

def completing_keys(rows):
    done=[]
    for r in rows:
        for it in r:
            if it['k']=='M' and it['vk'] not in done:
                done.append(it['vk'])
    return done

def row_fill_mm(rows):
    return sum(row_h(r) for r in rows)

def end_ornament(label):
    return (f'<div class="endmark"><div class="endmark-orn">&#10059;</div>'
            f'<div class="endmark-txt">End of Surah {label}</div>'
            f'<div class="endmark-orn">&#10059;</div></div>')

def page_std(juz,pg,label,rows,panel_html,decorate=False):
    words = ''.join(em_row(r) for r in rows)
    if decorate:
        words += end_ornament(label.title())
    return (f'<div class="page"><div class="inner">{header(juz,label,pg)}'
            f'<div class="body">{panel_html}<div class="words">'
            f'{words}</div></div>'
            f'{footer(label,pg,juz)}</div></div>')

def page_panel_cont(juz,pg,label,panel_html):
    """Panel-only continuation page (carries leftover verse meanings)."""
    note = ('<div class="contnote"><div class="endmark-orn">&#10059;</div>'
            '<div class="endmark-txt">Continued verse meanings</div></div>')
    return (f'<div class="page"><div class="inner">{header(juz,label,pg)}'
            f'<div class="body">{panel_html}<div class="words">{note}</div></div>'
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
    # 1) Build layout: openers + standard pages (rows + completing verse keys)
    layout=[('openjuz',)]
    for ch,vks in chapter_segments(juz):
        label=CH[ch]['name_en'].upper()
        if vks and vks[0].endswith(':1'):
            layout.append(('opensurah', ch))
        rows_pages=paginate(pack(make_items(vks,rmap)))
        for k,pr in enumerate(rows_pages):
            is_last = (k==len(rows_pages)-1)
            layout.append(('std', label, pr, completing_keys(pr), is_last))

    # 2) Render pages, flowing panel meanings with carry-over
    pages=[]; pno=0; carry=[]; FILL_LIMIT=BODY_H*0.55
    for item in layout:
        if item[0]=='openjuz':
            pno+=1; pages.append(page_juz_opener(juz,pno)); continue
        if item[0]=='opensurah':
            pno+=1; pages.append(page_surah_opener(juz,pno,item[1])); continue
        _,label,rows,comp,is_last=item
        blocks=[meaning_block(vk) for vk in comp]
        panel_html, carry = flow_panel(blocks, carry)
        decorate = is_last and (row_fill_mm(rows) < FILL_LIMIT) and not carry
        pno+=1
        pages.append(page_std(juz,pno,label,rows,panel_html,decorate))
    # 3) Flush remaining carried meanings onto continuation pages
    last_label = layout[-1][1] if layout[-1][0]=='std' else 'JUZ'
    while carry:
        panel_html, carry = flow_panel([], carry)
        pno+=1
        pages.append(page_panel_cont(juz,pno,last_label,panel_html))
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
.pcont{{color:#b08820;font-weight:400}}
.endmark{{display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:2mm;padding:10mm 0;margin-top:6mm}}
.endmark-orn{{font-size:18pt;color:#c9a84c}}
.endmark-txt{{font-size:11pt;font-style:italic;letter-spacing:2px;color:#8b6c14}}
.contnote{{display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:2mm;height:100%;color:#b8a988}}
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
    suffix=globals().get('VARIANT','')
    tsuf=globals().get('TITLE_SUFFIX','')
    html=(f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>'
          f'<meta name="viewport" content="width=device-width,initial-scale=1.0"/>'
          f'<title>Traceable Quran &mdash; Juz {juz}{tsuf}</title>'
          f'{fonts_block()}<style>{css()}{EDITOR_CSS}</style></head><body>'
          f'{EDITOR_BAR}{"".join(pages)}{EDITOR_JS}</body></html>')
    out=OUTDIR/f'Juz-{juz:02d}{suffix}.html'
    out.write_text(html,encoding='utf-8')
    return out,len(pages),out.stat().st_size

def _main():
    import sys
    targets=range(2,31) if len(sys.argv)<2 else [int(x) for x in sys.argv[1:]]
    total=0
    for j in targets:
        out,n,sz=write_juz(j); total+=n
        print(f'Juz {j:2d}: {n:3d} pages, {sz//1024} KB -> {out.name}')
    print(f'Total pages: {total}')



# ═══════════════════════════════════════════════════════════════
# IN-BROWSER EDITOR  (Edit Mode toolbar + change-only persistence)
# Editable: Arabic words, transliterations, meanings, verse meanings,
#           headers, surah/juz opener text. Saves ONLY changed cells.
# ═══════════════════════════════════════════════════════════════
EDITOR_CSS = """
#tqbar{position:fixed;top:0;left:0;right:0;z-index:9999;display:flex;
  align-items:center;gap:8px;flex-wrap:wrap;background:#1a0e04;
  padding:8px 14px;box-shadow:0 2px 10px rgba(0,0,0,.45)}
#tqbar .t{color:#f0e4c0;font:700 12px Georgia,serif;letter-spacing:1px;margin-right:auto}
#tqbar button{background:#c9a84c;color:#1a0e04;border:none;padding:7px 14px;
  border-radius:5px;cursor:pointer;font:700 12px Georgia,serif;letter-spacing:.4px}
#tqbar button:hover{background:#e8c050}
#tqbar button.alt{background:#5a4a2a;color:#f0e4c0}
#tqbar button.on{background:#1a7a4a;color:#fff}
#tqbar .s{color:#bda;font:italic 11px Georgia,serif}
body.tqedit [data-tq]{cursor:text}
body.tqedit [data-tq]:hover{background:rgba(201,168,76,.25);border-radius:3px}
body.tqedit [data-tq]:focus{background:#fffbe9;box-shadow:0 0 0 2px #c9a84c;
  border-radius:3px;outline:none}
body.tqpad{padding-top:46px}
@media print{#tqbar{display:none}body.tqpad{padding-top:0}#tqcolors{display:none!important}}

/* ── COLOUR VARIABLES + OVERRIDES (live-editable theme) ── */
:root{
  --c-sheet:#fdf7ed; --c-words:#fdf7ed; --c-panel:#f6ead6; --c-header:#f8f0dc;
  --c-arabic:rgba(0,0,0,0.18); --c-translit:#a07830; --c-meaning:#1e1206;
  --c-vmeaning:#2a1a06; --c-gold:#c9a84c;
}
.page{background:var(--c-sheet)!important;border-color:var(--c-gold)!important}
.words{background:var(--c-words)!important}
.panel{background:var(--c-panel)!important}
.header{background:var(--c-header)!important}
.ar{color:var(--c-arabic)!important}
.marker .ar.mk{color:var(--c-gold)!important}
.tr{color:var(--c-translit)!important}
.mn{color:var(--c-meaning)!important}
.ptxt,.pnum{color:var(--c-vmeaning)!important}

/* ── COLOUR PANEL ── */
#tqcolors{position:fixed;top:46px;right:10px;z-index:9998;width:250px;
  background:#fdf7ed;border:1.5px solid #c9a84c;border-radius:8px;
  box-shadow:0 8px 28px rgba(0,0,0,.4);padding:12px 14px;display:none;
  font:12px Georgia,serif;color:#1a0e04;max-height:82vh;overflow:auto}
#tqcolors.show{display:block}
#tqcolors h4{font-size:12px;letter-spacing:1px;color:#8b6c14;margin:0 0 8px;
  text-transform:uppercase;border-bottom:1px solid #d4b870;padding-bottom:5px}
.tqrow{display:flex;align-items:center;justify-content:space-between;
  gap:8px;margin:7px 0}
.tqrow label{font-size:11.5px;color:#2a1a06}
.tqrow input[type=color]{width:34px;height:24px;border:1px solid #c9a84c;
  border-radius:4px;background:none;cursor:pointer;padding:0}
.tqrow input[type=range]{width:90px}
#tqcolors .presets{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 10px}
#tqcolors .presets button{flex:1;min-width:60px;font-size:10px;padding:5px 4px;
  border:1px solid #c9a84c;border-radius:4px;cursor:pointer;background:#f6ead6;color:#1a0e04}
#tqcolors .presets button:hover{background:#ece0c4}
"""

EDITOR_BAR = ('<div id="tqbar">'
  '<span class="t">TRACEABLE QURAN &middot; EDIT</span>'
  '<button id="tqEdit" onclick="tqToggle()">&#9998; Edit Mode</button>'
  '<button class="alt" onclick="tqColors()">&#127912; Colors</button>'
  '<button class="alt" onclick="tqReset()">&#8635; Reset</button>'
  '<button onclick="tqExport()">&#10515; Save / Export</button>'
  '<span class="s" id="tqStatus"></span></div>'
  '<div id="tqcolors">'
    '<h4>Theme Presets</h4>'
    '<div class="presets">'
      '<button onclick="tqPreset(\'ivory\')">Ivory</button>'
      '<button onclick="tqPreset(\'white\')">White</button>'
      '<button onclick="tqPreset(\'sepia\')">Sepia</button>'
      '<button onclick="tqPreset(\'night\')">Night</button>'
      '<button onclick="tqPreset(\'mint\')">Mint</button>'
    '</div>'
    '<h4>Custom Colours</h4>'
    '<div class="tqrow"><label>Sheet background</label>'
      '<input type="color" id="cv-sheet" data-var="--c-sheet"></div>'
    '<div class="tqrow"><label>Word area background</label>'
      '<input type="color" id="cv-words" data-var="--c-words"></div>'
    '<div class="tqrow"><label>Meaning box background</label>'
      '<input type="color" id="cv-panel" data-var="--c-panel"></div>'
    '<div class="tqrow"><label>Header background</label>'
      '<input type="color" id="cv-header" data-var="--c-header"></div>'
    '<div class="tqrow"><label>Border / accent</label>'
      '<input type="color" id="cv-gold" data-var="--c-gold"></div>'
    '<h4>Text Colours</h4>'
    '<div class="tqrow"><label>Arabic trace</label>'
      '<input type="color" id="cv-arabic"></div>'
    '<div class="tqrow"><label>Arabic darkness</label>'
      '<input type="range" id="cv-arabic-op" min="8" max="100" value="18"></div>'
    '<div class="tqrow"><label>Transliteration</label>'
      '<input type="color" id="cv-translit" data-var="--c-translit"></div>'
    '<div class="tqrow"><label>Word meaning</label>'
      '<input type="color" id="cv-meaning" data-var="--c-meaning"></div>'
    '<div class="tqrow"><label>Verse meaning</label>'
      '<input type="color" id="cv-vmeaning" data-var="--c-vmeaning"></div>'
  '</div>')


EDITOR_JS = """<script>
(function(){
  // Editable content selectors (Arabic, translit, meaning, panel, headers, openers)
  var SEL=['.ar','.tr','.mn','.pnum','.ptxt','.h-mid',
           '.s-ar','.s-en','.s-meta','.o-bignum','.o-arlabel','.o-intro',
           '.c-para','.c-title','.c-subtitle','.c-arabic-main','.c-section',
           '.c-arabic-hadith','.khatm-ar','.khatm-msg','.cover-main-ar',
           '.cover-main-en','.cover-sub','.cover-desc'];
  var KEY='tqedits::'+document.title;
  var nodes=[];
  function collect(){
    nodes=[];
    var seen=new Set();
    SEL.forEach(function(s){
      document.querySelectorAll(s).forEach(function(el){
        if(el.closest('#tqbar')) return;
        if(seen.has(el)) return; seen.add(el); nodes.push(el);
      });
    });
    nodes.forEach(function(el,i){el.setAttribute('data-tq',i);});
  }
  function load(){
    var raw=localStorage.getItem(KEY); if(!raw) return;
    try{var d=JSON.parse(raw);
      Object.keys(d).forEach(function(i){ if(nodes[i]) nodes[i].innerHTML=d[i]; });
      status('Loaded your saved edits');
    }catch(e){}
  }
  function save(){
    var d={};
    nodes.forEach(function(el,i){
      var orig=el.getAttribute('data-orig');
      if(orig===null){orig=el.getAttribute('data-orig')||'';}
      if(el.innerHTML!==el.dataset.orig){ d[i]=el.innerHTML; }
    });
    try{localStorage.setItem(KEY,JSON.stringify(d));
        status('Saved \u2713 '+new Date().toLocaleTimeString());}
    catch(e){status('Storage full \u2014 use Export instead');}
  }
  var editing=false,t;
  window.tqToggle=function(){
    editing=!editing;
    document.body.classList.toggle('tqedit',editing);
    var b=document.getElementById('tqEdit');
    b.classList.toggle('on',editing);
    b.innerHTML=editing?'\u2713 Editing (click text)':'\u270e Edit Mode';
    nodes.forEach(function(el){el.contentEditable=editing?'true':'false';});
    document.querySelectorAll('a').forEach(function(a){
      a.onclick=function(e){if(editing)e.preventDefault();};});
    status(editing?'Edit mode ON \u2014 click any word, transliteration or meaning':'Edit mode off');
  };
  window.tqReset=function(){
    if(!confirm('Clear all your edits on this Juz and restore the original text?'))return;
    localStorage.removeItem(KEY); location.reload();
  };
  window.tqExport=function(){
    var c=document.documentElement.cloneNode(true);
    var bar=c.querySelector('#tqbar'); if(bar)bar.remove();
    c.querySelectorAll('[contenteditable]').forEach(function(e){e.setAttribute('contenteditable','false');});
    var b=c.querySelector('body'); if(b)b.classList.remove('tqedit');
    var html='<!DOCTYPE html>\\n'+c.outerHTML;
    var blob=new Blob([html],{type:'text/html'});
    var u=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=u; a.download=document.title.replace(/[^A-Za-z0-9]+/g,'-')+'.html'; a.click();
    URL.revokeObjectURL(u); status('Exported edited file \u2713');
  };
  function status(m){document.getElementById('tqStatus').textContent=m;}
  document.addEventListener('input',function(){if(!editing)return;clearTimeout(t);t=setTimeout(save,500);});

  /* ── COLOUR THEME ENGINE ── */
  var CKEY='tqcolors::'+document.title;
  var root=document.documentElement;
  var PRESETS={
    ivory:{'--c-sheet':'#fdf7ed','--c-words':'#fdf7ed','--c-panel':'#f6ead6','--c-header':'#f8f0dc','--c-gold':'#c9a84c','--c-translit':'#a07830','--c-meaning':'#1e1206','--c-vmeaning':'#2a1a06','--c-arabic':'rgba(0,0,0,0.18)'},
    white:{'--c-sheet':'#ffffff','--c-words':'#ffffff','--c-panel':'#f4f4f2','--c-header':'#eeeeee','--c-gold':'#b8964a','--c-translit':'#8a6a28','--c-meaning':'#1a1a1a','--c-vmeaning':'#222222','--c-arabic':'rgba(0,0,0,0.20)'},
    sepia:{'--c-sheet':'#f3e7d0','--c-words':'#f3e7d0','--c-panel':'#ead9bb','--c-header':'#e6d3ad','--c-gold':'#a9852f','--c-translit':'#8a5a1c','--c-meaning':'#3a2410','--c-vmeaning':'#43301a','--c-arabic':'rgba(40,20,0,0.22)'},
    night:{'--c-sheet':'#222018','--c-words':'#222018','--c-panel':'#2c2a20','--c-header':'#1a1812','--c-gold':'#c9a84c','--c-translit':'#d8b36a','--c-meaning':'#ece0c4','--c-vmeaning':'#e6d8b8','--c-arabic':'rgba(255,255,255,0.28)'},
    mint:{'--c-sheet':'#eef6f0','--c-words':'#eef6f0','--c-panel':'#dcebe0','--c-header':'#d6e8da','--c-gold':'#4a9e74','--c-translit':'#2f7a52','--c-meaning':'#13301f','--c-vmeaning':'#1c3a28','--c-arabic':'rgba(0,40,20,0.20)'}
  };
  function hexToRgba(hex,a){var n=hex.replace('#','');
    var r=parseInt(n.substr(0,2),16),g=parseInt(n.substr(2,2),16),b=parseInt(n.substr(4,2),16);
    return 'rgba('+r+','+g+','+b+','+a+')';}
  function rgbaParts(v){var m=/rgba?\\(([^)]+)\\)/.exec(v);if(!m)return null;
    var p=m[1].split(',');return {r:+p[0],g:+p[1],b:+p[2],a:p[3]!==undefined?+p[3]:1};}
  function rgbToHex(r,g,b){return '#'+[r,g,b].map(function(x){return ('0'+(x|0).toString(16)).slice(-2);}).join('');}
  function applyVars(map){Object.keys(map).forEach(function(k){root.style.setProperty(k,map[k]);});}
  function saveColors(){
    var d={}; ['--c-sheet','--c-words','--c-panel','--c-header','--c-gold',
      '--c-translit','--c-meaning','--c-vmeaning','--c-arabic'].forEach(function(k){
        var v=root.style.getPropertyValue(k); if(v) d[k]=v.trim(); });
    localStorage.setItem(CKEY,JSON.stringify(d));
    status('Theme saved \\u2713');
  }
  function syncPickers(){
    document.querySelectorAll('#tqcolors input[data-var]').forEach(function(inp){
      var cur=getComputedStyle(root).getPropertyValue(inp.dataset.var).trim();
      if(cur && cur[0]==='#') inp.value=cur;
      else if(cur.indexOf('rgb')===0){var p=rgbaParts(cur);if(p)inp.value=rgbToHex(p.r,p.g,p.b);}
    });
    var av=getComputedStyle(root).getPropertyValue('--c-arabic').trim();
    var p=rgbaParts(av);
    if(p){document.getElementById('cv-arabic').value=rgbToHex(p.r,p.g,p.b);
          document.getElementById('cv-arabic-op').value=Math.round(p.a*100);}
  }
  window.tqColors=function(){document.getElementById('tqcolors').classList.toggle('show');syncPickers();};
  window.tqPreset=function(name){applyVars(PRESETS[name]);saveColors();syncPickers();status('Applied '+name+' theme');};
  // wire pickers
  function wireColors(){
    document.querySelectorAll('#tqcolors input[data-var]').forEach(function(inp){
      inp.addEventListener('input',function(){root.style.setProperty(inp.dataset.var,inp.value);saveColors();});
    });
    function setArabic(){
      var hex=document.getElementById('cv-arabic').value;
      var op=(+document.getElementById('cv-arabic-op').value)/100;
      root.style.setProperty('--c-arabic',hexToRgba(hex,op));saveColors();
    }
    document.getElementById('cv-arabic').addEventListener('input',setArabic);
    document.getElementById('cv-arabic-op').addEventListener('input',setArabic);
  }
  function loadColors(){
    var raw=localStorage.getItem(CKEY); if(!raw)return;
    try{applyVars(JSON.parse(raw));}catch(e){}
  }
  document.body.classList.add('tqpad');
  collect();
  nodes.forEach(function(el){el.dataset.orig=el.innerHTML;});
  load();
  wireColors();
  loadColors();
})();
</script>"""



if __name__ == '__main__':
    _main()
