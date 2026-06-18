#!/usr/bin/env python3
"""
Phase 2 — Populate the locked workbook template with complete Juz 1.

Uses CSS and HTML structure from template.py exactly — nothing changes.
Only content is injected.

Output: Traceable-Quran-Juz1.html (offline, fonts embedded).
"""
import base64, re
from pathlib import Path

# Locked template (CSS + measurements + components — never modified)
from template import (
    CSS,
    header, footer,
    ROW_COUNT, WORDS_PER_ROW,
)
# Authentic Quran data (sourced from quran.com API)
from generate import WORDS, MEANINGS, ar

BASE     = Path(__file__).parent
FONT_DIR = BASE / 'fonts'
OUT      = BASE / 'Traceable-Quran-Juz1.html'

# ─── TEXT SHORTENERS ─────────────────────────────────────────────
PAREN_RX = re.compile(r'[\(\[][^\)\]]*[\)\]]')

def short_word_meaning(text: str, limit: int = 20) -> str:
    """Strip parentheticals only — no hard truncation."""
    text = PAREN_RX.sub('', text or '').replace('  ', ' ').strip(' ,;:.')
    return text

def short_translit(text: str, limit: int = 18) -> str:
    """Return full transliteration — no truncation."""
    return (text or '').strip()

# ─── ADAPTIVE WIDTH ───────────────────────────────────────────────
_DIAC = re.compile(
    r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]'
)

def flex_weight(arabic: str) -> int:
    """
    Proportional flex weight based on Arabic base-character count
    (diacritics stripped). Short words get less horizontal space;
    long words get more. Minimum weight = 2.
    """
    base = _DIAC.sub('', arabic or '')
    n = sum(1 for c in base if '\u0600' <= c <= '\u06FF')
    return max(2, n)
def clean_verse_meaning(text: str) -> str:
    """Light cleanup — keep simple; CSS clamps to 3 lines."""
    text = PAREN_RX.sub('', text or '').replace('  ', ' ').strip()
    return text



# ─── HTML EMITTERS — MIRROR template.py's STRUCTURE EXACTLY ──────

def emit_cell(arabic, translit, meaning, weight=3):
    return (
        f'<div class="cell" style="flex:{weight}">'
        f'<div class="tr">{translit}</div>'
        f'<div class="ar">{arabic}</div>'
        f'<div class="mn">{meaning}</div>'
        f'</div>'
    )

def emit_marker_cell(verse_num: int):
    glyph = f'&#1757;{ar(verse_num)}'
    return (
        f'<div class="cell" style="flex:2">'
        f'<div class="tr">&middot;</div>'
        f'<div class="ar" style="color:#c9a84c;font-size:18pt;">{glyph}</div>'
        f'<div class="mn">&middot;</div>'
        f'</div>'
    )

def emit_blank_cell():
    return (
        '<div class="cell">'
        '<div class="tr">&nbsp;</div>'
        '<div class="ar">&nbsp;</div>'
        '<div class="mn">&nbsp;</div>'
        '</div>'
    )

def emit_row(cells_html: str):
    return f'<div class="row">{cells_html}</div>'

def emit_blank_row():
    return f'<div class="row">{"".join(emit_blank_cell() for _ in range(WORDS_PER_ROW))}</div>'

def emit_slot(num: str, text: str):
    return (
        f'<div class="slot">'
        f'<div class="slot-num">{num}</div>'
        f'<div class="slot-text">{text}</div>'
        f'</div>'
    )

def emit_blank_slot():
    return '<div class="slot"><div class="slot-num">&nbsp;</div><div class="slot-text">&nbsp;</div></div>'



# ─── PACK PAGES — Auto-flow Juz 1 content into Standard pages ────

def build_items_for_surah(verse_keys):
    """Flat list of items: ('W', vkey, widx) for each word, ('M', vkey) marker."""
    items = []
    for vk in verse_keys:
        for i in range(len(WORDS[vk])):
            items.append(('W', vk, i))
        items.append(('M', vk, None))
    return items

def chunk_pages(items, rows_per_page=ROW_COUNT, words_per_row=WORDS_PER_ROW):
    """
    Split items into pages of (rows_per_page × words_per_row) cells.
    Returns list of pages — each page is a list of rows (each row = list of items).
    """
    cap = rows_per_page * words_per_row
    pages = []
    for p_start in range(0, len(items), cap):
        page_items = items[p_start:p_start + cap]
        rows = [
            page_items[r:r + words_per_row]
            for r in range(0, len(page_items), words_per_row)
        ]
        # Pad last row to full width with blanks
        if rows and len(rows[-1]) < words_per_row:
            rows[-1] = rows[-1] + [('B', None, None)] * (words_per_row - len(rows[-1]))
        # Pad page to exactly rows_per_page rows
        while len(rows) < rows_per_page:
            rows.append([('B', None, None)] * words_per_row)
        pages.append(rows)
    return pages

def render_row(row_items):
    cells = []
    for kind, vk, wi in row_items:
        if kind == 'W':
            ar_text, tr_text, en_text = WORDS[vk][wi]
            cells.append(emit_cell(
                ar_text,
                short_translit(tr_text),
                short_word_meaning(en_text),
                weight=flex_weight(ar_text),
            ))
        elif kind == 'M':
            verse_num = int(vk.split(':')[1])
            cells.append(emit_marker_cell(verse_num))
        else:
            cells.append(emit_blank_cell())
    return emit_row(''.join(cells))

def verses_on_page(rows):
    """Return ordered list of verse keys appearing on this page."""
    seen = []
    for row in rows:
        for kind, vk, _ in row:
            if vk and vk not in seen:
                seen.append(vk)
    return seen



# ─── PAGE RENDERERS (mirror template.py exactly) ─────────────────

def render_juz_opener_page(juz_no, page_no, intro_text, themes_text):
    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', 'JUZ OPENING', f'PAGE {page_no}')}
    <div class="body-a">
      <div class="a-eyebrow">PARA &middot; JUZ</div>
      <div class="a-divider-top">&middot; &middot; &middot;</div>
      <div class="a-number">{juz_no}</div>
      <div class="a-arabic-label">&#1575;&#1604;&#1601;&#1614;&#1575;&#1578;&#1616;&#1581;&#1614;&#1577; &mdash; &#1575;&#1604;&#1576;&#1614;&#1602;&#1614;&#1585;&#1614;&#1577;</div>
      <div class="a-divider-mid">&middot; &middot; &middot;</div>
      <div class="a-intro">{intro_text}</div>
      <div class="a-themes">
        <div class="a-themes-title">Key Themes</div>
        <div class="a-themes-text">{themes_text}</div>
      </div>
    </div>
    {footer('Juz 1 &mdash; Opening', page_no, juz_no)}
  </div>
</div>'''

def render_surah_opener_page(juz_no, page_no, sd):
    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', sd['english'].upper(), f'PAGE {page_no}')}
    <div class="body-b">
      <div class="b-orn-top">&#10022; &#10022; &#10022;</div>
      <div class="b-arabic">{sd['arabic']}</div>
      <div class="b-english">{sd['english']}</div>
      <div class="b-meta">
        Surah {sd['no']} &nbsp;&middot;&nbsp; {sd['meaning']} &nbsp;&middot;&nbsp;
        {sd['revealed']} &nbsp;&middot;&nbsp; {sd['verses']} Verses
      </div>
      <div class="b-divider">&middot; &middot; &middot;</div>
      <div class="b-overview">{sd['overview']}</div>
      <div class="b-bismillah">&#1576;&#1616;&#1587;&#1618;&#1605;&#1616; &#1649;&#1604;&#1604;&#1617;&#1614;&#1607;&#1616; &#1649;&#1604;&#1585;&#1617;&#1614;&#1581;&#1618;&#1605;&#1614;&#1648;&#1606;&#1616; &#1649;&#1604;&#1585;&#1617;&#1614;&#1581;&#1616;&#1610;&#1605;&#1616;</div>
      <div class="b-orn-bot">&#10022; &#10022; &#10022;</div>
    </div>
    {footer(sd['english'] + ' &mdash; Opening', page_no, juz_no)}
  </div>
</div>'''

def render_standard_page(juz_no, page_no, surah_label, rows, slots):
    rows_html = ''.join(render_row(r) for r in rows)
    # Pad slots to ROW_COUNT
    slot_items = list(slots) + [None] * (ROW_COUNT - len(slots))
    slots_html = ''.join(
        emit_slot(s[0], s[1]) if s else emit_blank_slot()
        for s in slot_items[:ROW_COUNT]
    )
    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', surah_label, f'PAGE {page_no}')}
    <div class="body-c">
      <div class="panel">{slots_html}</div>
      <div class="grid">{rows_html}</div>
    </div>
    {footer(surah_label, page_no, juz_no)}
  </div>
</div>'''



# ─── SURAH METADATA ──────────────────────────────────────────────
SURAHS = {
    1: {
        'arabic': '\u0633\u064f\u0648\u0631\u064e\u0629\u064f \u0627\u0644\u0652\u0641\u064e\u0627\u062a\u0650\u062d\u064e\u0629\u0650',
        'english': 'AL-FATIHA',
        'meaning': 'The Opening',
        'no': 1,
        'revealed': 'Makkah',
        'verses': 7,
        'overview': (
            'The opening chapter of the Qur\u2019an &mdash; a short, complete '
            'prayer recited in every unit of formal prayer. It praises Allah, '
            'affirms His mercy and sovereignty, and asks Him for guidance to '
            'the straight path.'
        ),
    },
    2: {
        'arabic': '\u0633\u064f\u0648\u0631\u064e\u0629\u064f \u0627\u0644\u0652\u0628\u064e\u0642\u064e\u0631\u064e\u0629',
        'english': 'AL-BAQARAH',
        'meaning': 'The Cow',
        'no': 2,
        'revealed': 'Madinah',
        'verses': 286,
        'overview': (
            'The longest chapter of the Qur\u2019an, revealed in Madinah. '
            'It establishes core beliefs, lays down practical guidance for the '
            'community, recounts the story of Banu Israil and Prophet Ibrahim, '
            'and outlines laws of worship and dealings.'
        ),
    },
}

JUZ_INTRO = (
    'Juz 1 begins with Surah Al-Fatiha &mdash; the daily opening prayer of '
    'every Muslim &mdash; and continues with the first 141 verses of Surah '
    'Al-Baqarah. These pages set the foundation: the praise of Allah, His '
    'guidance, the qualities of the believers, and the early lessons drawn '
    'from earlier nations.'
)
JUZ_THEMES = (
    'Praise of Allah &middot; Guidance &middot; Faith &middot; '
    'Mercy &middot; Belief in the Unseen &middot; Stories of past nations'
)



# ─── BUILD ───────────────────────────────────────────────────────

def build():
    pages_html = []
    page_no = 0

    # Page 1 — Juz 1 opener
    page_no += 1
    pages_html.append(render_juz_opener_page(1, page_no, JUZ_INTRO, JUZ_THEMES))

    # Surahs in Juz 1: Al-Fatiha (1:1-1:7) and Al-Baqarah (2:1-2:141)
    surah_layouts = [
        (1, [f'1:{v}' for v in range(1, 8)]),
        (2, [f'2:{v}' for v in range(1, 142)]),
    ]

    for surah_no, verse_keys in surah_layouts:
        sd = SURAHS[surah_no]
        # Surah opener
        page_no += 1
        pages_html.append(render_surah_opener_page(1, page_no, sd))

        # Standard pages (auto-pack)
        items = build_items_for_surah(verse_keys)
        std_pages = chunk_pages(items)

        for rows in std_pages:
            page_no += 1
            # Build meaning slots from verses present on this page
            vks = verses_on_page(rows)
            slots = [
                (f'[ {ar(int(vk.split(":")[1]))} ]', clean_verse_meaning(MEANINGS[vk]))
                for vk in vks if vk in MEANINGS
            ]
            pages_html.append(render_standard_page(
                juz_no=1,
                page_no=page_no,
                surah_label=sd['english'],
                rows=rows,
                slots=slots,
            ))

    return pages_html, page_no



# ─── HTML SHELL & FONT EMBEDDING ─────────────────────────────────

def embed_fonts_css() -> str:
    def b64(name):
        return base64.b64encode((FONT_DIR / name).read_bytes()).decode()
    return (
        f"<style>"
        f"@font-face{{font-family:'Amiri';font-weight:400;"
        f"src:url('data:font/truetype;base64,{b64('Amiri-Regular.ttf')}') format('truetype')}}"
        f"@font-face{{font-family:'Amiri';font-weight:700;"
        f"src:url('data:font/truetype;base64,{b64('Amiri-Bold.ttf')}') format('truetype')}}"
        f"@font-face{{font-family:'EB Garamond';font-weight:400;font-style:normal;"
        f"src:url('data:font/truetype;base64,{b64('EBGaramond-Regular.ttf')}') format('truetype')}}"
        f"@font-face{{font-family:'EB Garamond';font-weight:400;font-style:italic;"
        f"src:url('data:font/truetype;base64,{b64('EBGaramond-Italic.ttf')}') format('truetype')}}"
        f"@font-face{{font-family:'EB Garamond';font-weight:600;"
        f"src:url('data:font/truetype;base64,{b64('EBGaramond-SemiBold.ttf')}') format('truetype')}}"
        f"</style>"
    )

def write_html(pages_html, total_pages):
    body = '\n\n'.join(pages_html)
    fonts = embed_fonts_css() if FONT_DIR.exists() else ''
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Traceable Quran &mdash; Juz 1 (Para 1)</title>
  {fonts}
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>'''
    OUT.write_text(html, encoding='utf-8')
    size = OUT.stat().st_size
    print(f'Written: {OUT.name}  ({size:,} bytes / {size/1024/1024:.1f} MB)')
    print(f'Total pages: {total_pages}')

if __name__ == '__main__':
    pages, n = build()
    write_html(pages, n)
