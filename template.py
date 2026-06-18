#!/usr/bin/env python3
"""
Traceable Quran — STRUCTURAL TEMPLATE v2

THREE INDEPENDENT PAGE TEMPLATES:
  A) Juz Opening Page    — decorative, no tracing rows
  B) Surah Opening Page  — surah card + 6 tracing rows
  C) Standard Workbook   — 12 tracing rows + tracker strip

Every page is structurally identical for its type.
All measurements are FIXED — content adapts to template.
Phase 1: placeholders only — no Quran content.
"""
from pathlib import Path

# ─── PAGE GEOMETRY ───────────────────────────────────────────────
PAGE_W_MM       = 210
PAGE_H_MM       = 297
PAGE_PAD_MM     = 10

# Frame
FRAME_GAP_MM    = 1.5
FRAME_W_MM      = 0.5

# Bands (identical on all 3 templates)
HEADER_MM       = 14
FOOTER_MM       = 10
TRACKER_MM      = 13

# Body heights derived
BODY_W_MM       = PAGE_W_MM - 2 * PAGE_PAD_MM        # 190
BODY_H_MM       = PAGE_H_MM - 2 * PAGE_PAD_MM - HEADER_MM - FOOTER_MM  # 253

# Standard page row grid
STANDARD_ROWS         = 12
STANDARD_ROW_AREA_MM  = BODY_H_MM - TRACKER_MM       # 240
STANDARD_ROW_H_MM     = STANDARD_ROW_AREA_MM / STANDARD_ROWS   # 20.0

# Surah opener: top card + 6 rows + tracker
SURAH_CARD_MM         = 90
SURAH_ROWS            = 6
SURAH_ROW_AREA_MM     = BODY_H_MM - SURAH_CARD_MM - TRACKER_MM  # 150
SURAH_ROW_H_MM        = SURAH_ROW_AREA_MM / SURAH_ROWS          # 25.0

# Words per row (same on B & C)
WORDS_PER_ROW   = 10

# Left meaning panel
LEFT_COL_PCT    = 30



# ─── PALETTE ─────────────────────────────────────────────────────
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
GRAY_TRACE      = 'rgba(0,0,0,0.13)'
PLACEHOLDER_BG  = '#f8f1dc'
PLACEHOLDER_TX  = '#bfa770'

# ─── TYPOGRAPHY ──────────────────────────────────────────────────
TR_PT           = 11   # transliteration  (priority 3)
AR_PT           = 27   # Arabic           (priority 1 — preserved)
MN_PT_CELL      = 11   # word meaning inside cell
MEANING_PT      = 13   # left-panel verse meaning   (priority 2 — +60% from old 8pt)



# ─── CSS — SHARED BASE ───────────────────────────────────────────
CSS_BASE = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  background: #9e8f72;
  font-family: 'EB Garamond', 'Georgia', serif;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}
body {{
  display: flex; flex-direction: column; align-items: center;
  padding: 30px 0; gap: 30px;
}}

/* PAGE — fixed A4, never grows */
.page {{
  position: relative;
  background: {PARCHMENT};
  width: {PAGE_W_MM}mm;
  height: {PAGE_H_MM}mm;
  padding: {PAGE_PAD_MM}mm;
  border: {FRAME_W_MM}mm solid {GOLD};
  box-shadow:
    0 0 0 {FRAME_GAP_MM}mm {PARCHMENT},
    0 0 0 {FRAME_GAP_MM + FRAME_W_MM}mm {GOLD},
    0 12px 50px rgba(0,0,0,.30);
  overflow: hidden;
}}
.page::before {{
  content: '';
  position: absolute;
  top: 4mm; right: 4mm; bottom: 4mm; left: 4mm;
  border: 0.3mm solid rgba(201,168,76,.4);
  pointer-events: none;
}}

.page-inner {{
  position: relative;
  width: 100%; height: 100%;
  display: flex; flex-direction: column;
}}

/* HEADER (identical for A, B, C) */
.header {{
  flex: 0 0 {HEADER_MM}mm;
  display: flex; align-items: center; justify-content: space-between;
  background: #f8f0dc;
  border-top:    0.6mm solid {GOLD_DEEP};
  border-bottom: 0.6mm solid {GOLD_DEEP};
  box-shadow: inset 0 0.6mm 0 {GOLD_LIGHT}, inset 0 -0.6mm 0 {GOLD_LIGHT};
  padding: 0 4mm;
}}
.header-juz, .header-page {{
  font-size: 9pt; font-weight: 700; color: {GOLD_DEEP};
  letter-spacing: 1.2px; text-transform: uppercase; width: 22mm;
}}
.header-page {{ text-align: right; }}
.header-mid {{ display: flex; align-items: center; gap: 3mm; }}
.header-orn {{ font-size: 11pt; color: {GOLD}; line-height: 1; }}
.header-name {{
  font-size: 12pt; font-weight: 700; letter-spacing: 2.4px;
  color: {INK_DARK}; text-transform: uppercase;
}}

/* FOOTER (identical for A, B, C) */
.footer {{
  flex: 0 0 {FOOTER_MM}mm;
  display: flex; align-items: center; justify-content: space-between;
  border-top: 0.6mm solid {GOLD_DEEP};
  padding: 0 4mm;
  font-size: 9pt; font-weight: 600; color: {GOLD_DEEP}; letter-spacing: 0.4px;
}}
"""



# ─── CSS — STANDARD WORKBOOK (Template C) ────────────────────────
CSS_STANDARD = f"""
.body-standard {{
  flex: 0 0 {BODY_H_MM}mm; height: {BODY_H_MM}mm;
  display: flex; flex-direction: row;
  border: 0.3mm solid {ROW_BORDER};
}}

.meaning-panel {{
  flex: 0 0 {LEFT_COL_PCT}%; width: {LEFT_COL_PCT}%;
  background: {PARCHMENT_DEEP};
  border-right: 0.4mm solid {ROW_BORDER};
  padding: 3mm; gap: 2mm;
  display: flex; flex-direction: column;
  overflow: hidden;
}}
.meaning-panel-title {{
  font-size: 8pt; font-weight: 700; letter-spacing: 1.5px;
  color: {GOLD_DEEP}; text-transform: uppercase;
  padding-bottom: 1.5mm;
  border-bottom: 0.3mm dashed {ROW_BORDER};
}}
.meaning-item {{
  display: flex; flex-direction: column; gap: 1mm;
  padding: 1.5mm 1mm;
  border: 0.2mm dashed {PLACEHOLDER_TX};
  background: {PLACEHOLDER_BG};
  border-radius: 1mm;
}}
.meaning-num {{
  font-family: 'Amiri', serif;
  font-size: 10pt; font-weight: 700;
  color: {GOLD_DEEP};
}}
.meaning-text {{
  font-size: {MEANING_PT}pt;
  font-style: italic;
  color: {PLACEHOLDER_TX};
  line-height: 1.45;
  letter-spacing: 0.2px;
}}

.grid {{
  flex: 1 1 auto; height: 100%;
  display: flex; flex-direction: column;
  background: {PARCHMENT};
}}
.grid-rows {{
  flex: 0 0 {STANDARD_ROW_AREA_MM}mm;
  height: {STANDARD_ROW_AREA_MM}mm;
  display: grid;
  grid-template-rows: repeat({STANDARD_ROWS}, {STANDARD_ROW_H_MM}mm);
  grid-auto-rows: 0;
}}

.row {{
  height: {STANDARD_ROW_H_MM}mm;
  border-bottom: 0.2mm solid {HAIRLINE};
  display: grid;
  grid-template-columns: repeat({WORDS_PER_ROW}, 1fr);
  direction: rtl;
}}
.row:last-child {{ border-bottom: none; }}

.cell {{
  height: {STANDARD_ROW_H_MM}mm;
  border-left: 0.2mm dotted #efe2c2;
  display: grid;
  grid-template-rows: 1fr auto 2fr auto 1fr;
  align-items: stretch;
  direction: ltr;
}}
.cell:last-child {{ border-left: none; }}

.cell-tr {{ display:flex; align-items:center; justify-content:center;
  font-size:{TR_PT}pt; font-style:italic; color:{PLACEHOLDER_TX};
  background:{PLACEHOLDER_BG}; }}
.cell-div {{ height: 0.2mm; background: {HAIRLINE}; }}
.cell-ar {{ display:flex; align-items:center; justify-content:center;
  font-family:'Amiri',serif; font-size:{AR_PT}pt; color:{GRAY_TRACE}; direction:rtl; }}
.cell-mn {{ display:flex; align-items:center; justify-content:center;
  font-size:{MN_PT_CELL}pt; color:{PLACEHOLDER_TX}; background:{PLACEHOLDER_BG}; }}

/* TRACKER STRIP (subtle bottom band on Standard & Surah pages) */
.tracker {{
  flex: 0 0 {TRACKER_MM}mm; height: {TRACKER_MM}mm;
  display: flex; align-items: center; gap: 4mm;
  padding: 0 4mm;
  background: {PARCHMENT_DEEP};
  border-top: 0.3mm solid {ROW_BORDER};
  font-size: 8pt; color: {GOLD_DEEP};
}}
.tracker-check {{ display:flex; align-items:center; gap: 1.5mm; }}
.tracker-box {{
  display: inline-block;
  width: 3.5mm; height: 3.5mm;
  border: 0.3mm solid {GOLD_DEEP};
  background: {PARCHMENT};
  border-radius: 0.5mm;
}}
.tracker-line {{
  flex: 1 1 auto;
  border-bottom: 0.2mm solid {ROW_BORDER};
  height: 0;
  margin-bottom: 0.5mm;
}}
.tracker-label {{ font-weight: 600; letter-spacing: 0.3px; }}
"""



# ─── CSS — SURAH OPENER (Template B) ─────────────────────────────
CSS_SURAH = f"""
.body-surah {{
  flex: 0 0 {BODY_H_MM}mm; height: {BODY_H_MM}mm;
  display: flex; flex-direction: column;
}}

.surah-card {{
  flex: 0 0 {SURAH_CARD_MM}mm;
  height: {SURAH_CARD_MM}mm;
  position: relative;
  background: linear-gradient(135deg,#f4e8c4 0%,#ede0aa 50%,#f4e8c4 100%);
  border: 0.4mm solid {GOLD};
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 6mm 12mm;
  gap: 3mm;
}}
.surah-card::before, .surah-card::after {{
  content: '\\2756';
  position: absolute; top: 50%; transform: translateY(-50%);
  color: {GOLD}; font-size: 16pt;
}}
.surah-card::before {{ left: 4mm; }}
.surah-card::after  {{ right: 4mm; }}

.surah-arabic {{
  font-family: 'Amiri', serif;
  font-size: 32pt; font-weight: 700;
  color: {INK_DARK};
  direction: rtl; letter-spacing: 1px;
}}
.surah-english {{
  font-size: 14pt; font-weight: 700;
  letter-spacing: 4px; text-transform: uppercase;
  color: {GOLD_DEEP};
}}
.surah-meta {{
  font-size: 10pt; color: {GOLD_DEEP};
  letter-spacing: 0.6px;
}}
.surah-overview {{
  font-size: 10pt; font-style: italic;
  color: {INK_BODY};
  text-align: center; line-height: 1.5;
  max-width: 140mm;
  margin-top: 1mm;
}}
.surah-bismillah {{
  font-family: 'Amiri', serif;
  font-size: 18pt;
  color: rgba(0,0,0,0.18);
  direction: rtl;
  margin-top: 1mm;
}}

/* Surah-opener uses 6 rows × 25mm */
.body-surah .grid-rows {{
  flex: 0 0 {SURAH_ROW_AREA_MM}mm;
  height: {SURAH_ROW_AREA_MM}mm;
  grid-template-rows: repeat({SURAH_ROWS}, {SURAH_ROW_H_MM}mm);
}}
.body-surah .row, .body-surah .cell {{ height: {SURAH_ROW_H_MM}mm; }}
"""



# ─── CSS — JUZ OPENER (Template A) ───────────────────────────────
CSS_JUZ = f"""
.body-juz {{
  flex: 0 0 {BODY_H_MM}mm; height: {BODY_H_MM}mm;
  display: flex; flex-direction: column;
  padding: 6mm 6mm;
  gap: 5mm;
  background: {PARCHMENT};
}}

.juz-title-block {{
  flex: 0 0 70mm; height: 70mm;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  border: 0.5mm double {GOLD};
  background: linear-gradient(180deg, #f4e8c4 0%, #fdf7ed 100%);
  position: relative;
}}
.juz-corner {{
  position: absolute;
  width: 8mm; height: 8mm;
  border-color: {GOLD};
  border-style: solid;
}}
.juz-corner.tl {{ top: 1mm; left: 1mm; border-width: 0.4mm 0 0 0.4mm; }}
.juz-corner.tr {{ top: 1mm; right: 1mm; border-width: 0.4mm 0.4mm 0 0; }}
.juz-corner.bl {{ bottom: 1mm; left: 1mm; border-width: 0 0 0.4mm 0.4mm; }}
.juz-corner.br {{ bottom: 1mm; right: 1mm; border-width: 0 0.4mm 0.4mm 0; }}

.juz-eyebrow {{
  font-size: 10pt; font-weight: 700;
  letter-spacing: 5px; text-transform: uppercase;
  color: {GOLD_DEEP};
  margin-bottom: 4mm;
}}
.juz-number {{
  font-family: 'Amiri', serif;
  font-size: 60pt; font-weight: 700;
  color: {INK_DARK};
  line-height: 1;
}}
.juz-arabic-label {{
  font-family: 'Amiri', serif;
  font-size: 18pt;
  color: {GOLD_DEEP};
  margin-top: 3mm;
}}

.juz-meta-row {{
  flex: 0 0 50mm; height: 50mm;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5mm;
}}
.juz-card {{
  border: 0.3mm solid {GOLD};
  background: {PARCHMENT_DEEP};
  padding: 4mm;
  display: flex; flex-direction: column; gap: 2mm;
}}
.juz-card-title {{
  font-size: 9pt; font-weight: 700;
  letter-spacing: 2px; text-transform: uppercase;
  color: {GOLD_DEEP};
  border-bottom: 0.3mm solid {GOLD};
  padding-bottom: 1.5mm;
}}
.juz-card-body {{
  font-size: 11pt; color: {PLACEHOLDER_TX}; font-style: italic;
  line-height: 1.5;
}}

.juz-intro {{
  flex: 1 1 auto;
  border: 0.3mm solid {GOLD};
  background: {PARCHMENT_DEEP};
  padding: 5mm 7mm;
  display: flex; flex-direction: column; gap: 2mm;
}}
.juz-intro-title {{
  font-size: 10pt; font-weight: 700;
  letter-spacing: 2.5px; text-transform: uppercase;
  color: {GOLD_DEEP};
  text-align: center;
  padding-bottom: 2mm;
  border-bottom: 0.3mm dashed {ROW_BORDER};
}}
.juz-intro-body {{
  font-size: 11pt; line-height: 1.65;
  color: {PLACEHOLDER_TX}; font-style: italic;
  text-align: justify;
}}

.juz-flourish {{
  text-align: center;
  font-size: 22pt; color: {GOLD};
  letter-spacing: 8px;
  margin-top: 1mm;
}}
"""

# ─── PRINT CSS ───────────────────────────────────────────────────
CSS_PRINT = """
@media print {
  @page { size: A4; margin: 0; }
  body  { background: #fdf7ed; padding: 0; gap: 0; }
  .page { box-shadow: none; margin: 0; page-break-after: always; break-after: page; }
  .page:last-of-type { page-break-after: auto; break-after: auto; }
  .row { page-break-inside: avoid; break-inside: avoid; }
}
"""

CSS = CSS_BASE + CSS_STANDARD + CSS_SURAH + CSS_JUZ + CSS_PRINT



# ─── COMPONENTS ──────────────────────────────────────────────────

def header(juz_label, mid_label, page_label):
    return (
        f'<div class="header">'
        f'<span class="header-juz">{juz_label}</span>'
        f'<div class="header-mid">'
        f'<span class="header-orn">&#10022;</span>'
        f'<span class="header-name">{mid_label}</span>'
        f'<span class="header-orn">&#10022;</span>'
        f'</div>'
        f'<span class="header-page">{page_label}</span>'
        f'</div>'
    )

def footer(left_label, page_no, juz_no=1):
    return (
        f'<div class="footer">'
        f'<span>{left_label}</span>'
        f'<span>Page {page_no} &nbsp;|&nbsp; Juz {juz_no}</span>'
        f'</div>'
    )

def tracker_strip():
    return (
        '<div class="tracker">'
        '<div class="tracker-check">'
        '<span class="tracker-box"></span>'
        '<span class="tracker-label">Completed</span></div>'
        '<div class="tracker-check">'
        '<span class="tracker-box"></span>'
        '<span class="tracker-label">Reviewed</span></div>'
        '<div class="tracker-check">'
        '<span class="tracker-box"></span>'
        '<span class="tracker-label">Memorized</span></div>'
        '<span class="tracker-label">&nbsp;Date</span>'
        '<div class="tracker-line"></div>'
        '<span class="tracker-label">Notes</span>'
        '<div class="tracker-line"></div>'
        '</div>'
    )

def cell_placeholder(idx):
    return (
        f'<div class="cell" data-cell="{idx}">'
        f'<div class="cell-tr">tr-{idx}</div>'
        f'<div class="cell-div"></div>'
        f'<div class="cell-ar">&#1593;</div>'
        f'<div class="cell-div"></div>'
        f'<div class="cell-mn">m-{idx}</div>'
        f'</div>'
    )

def row_placeholder(row_idx):
    cells = ''.join(cell_placeholder(i + 1) for i in range(WORDS_PER_ROW))
    return f'<div class="row" data-row="{row_idx}">{cells}</div>'

def meaning_item(n, text='[ verse meaning placeholder — comfortable readable text for older learners ]'):
    return (
        f'<div class="meaning-item">'
        f'<span class="meaning-num">[ {n} ]</span>'
        f'<span class="meaning-text">{text}</span>'
        f'</div>'
    )



# ─── TEMPLATE A — JUZ OPENER ─────────────────────────────────────

def render_juz_opener(juz_no=1, page_no=1):
    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', '[ JUZ OPENING ]', f'PAGE {page_no}')}
    <div class="body-juz">

      <div class="juz-title-block">
        <div class="juz-corner tl"></div>
        <div class="juz-corner tr"></div>
        <div class="juz-corner bl"></div>
        <div class="juz-corner br"></div>
        <div class="juz-eyebrow">PARA &middot; JUZ</div>
        <div class="juz-number">{juz_no}</div>
        <div class="juz-arabic-label">[ &#1580;&#1586;&#1569; ]</div>
      </div>

      <div class="juz-meta-row">
        <div class="juz-card">
          <div class="juz-card-title">Key Themes</div>
          <div class="juz-card-body">
            [ placeholder &mdash; theme one, theme two, theme three ]
          </div>
        </div>
        <div class="juz-card">
          <div class="juz-card-title">Learning Objectives</div>
          <div class="juz-card-body">
            [ placeholder &mdash; objective one, objective two, objective three ]
          </div>
        </div>
      </div>

      <div class="juz-intro">
        <div class="juz-intro-title">Introduction</div>
        <div class="juz-intro-body">
          [ placeholder for the introductory text that orients the reader to this Juz.
          Two to four short paragraphs describing the surahs covered, the central message,
          and the spiritual focus of this Para. Spacious, italic, easy to read for older
          learners. ]
        </div>
        <div class="juz-flourish">&middot; &middot; &middot;</div>
      </div>

    </div>
    {footer('[ Juz Opening ]', page_no, juz_no)}
  </div>
</div>'''



# ─── TEMPLATE B — SURAH OPENER ───────────────────────────────────

def render_surah_opener(juz_no=1, page_no=2):
    rows = ''.join(row_placeholder(r + 1) for r in range(SURAH_ROWS))
    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', '[ SURAH OPENING ]', f'PAGE {page_no}')}
    <div class="body-surah">

      <div class="surah-card">
        <div class="surah-arabic">[ &#1587;&#1615;&#1608;&#1585;&#1614;&#1577; ]</div>
        <div class="surah-english">[ SURAH NAME ]</div>
        <div class="surah-meta">
          Surah [ # ] &nbsp;&middot;&nbsp; [ Meaning ] &nbsp;&middot;&nbsp;
          Revealed in [ Place ] &nbsp;&middot;&nbsp; [ # ] Verses
        </div>
        <div class="surah-overview">
          [ short overview of this surah &mdash; one or two sentences explaining
          the central message and context for the reader ]
        </div>
        <div class="surah-bismillah">[ &#1576;&#1614;&#1587;&#1614;&#1605; ]</div>
      </div>

      <div class="grid-rows">
        {rows}
      </div>

      {tracker_strip()}
    </div>
    {footer('[ Surah Opening ]', page_no, juz_no)}
  </div>
</div>'''


# ─── TEMPLATE C — STANDARD WORKBOOK ──────────────────────────────

def render_standard(juz_no=1, page_no=3, surah_label='[ SURAH PLACEHOLDER ]'):
    rows = ''.join(row_placeholder(r + 1) for r in range(STANDARD_ROWS))
    meanings = ''.join(meaning_item(i + 1) for i in range(8))
    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', surah_label, f'PAGE {page_no}')}
    <div class="body-standard">

      <div class="meaning-panel">
        <div class="meaning-panel-title">Verse Meanings</div>
        {meanings}
      </div>

      <div class="grid">
        <div class="grid-rows">
          {rows}
        </div>
        {tracker_strip()}
      </div>

    </div>
    {footer('[ Standard Page ]', page_no, juz_no)}
  </div>
</div>'''



# ─── DEMO BUILD ──────────────────────────────────────────────────

def build_html():
    pages = [
        render_juz_opener(juz_no=1, page_no=1),
        render_surah_opener(juz_no=1, page_no=2),
        render_standard(juz_no=1, page_no=3),
        render_standard(juz_no=1, page_no=4),
    ]
    body = '\n\n'.join(pages)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Traceable Quran &#8212; Template System</title>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet"/>
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>'''

if __name__ == '__main__':
    out = Path(__file__).parent / 'template.html'
    out.write_text(build_html(), encoding='utf-8')
    print(f'Written: {out.name}')
    print(f'  Page size:        {PAGE_W_MM}mm x {PAGE_H_MM}mm  (A4)')
    print(f'  Body height:      {BODY_H_MM:.1f}mm')
    print(f'  Templates:        A=Juz opener, B=Surah opener, C=Standard')
    print(f'  Standard rows:    {STANDARD_ROWS} x {STANDARD_ROW_H_MM:.2f}mm = {STANDARD_ROW_AREA_MM}mm')
    print(f'  Surah rows:       {SURAH_ROWS} x {SURAH_ROW_H_MM:.2f}mm = {SURAH_ROW_AREA_MM}mm')
    print(f'  Tracker strip:    {TRACKER_MM}mm')
    print(f'  Words per row:    {WORDS_PER_ROW}')
    print(f'  Left panel:       {LEFT_COL_PCT}%, meaning font {MEANING_PT}pt')
