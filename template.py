#!/usr/bin/env python3
"""
Traceable Quran — STRUCTURAL TEMPLATE (Phase 1)

Generates an A4 workbook template with:
  * Fixed Mushaf border
  * Fixed header band
  * Fixed footer band
  * Fixed left meaning column
  * Fixed right tracing area
  * Exactly 12 fixed-height rows
  * 10 fixed-width word cells per row
  * Placeholder content only — no Quran text

Every page is structurally identical. No flex-grow, no auto-sizing.
Output: template.html (3 sample pages, all identical structure).
"""
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────
# FIXED LAYOUT MEASUREMENTS — A4 in millimetres
# ─────────────────────────────────────────────────────────────────────
PAGE_W_MM       = 210
PAGE_H_MM       = 297
PAGE_PAD_MM     = 10        # uniform inner padding from physical edge

# Frame
FRAME_GAP_MM    = 1.5       # cream gap inside the gold border
FRAME_WIDTH_MM  = 0.5       # gold frame stroke width

# Bands
HEADER_MM       = 14        # JUZ ❖ SURAH ❖ PAGE bar
SURAH_BAND_MM   = 16        # surah Arabic name + meta line
BISMILLAH_MM    = 18        # bismillah row (only on surah-start pages)
FOOTER_MM       = 10

# Row grid
ROWS_PER_PAGE   = 12
WORDS_PER_ROW   = 10

# Left meaning column
LEFT_COL_PCT    = 22        # % of body width

# Computed: usable body height
BODY_W_MM       = PAGE_W_MM - 2 * PAGE_PAD_MM
BODY_H_MM       = PAGE_H_MM - 2 * PAGE_PAD_MM - HEADER_MM - FOOTER_MM
ROW_H_MM        = BODY_H_MM / ROWS_PER_PAGE        # ~17.4 mm per row

# Within a word cell (vertical breakdown)
TR_PT           = 11        # transliteration font
AR_PT           = 27        # Arabic font (preserved at 27px)
MN_PT           = 11        # meaning font

# Colours (Mushaf palette — kept identical to live design)
INK_DARK        = '#1a0e04'
INK_BODY        = '#2a1a06'
GOLD            = '#c9a84c'
GOLD_DEEP       = '#8b6c14'
GOLD_LIGHT      = '#e8d49a'
PARCHMENT       = '#fdf7ed'
PARCHMENT_DEEP  = '#f6ead6'
AMBER           = '#a07830'
HAIRLINE        = '#e4d0a8'
ROW_BORDER      = '#d4b870'
GRAY_TRACE      = 'rgba(0,0,0,0.13)'   # placeholder Arabic shadow tone
PLACEHOLDER_BG  = '#f8f1dc'             # tinted box to make placeholders visible
PLACEHOLDER_TX  = '#bfa770'             # placeholder label colour



# ─────────────────────────────────────────────────────────────────────
# CSS — fixed measurements only
# ─────────────────────────────────────────────────────────────────────
CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body {{
  background: #9e8f72;
  font-family: 'EB Garamond', 'Georgia', serif;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}

body {{
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 0;
  gap: 30px;
}}

/* ─── PAGE — fixed A4, no scaling, no flex stretching ─── */
.page {{
  position: relative;
  background: {PARCHMENT};
  width: {PAGE_W_MM}mm;
  height: {PAGE_H_MM}mm;        /* fixed — never grows */
  padding: {PAGE_PAD_MM}mm;
  border: {FRAME_WIDTH_MM}mm solid {GOLD};
  box-shadow:
    0 0 0 {FRAME_GAP_MM}mm {PARCHMENT},
    0 0 0 {FRAME_GAP_MM + FRAME_WIDTH_MM}mm {GOLD},
    0 12px 50px rgba(0,0,0,.30);
  overflow: hidden;             /* never let content escape the frame */
}}

/* Inner hairline frame (decorative) */
.page::before {{
  content: '';
  position: absolute;
  top: 4mm; right: 4mm; bottom: 4mm; left: 4mm;
  border: 0.3mm solid rgba(201,168,76,.4);
  pointer-events: none;
}}

/* ─── PAGE LAYOUT — vertical stack of fixed-height bands ─── */
.page-inner {{
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}}

/* Header band — fixed height */
.header {{
  flex: 0 0 {HEADER_MM}mm;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8f0dc;
  border-top:    0.6mm solid {GOLD_DEEP};
  border-bottom: 0.6mm solid {GOLD_DEEP};
  box-shadow:
    inset 0 0.6mm 0 {GOLD_LIGHT},
    inset 0 -0.6mm 0 {GOLD_LIGHT};
  padding: 0 4mm;
}}
.header-juz, .header-page {{
  font-size: 9pt;
  font-weight: 700;
  color: {GOLD_DEEP};
  letter-spacing: 1.2px;
  text-transform: uppercase;
  width: 22mm;
}}
.header-page {{ text-align: right; }}
.header-mid {{
  display: flex;
  align-items: center;
  gap: 3mm;
}}
.header-orn {{ font-size: 11pt; color: {GOLD}; line-height: 1; }}
.header-name {{
  font-size: 12pt;
  font-weight: 700;
  letter-spacing: 2.4px;
  color: {INK_DARK};
  text-transform: uppercase;
}}

/* Body — split into left meaning column and right grid */
.body {{
  flex: 1 1 {BODY_H_MM}mm;
  height: {BODY_H_MM}mm;
  display: flex;
  flex-direction: row;
  border: 0.3mm solid {ROW_BORDER};
}}

/* Left column — fixed width, full body height */
.meanings {{
  flex: 0 0 {LEFT_COL_PCT}%;
  width: {LEFT_COL_PCT}%;
  height: 100%;
  background: {PARCHMENT_DEEP};
  border-right: 0.4mm solid {ROW_BORDER};
  padding: 2mm;
  display: flex;
  flex-direction: column;
  gap: 1.5mm;
  overflow: hidden;
}}

.meaning-item {{
  display: flex;
  flex-direction: column;
  gap: 1mm;
  padding: 1.5mm;
  background: {PLACEHOLDER_BG};
  border: 0.2mm dashed {PLACEHOLDER_TX};
  border-radius: 1mm;
}}
.meaning-num {{
  font-size: 9pt;
  font-weight: 700;
  color: {GOLD_DEEP};
  font-family: 'Amiri', serif;
}}
.meaning-text {{
  font-size: 8pt;
  color: {PLACEHOLDER_TX};
  font-style: italic;
  letter-spacing: 0.3px;
}}

/* Right area — exactly 12 rows of fixed height */
.grid {{
  flex: 1 1 auto;
  height: 100%;
  display: grid;
  grid-template-rows: repeat({ROWS_PER_PAGE}, {ROW_H_MM}mm);
  grid-auto-rows: 0;            /* never create extra rows */
  background: {PARCHMENT};
  overflow: hidden;
}}

/* Row — fixed height, never stretches or shrinks */
.row {{
  height: {ROW_H_MM}mm;
  border-bottom: 0.2mm solid {HAIRLINE};
  display: grid;
  grid-template-columns: repeat({WORDS_PER_ROW}, 1fr);
  /* RTL flow — first cell appears on the right */
  direction: rtl;
}}
.row:last-child {{ border-bottom: none; }}

/* Word cell — fixed structure: translit / arabic / meaning */
.cell {{
  height: {ROW_H_MM}mm;
  border-left: 0.2mm dotted #efe2c2;
  display: grid;
  grid-template-rows: 1fr auto 2fr auto 1fr;  /* tr / divider / ar / divider / mn */
  align-items: stretch;
  direction: ltr;             /* reset for inner labels */
}}
.cell:last-child {{ border-left: none; }}

/* Cell sub-areas */
.cell-tr {{
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: {TR_PT}pt;
  font-style: italic;
  color: {PLACEHOLDER_TX};
  background: {PLACEHOLDER_BG};
}}

.cell-div {{
  height: 0.2mm;
  background: {HAIRLINE};
}}

.cell-ar {{
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Amiri', serif;
  font-size: {AR_PT}pt;
  color: {GRAY_TRACE};
  direction: rtl;
}}

.cell-mn {{
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: {MN_PT}pt;
  color: {PLACEHOLDER_TX};
  background: {PLACEHOLDER_BG};
}}

/* Footer band — fixed height */
.footer {{
  flex: 0 0 {FOOTER_MM}mm;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 0.6mm solid {GOLD_DEEP};
  padding: 0 4mm;
  font-size: 9pt;
  font-weight: 600;
  color: {GOLD_DEEP};
  letter-spacing: 0.4px;
}}

/* ─── PRINT ─── */
@media print {{
  @page {{ size: A4; margin: 0; }}
  body  {{ background: {PARCHMENT}; padding: 0; gap: 0; }}
  .page {{
    box-shadow: none;
    margin: 0;
    page-break-after: always;
    break-after: page;
  }}
  .page:last-of-type {{ page-break-after: auto; break-after: auto; }}
  .row {{ page-break-inside: avoid; break-inside: avoid; }}
}}
"""



# ─────────────────────────────────────────────────────────────────────
# HTML — placeholder content only (Phase 1)
# ─────────────────────────────────────────────────────────────────────

def render_meaning_placeholder(n: int) -> str:
    return (
        f'<div class="meaning-item">'
        f'<span class="meaning-num">[ {n} ]</span>'
        f'<span class="meaning-text">[ verse meaning placeholder ]</span>'
        f'</div>'
    )

def render_cell_placeholder(idx: int) -> str:
    return (
        f'<div class="cell" data-cell="{idx}">'
        f'<div class="cell-tr">tr-{idx}</div>'
        f'<div class="cell-div"></div>'
        f'<div class="cell-ar">ع</div>'   # generic placeholder Arabic glyph
        f'<div class="cell-div"></div>'
        f'<div class="cell-mn">m-{idx}</div>'
        f'</div>'
    )

def render_row_placeholder(row_idx: int) -> str:
    cells = ''.join(render_cell_placeholder(i + 1) for i in range(WORDS_PER_ROW))
    return f'<div class="row" data-row="{row_idx}">{cells}</div>'

def render_page(page_no: int) -> str:
    juz_label  = f'JUZ 1'
    name_label = '[ SURAH PLACEHOLDER ]'
    page_label = f'PAGE {page_no}'

    rows = ''.join(
        render_row_placeholder(r + 1)
        for r in range(ROWS_PER_PAGE)
    )

    meanings = ''.join(
        render_meaning_placeholder(i + 1)
        for i in range(6)   # 6 placeholder meaning items
    )

    return f'''<div class="page">
  <div class="page-inner">
    <div class="header">
      <span class="header-juz">{juz_label}</span>
      <div class="header-mid">
        <span class="header-orn">&#10022;</span>
        <span class="header-name">{name_label}</span>
        <span class="header-orn">&#10022;</span>
      </div>
      <span class="header-page">{page_label}</span>
    </div>
    <div class="body">
      <div class="meanings">
        {meanings}
      </div>
      <div class="grid">
        {rows}
      </div>
    </div>
    <div class="footer">
      <span>[ Surah Placeholder ]</span>
      <span>Page {page_no} &nbsp;|&nbsp; Juz 1</span>
    </div>
  </div>
</div>'''


def build_html(num_pages: int = 3) -> str:
    pages = '\n\n'.join(render_page(i + 1) for i in range(num_pages))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Traceable Quran &#8212; Structural Template</title>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet"/>
  <style>{CSS}</style>
</head>
<body>
{pages}
</body>
</html>'''


if __name__ == '__main__':
    out = Path(__file__).parent / 'template.html'
    out.write_text(build_html(num_pages=3), encoding='utf-8')
    print(f'Written: {out.name}')
    print(f'  Page size:        {PAGE_W_MM}mm x {PAGE_H_MM}mm  (A4)')
    print(f'  Body height:      {BODY_H_MM:.1f}mm')
    print(f'  Rows per page:    {ROWS_PER_PAGE}  (each {ROW_H_MM:.2f}mm tall)')
    print(f'  Cells per row:    {WORDS_PER_ROW}')
    print(f'  Total placeholder cells per page: {ROWS_PER_PAGE * WORDS_PER_ROW}')
