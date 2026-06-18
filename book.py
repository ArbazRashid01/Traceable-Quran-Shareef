#!/usr/bin/env python3
"""
Traceable Quran Workbook — Publishing Engine (built from first principles)

DESIGN:
  * Content-driven cell widths (Arabic char count is primary factor)
  * Greedy RTL row packing — words fill a row until it is full
  * Adaptive row heights — row grows to its tallest cell
  * Pre-computed pagination — no row ever splits across a page
  * Three page types: Juz opener (A), Surah opener (B), Standard (C)

This file is self-contained. It imports only raw Quran data
(WORDS, MEANINGS, ar) from generate.py — no old layout logic.
"""
import re, base64
from pathlib import Path
from generate import WORDS, MEANINGS, ar

BASE     = Path(__file__).parent
FONT_DIR = BASE / 'fonts'
OUT      = BASE / 'Traceable-Quran-Juz1.html'

# ─── PAGE GEOMETRY (mm) ──────────────────────────────────────────
PAGE_W, PAGE_H = 210, 297
PAD            = 12
FRAME_W        = 0.5
HEADER_H       = 14
FOOTER_H       = 10
BODY_W         = PAGE_W - 2*PAD - 2*FRAME_W          # 185
BODY_H         = PAGE_H - 2*PAD - 2*FRAME_W - HEADER_H - FOOTER_H   # 248

# Column split
PANEL_PCT      = 24                                  # left meaning panel
WORD_W_MM      = BODY_W * (100 - PANEL_PCT) / 100    # ~140.6 mm usable for words

# ─── TYPOGRAPHY (pt) ─────────────────────────────────────────────
AR_PT          = 15      # Arabic — traceable, dense layout (target <30 pages)
TR_PT          = 9       # transliteration
MN_PT          = 9       # word meaning
PANEL_NUM_PT   = 12      # ayah number in panel
PANEL_TXT_PT   = 11      # verse meaning in panel

# ─── WIDTH MODEL (mm per character, empirically calibrated) ──────
AR_CHAR_MM     = 2.45    # 15pt Amiri base char (connected-script calibrated, safe)
TR_CHAR_MM     = 1.55
MN_CHAR_MM     = 1.55
CELL_PAD_MM    = 3
CELL_MIN_MM    = 10
CELL_MAX_MM    = WORD_W_MM

ROW_BASE_MM    = 15      # 1-line tr + 15pt arabic + 1-line mn + tight padding
ROW_LINE_MM    = 3.4

# ─── DIACRITIC STRIP (for width measurement only) ────────────────
_DIAC  = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]')
_PAREN = re.compile(r'[\(\[][^\)\]]*[\)\]]')

def ar_base_len(s):
    return sum(1 for c in _DIAC.sub('', s or '') if '\u0600' <= c <= '\u06FF')

def clean_meaning(s):
    return _PAREN.sub('', s or '').replace('  ', ' ').strip(' ,;:.')



# ─── MEASUREMENT ─────────────────────────────────────────────────

def _longest_token_mm(text, char_mm):
    """Width of the single longest unbreakable word (cannot wrap mid-word)."""
    toks = (text or '').split()
    if not toks:
        return 0
    return max(len(t) for t in toks) * char_mm

def cell_width_mm(arabic, translit, meaning):
    """
    Arabic is the primary width driver. Transliteration and meaning may
    wrap to 2 lines, so they only force extra width if a single unbreakable
    word is wider than the Arabic.
    """
    aw = ar_base_len(arabic) * AR_CHAR_MM
    mn = clean_meaning(meaning)
    # tr/mn can wrap — only their longest single token must fit
    tw = _longest_token_mm(translit, TR_CHAR_MM)
    mw = _longest_token_mm(mn, MN_CHAR_MM)
    w  = max(aw, tw, mw) + CELL_PAD_MM
    return max(CELL_MIN_MM, min(CELL_MAX_MM, w))

def cell_height_mm(arabic, translit, meaning, width_mm):
    """Estimate cell height — grows if translit or meaning wraps."""
    usable = width_mm - CELL_PAD_MM
    tr_lines = max(1, _ceil(len(translit or '') * TR_CHAR_MM / usable))
    mn_lines = max(1, _ceil(len(clean_meaning(meaning)) * MN_CHAR_MM / usable))
    extra = (tr_lines - 1 + mn_lines - 1) * ROW_LINE_MM
    return ROW_BASE_MM + extra

def _ceil(x):
    import math
    return int(math.ceil(x))


# ─── ROW PACKING (greedy, RTL, per-verse) ────────────────────────

def pack_verse_rows(verse_items):
    """Pack ONE verse's items into rows that fit within WORD_W_MM.
    A verse never shares a row with another verse."""
    rows, cur, cur_w = [], [], 0.0
    for it in verse_items:
        w = it['width']
        if cur and cur_w + w > WORD_W_MM:
            rows.append(cur)
            cur, cur_w = [], 0.0
        cur.append(it)
        cur_w += w
    if cur:
        rows.append(cur)
    return rows

def build_verse_blocks(verse_keys):
    """Return list of (verse_key, rows) — each verse as its own block."""
    blocks = []
    for vk in verse_keys:
        items = [make_word_item(vk, i) for i in range(len(WORDS[vk]))]
        items.append(make_marker_item(vk))
        blocks.append((vk, pack_verse_rows(items)))
    return blocks

def row_height(row):
    return max(it['height'] for it in row)

def block_height(rows):
    return sum(row_height(r) for r in rows)


# ─── CONTINUOUS DENSE PACKING (cross-verse, fills every page) ─────

def pack_all_rows(verse_keys):
    """All words of all verses flow continuously into full rows."""
    items = []
    for vk in verse_keys:
        for i in range(len(WORDS[vk])):
            items.append(make_word_item(vk, i))
        items.append(make_marker_item(vk))
    rows, cur, cur_w = [], [], 0.0
    for it in items:
        w = it['width']
        if cur and cur_w + w > WORD_W_MM:
            rows.append(cur)
            cur, cur_w = [], 0.0
        cur.append(it)
        cur_w += w
    if cur:
        rows.append(cur)
    return rows

def paginate_rows(rows):
    """Fill each page with rows up to BODY_H — near-100% fill on all but last."""
    limit = BODY_H - 2
    pages, cur, cur_h = [], [], 0.0
    for r in rows:
        h = row_height(r)
        if cur and cur_h + h > limit:
            pages.append(cur)
            cur, cur_h = [], 0.0
        cur.append(r)
        cur_h += h
    if cur:
        pages.append(cur)
    return pages

def verses_in_rows(page_rows):
    seen = []
    for row in page_rows:
        for it in row:
            if it['vk'] not in seen:
                seen.append(it['vk'])
    return seen


# ─── PAGINATION — pages end at a complete ayah whenever possible ──
# Only a verse that is itself taller than a full page is split (Mushaf-style).

def paginate_blocks(blocks):
    limit = BODY_H - 3
    pages, cur, cur_h = [], [], 0.0

    def flush():
        nonlocal cur, cur_h
        if cur:
            pages.append(cur)
            cur, cur_h = [], 0.0

    for vk, rows in blocks:
        bh = block_height(rows)

        if bh <= limit:
            # Whole verse fits on a page — keep it intact
            if cur and cur_h + bh > limit:
                flush()
            cur.append((vk, rows))
            cur_h += bh
        else:
            # Verse longer than a page — must span pages, split at row boundaries
            flush()
            chunk, chunk_h = [], 0.0
            for r in rows:
                h = row_height(r)
                if chunk and chunk_h + h > limit:
                    pages.append([(vk, chunk)])
                    chunk, chunk_h = [], 0.0
                chunk.append(r)
                chunk_h += h
            if chunk:
                cur.append((vk, chunk))
                cur_h += chunk_h
    flush()
    return pages



# ─── ITEM BUILDERS ───────────────────────────────────────────────

def make_word_item(vk, widx):
    ar_text, tr_text, en_text = WORDS[vk][widx]
    w = cell_width_mm(ar_text, tr_text, en_text)
    h = cell_height_mm(ar_text, tr_text, en_text, w)
    return {
        'kind': 'word', 'vk': vk,
        'ar': ar_text,
        'tr': tr_text or '',
        'mn': clean_meaning(en_text),
        'width': w, 'height': h,
    }

def make_marker_item(vk):
    n = int(vk.split(':')[1])
    return {
        'kind': 'marker', 'vk': vk, 'num': n,
        'width': CELL_MIN_MM, 'height': ROW_BASE_MM,
    }

def build_surah_items(verse_keys):
    items = []
    for vk in verse_keys:
        for i in range(len(WORDS[vk])):
            items.append(make_word_item(vk, i))
        items.append(make_marker_item(vk))
    return items


# ─── HTML EMITTERS ───────────────────────────────────────────────

def emit_word(it):
    flex_basis = f'{it["width"]:.1f}mm'
    return (
        f'<div class="cell" style="flex:0 1 {flex_basis}">'
        f'<div class="tr">{_esc(it["tr"])}</div>'
        f'<div class="ar">{it["ar"]}</div>'
        f'<div class="mn">{_esc(it["mn"])}</div>'
        f'</div>'
    )

def emit_marker(it):
    glyph = f'&#1757;{ar(it["num"])}'
    return (
        f'<div class="cell marker" style="flex:0 0 {CELL_MIN_MM}mm">'
        f'<div class="tr">&nbsp;</div>'
        f'<div class="ar mk">{glyph}</div>'
        f'<div class="mn">&nbsp;</div>'
        f'</div>'
    )

def emit_row(row):
    cells = ''.join(emit_marker(it) if it['kind']=='marker' else emit_word(it) for it in row)
    return f'<div class="row">{cells}</div>'

def _esc(s):
    return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')



# ─── PANEL (left verse-meaning column) ───────────────────────────

def verses_in_blocks(page_blocks):
    return [vk for vk, _ in page_blocks]

def emit_panel(verse_keys):
    items = []
    for vk in verse_keys:
        n = ar(int(vk.split(':')[1]))
        meaning = clean_meaning(MEANINGS.get(vk, ''))
        items.append(
            f'<div class="pslot">'
            f'<div class="pnum">{n}</div>'
            f'<div class="ptxt">{_esc(meaning)}</div>'
            f'</div>'
        )
    return f'<div class="panel">{"".join(items)}</div>'


# ─── PAGE SHELLS ─────────────────────────────────────────────────

def header(juz, mid, page):
    return (
        f'<div class="header">'
        f'<span class="h-side">JUZ {juz}</span>'
        f'<span class="h-mid">&#10022; {mid} &#10022;</span>'
        f'<span class="h-side h-r">PAGE {page}</span>'
        f'</div>'
    )

def footer(left, page, juz):
    return (
        f'<div class="footer">'
        f'<span>{left}</span>'
        f'<span>Page {page} &middot; Juz {juz}</span>'
        f'</div>'
    )

def page_standard(juz, page_no, surah_label, page_rows):
    panel = emit_panel(verses_in_rows(page_rows))
    rows_html = ''.join(emit_row(r) for r in page_rows)
    return (
        f'<div class="page"><div class="inner">'
        f'{header(juz, surah_label, page_no)}'
        f'<div class="body">{panel}<div class="words">{rows_html}</div></div>'
        f'{footer(surah_label, page_no, juz)}'
        f'</div></div>'
    )



def page_juz_opener(juz, page_no, title_ar, intro, themes):
    return (
        f'<div class="page"><div class="inner">'
        f'{header(juz, "JUZ OPENING", page_no)}'
        f'<div class="open open-juz">'
        f'<div class="o-eyebrow">PARA &middot; JUZ</div>'
        f'<div class="o-rule">&middot; &middot; &middot;</div>'
        f'<div class="o-bignum">{juz}</div>'
        f'<div class="o-arlabel">{title_ar}</div>'
        f'<div class="o-rule">&middot; &middot; &middot;</div>'
        f'<div class="o-intro">{intro}</div>'
        f'<div class="o-themewrap"><div class="o-themetitle">KEY THEMES</div>'
        f'<div class="o-themes">{themes}</div></div>'
        f'</div>'
        f'{footer("Juz Opening", page_no, juz)}'
        f'</div></div>'
    )

def page_surah_opener(juz, page_no, sd):
    return (
        f'<div class="page"><div class="inner">'
        f'{header(juz, sd["english"].upper(), page_no)}'
        f'<div class="open open-surah">'
        f'<div class="s-orn">&#10022; &#10022; &#10022;</div>'
        f'<div class="s-ar">{sd["arabic"]}</div>'
        f'<div class="s-en">{sd["english"]}</div>'
        f'<div class="s-meta">Surah {sd["no"]} &middot; {sd["meaning"]} &middot; '
        f'{sd["revealed"]} &middot; {sd["verses"]} Verses</div>'
        f'<div class="s-rule">&middot; &middot; &middot;</div>'
        f'<div class="s-overview">{sd["overview"]}</div>'
        f'<div class="s-bism">&#1576;&#1616;&#1587;&#1618;&#1605;&#1616; &#1649;&#1604;&#1604;&#1617;&#1614;&#1607;&#1616; '
        f'&#1649;&#1604;&#1585;&#1617;&#1614;&#1581;&#1618;&#1605;&#1614;&#1648;&#1606;&#1616; '
        f'&#1649;&#1604;&#1585;&#1617;&#1614;&#1581;&#1616;&#1610;&#1605;&#1616;</div>'
        f'<div class="s-orn">&#10022; &#10022; &#10022;</div>'
        f'</div>'
        f'{footer(sd["english"] + " Opening", page_no, juz)}'
        f'</div></div>'
    )



# ─── CSS ─────────────────────────────────────────────────────────
def build_css():
    return f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#9e8f72;font-family:'EB Garamond','Georgia',serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{display:flex;flex-direction:column;align-items:center;padding:28px 0;gap:28px}}

/* PAGE */
.page{{position:relative;width:{PAGE_W}mm;height:{PAGE_H}mm;padding:{PAD}mm;
  background:#fdf7ed;border:{FRAME_W}mm solid #c9a84c;
  box-shadow:0 0 0 1.5mm #fdf7ed,0 0 0 2mm #c9a84c,0 12px 50px rgba(0,0,0,.30);
  overflow:hidden}}
.page::before{{content:'';position:absolute;top:4.5mm;right:4.5mm;bottom:4.5mm;left:4.5mm;
  border:0.3mm solid rgba(201,168,76,.4);pointer-events:none}}
.inner{{position:relative;width:100%;height:100%;display:flex;flex-direction:column}}

/* HEADER / FOOTER */
.header{{flex:0 0 {HEADER_H}mm;display:flex;align-items:center;justify-content:space-between;
  background:#f8f0dc;border-top:0.6mm solid #8b6c14;border-bottom:0.6mm solid #8b6c14;
  box-shadow:inset 0 0.6mm 0 #e8d49a,inset 0 -0.6mm 0 #e8d49a;padding:0 5mm}}
.h-side{{font-size:9pt;font-weight:700;color:#8b6c14;letter-spacing:1.2px;width:24mm}}
.h-r{{text-align:right}}
.h-mid{{font-size:12pt;font-weight:700;letter-spacing:2px;color:#1a0e04;text-transform:uppercase}}
.footer{{flex:0 0 {FOOTER_H}mm;display:flex;align-items:center;justify-content:space-between;
  border-top:0.6mm solid #8b6c14;padding:0 5mm;font-size:9pt;font-weight:600;color:#8b6c14}}

/* BODY: panel | words */
.body{{flex:1 1 auto;display:flex;flex-direction:row;border:0.3mm solid #d4b870;overflow:hidden}}

/* LEFT PANEL */
.panel{{flex:0 0 {PANEL_PCT}%;background:#f6ead6;border-right:0.4mm solid #d4b870;
  display:flex;flex-direction:column;padding:2mm}}
.pslot{{padding:2mm 1.5mm;border-bottom:0.3mm dashed #d8c9a8}}
.pslot:last-child{{border-bottom:none}}
.pnum{{font-family:'Amiri',serif;font-size:{PANEL_NUM_PT}pt;font-weight:700;color:#8b6c14;
  direction:rtl;line-height:1.3;margin-bottom:0.5mm}}
.ptxt{{font-size:{PANEL_TXT_PT}pt;font-style:italic;color:#2a1a06;line-height:1.5;
  word-wrap:break-word;overflow-wrap:break-word}}

/* WORD AREA */
.words{{flex:1 1 auto;display:flex;flex-direction:column}}
.row{{display:flex;flex-direction:row-reverse;align-items:stretch;flex-wrap:nowrap;
  border-bottom:0.25mm solid #ece0c4;
  page-break-inside:avoid;break-inside:avoid}}
.row:last-child{{border-bottom:none}}

/* WORD CELL — unified unit, no dividers */
.cell{{display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:0.6mm 1mm}}
.tr{{font-size:{TR_PT}pt;font-style:italic;color:#a07830;text-align:center;
  line-height:1.1;width:100%;word-break:break-word;overflow-wrap:break-word}}
.ar{{font-family:'Amiri',serif;font-size:{AR_PT}pt;color:rgba(0,0,0,.18);
  direction:rtl;text-align:center;line-height:1.15;width:100%;
  white-space:nowrap;padding:0.2mm 0}}
.mn{{font-size:{MN_PT}pt;color:#1e1206;text-align:center;
  line-height:1.1;width:100%;word-break:break-word;overflow-wrap:break-word}}
.marker .ar.mk{{color:#c9a84c;font-size:18pt}}
"""



CSS_OPEN = """
/* OPENING PAGES (Juz / Surah) */
.open{flex:1 1 auto;display:flex;flex-direction:column;align-items:center;
  border:0.3mm solid #d4b870;overflow:hidden}
.open-juz{justify-content:flex-start;padding:14mm 16mm;background:#fdf7ed}
.o-eyebrow{font-size:11pt;font-weight:700;letter-spacing:8px;color:#8b6c14;
  text-transform:uppercase;margin-bottom:4mm}
.o-rule{font-size:13pt;color:#c9a84c;letter-spacing:10px;margin:3mm 0}
.o-bignum{font-family:'Amiri',serif;font-size:78pt;font-weight:700;color:#1a0e04;line-height:1}
.o-arlabel{font-family:'Amiri',serif;font-size:22pt;color:#8b6c14;direction:rtl;margin-top:3mm}
.o-intro{font-size:12pt;font-style:italic;color:#2a1a06;text-align:center;
  line-height:1.7;padding:0 6mm;margin-top:4mm}
.o-themewrap{width:100%;border-top:0.3mm solid #d4b870;margin-top:6mm;padding-top:4mm}
.o-themetitle{font-size:9pt;font-weight:700;letter-spacing:3px;color:#8b6c14;
  text-align:center;text-transform:uppercase;margin-bottom:2mm}
.o-themes{font-size:12pt;font-style:italic;color:#2a1a06;text-align:center;line-height:1.5}

.open-surah{justify-content:center;padding:16mm;
  background:linear-gradient(180deg,#fdf7ed,#faedc6 50%,#fdf7ed)}
.s-orn{font-size:16pt;color:#c9a84c;letter-spacing:12px;margin:4mm 0}
.s-ar{font-family:'Amiri',serif;font-size:40pt;font-weight:700;color:#1a0e04;
  direction:rtl;text-align:center;margin:2mm 0}
.s-en{font-size:20pt;font-weight:700;letter-spacing:6px;color:#8b6c14;
  text-transform:uppercase;margin:2mm 0}
.s-meta{font-size:11pt;color:#8b6c14;letter-spacing:1px;margin:2mm 0}
.s-rule{font-size:14pt;color:#c9a84c;letter-spacing:8px;margin:4mm 0}
.s-overview{font-size:12.5pt;font-style:italic;color:#2a1a06;text-align:center;
  line-height:1.7;padding:0 8mm;max-width:150mm}
.s-bism{font-family:'Amiri',serif;font-size:26pt;color:rgba(0,0,0,.18);
  direction:rtl;margin:5mm 0 3mm}

@media print{
  @page{size:A4;margin:0}
  body{background:#fdf7ed;padding:0;gap:0}
  .page{box-shadow:none;margin:0;page-break-after:always;break-after:page;overflow:visible}
  .page:last-of-type{page-break-after:auto;break-after:auto}
  .body,.words,.panel{overflow:visible}
  .row{page-break-inside:avoid;break-inside:avoid}
}
"""


# ─── FONT EMBED ──────────────────────────────────────────────────
def fonts_block():
    if not FONT_DIR.exists():
        return ''
    def b(n): return base64.b64encode((FONT_DIR/n).read_bytes()).decode()
    faces = [
        ('Amiri',400,'normal','Amiri-Regular.ttf'),
        ('Amiri',700,'normal','Amiri-Bold.ttf'),
        ('EB Garamond',400,'normal','EBGaramond-Regular.ttf'),
        ('EB Garamond',400,'italic','EBGaramond-Italic.ttf'),
        ('EB Garamond',600,'normal','EBGaramond-SemiBold.ttf'),
    ]
    out = '<style>'
    for fam,wt,st,fn in faces:
        out += (f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};"
                f"src:url('data:font/truetype;base64,{b(fn)}') format('truetype')}}")
    return out + '</style>'



# ─── SURAH METADATA ──────────────────────────────────────────────
SURAHS = {
    1: {'arabic':'\u0633\u064f\u0648\u0631\u064e\u0629\u064f \u0627\u0644\u0652\u0641\u064e\u0627\u062a\u0650\u062d\u064e\u0629',
        'english':'AL-FATIHA','meaning':'The Opening','no':1,'revealed':'Makkah','verses':7,
        'overview':'The opening chapter of the Qur\u2019an &mdash; a complete prayer recited '
                   'in every unit of salah. It praises Allah, affirms His mercy and sovereignty, '
                   'and asks Him for guidance to the straight path.'},
    2: {'arabic':'\u0633\u064f\u0648\u0631\u064e\u0629\u064f \u0627\u0644\u0652\u0628\u064e\u0642\u064e\u0631\u064e\u0629',
        'english':'AL-BAQARAH','meaning':'The Cow','no':2,'revealed':'Madinah','verses':286,
        'overview':'The longest chapter of the Qur\u2019an, revealed in Madinah. It establishes '
                   'core beliefs, practical guidance for the community, and lessons drawn from '
                   'earlier nations and prophets.'},
}
JUZ1_INTRO = ('Juz 1 opens with Surah Al-Fatiha &mdash; the daily prayer of every Muslim &mdash; '
              'and continues into the first portion of Surah Al-Baqarah, laying the foundation '
              'of faith, guidance, and the qualities of the believers.')
JUZ1_THEMES = 'Praise of Allah &middot; Guidance &middot; Faith &middot; Mercy &middot; Belief in the Unseen'


# ─── BUILD ───────────────────────────────────────────────────────
def build():
    pages = []
    pno = 0

    # Page 1 — Juz opener
    pno += 1
    pages.append(page_juz_opener(1, pno,
        '\u0627\u0644\u062c\u0632\u0621 \u0627\u0644\u0623\u0648\u0644',
        JUZ1_INTRO, JUZ1_THEMES))

    layouts = [
        (1, [f'1:{v}' for v in range(1, 8)]),
        (2, [f'2:{v}' for v in range(1, 142)]),
    ]
    for surah_no, vks in layouts:
        sd = SURAHS[surah_no]
        pno += 1
        pages.append(page_surah_opener(1, pno, sd))

        rows = pack_all_rows(vks)
        for page_rows in paginate_rows(rows):
            pno += 1
            pages.append(page_standard(1, pno, sd['english'], page_rows))

    css = build_css() + CSS_OPEN
    html = (f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>'
            f'<meta name="viewport" content="width=device-width,initial-scale=1.0"/>'
            f'<title>Traceable Quran &mdash; Juz 1</title>'
            f'{fonts_block()}<style>{css}</style></head><body>'
            f'{"".join(pages)}</body></html>')
    OUT.write_text(html, encoding='utf-8')
    size = OUT.stat().st_size
    print(f'Written {OUT.name}: {len(pages)} pages, {size/1024/1024:.1f} MB')
    return pages

if __name__ == '__main__':
    build()
