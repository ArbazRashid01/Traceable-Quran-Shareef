#!/usr/bin/env python3
"""
Traceable Quran — Workbook Framework v3 (FIXED LAYOUT)

Three independent page templates. Layout is fully fixed.
Content adapts to the layout. Layout NEVER adapts to content.

  A) Juz Opening Page    — minimal, decorative, no rows
  B) Surah Opening Page  — minimal, premium chapter card, no rows
  C) Standard Workbook   — 12-row tracing grid + 12-slot meaning panel

All measurements in mm. Every container uses overflow: hidden.
No flex-grow. No content-based sizing. No tracker / checkboxes / notes.
"""
from pathlib import Path

# ─── PAGE GEOMETRY (A4, all values in millimetres) ───────────────
PAGE_W          = 210
PAGE_H          = 297
PAD             = 10               # uniform inner padding
HEADER_H        = 14
FOOTER_H        = 10
BODY_W          = PAGE_W - 2 * PAD                              # 190
BODY_H          = PAGE_H - 2 * PAD - HEADER_H - FOOTER_H        # 253

# Frame (decorative border)
FRAME_W         = 0.5
FRAME_GAP       = 1.5

# Standard page row grid
ROW_COUNT       = 12
ROW_H           = BODY_H / ROW_COUNT                            # 21.083 mm
WORDS_PER_ROW   = 10
LEFT_PCT        = 22                                            # left panel width

# Within each row: fixed sub-section heights (sum == ROW_H)
TR_H            = 4.5
DIV_H           = 0.3
AR_H            = 11.483
MN_H            = 4.5
# 4.5 + 0.3 + 11.483 + 0.3 + 4.5 = 21.083 ✓

# Meaning slot — same height as row for vertical alignment
MEANING_SLOT_H  = ROW_H

# Typography (fixed)
TR_PT           = 9
AR_PT           = 22
MN_PT_CELL      = 9
MEANING_PT      = 11               # left-panel verse meaning
MEANING_NUM_PT  = 11



# ─── PALETTE ─────────────────────────────────────────────────────
INK_DARK     = '#1a0e04'
INK_BODY     = '#2a1a06'
GOLD         = '#c9a84c'
GOLD_DEEP    = '#8b6c14'
GOLD_LIGHT   = '#e8d49a'
PARCHMENT    = '#fdf7ed'
PARCHMENT_2  = '#f6ead6'
AMBER        = '#a07830'
HAIRLINE     = '#e4d0a8'
ROW_BORDER   = '#d4b870'
GRAY_TRACE   = 'rgba(0,0,0,0.13)'
PH_BG        = '#f8f1dc'
PH_TX        = '#bfa770'

# ─── CSS — base / page frame / header / footer (shared by A,B,C) ──
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

.page {{
  position: relative;
  width: {PAGE_W}mm;
  height: {PAGE_H}mm;
  padding: {PAD}mm;
  background: {PARCHMENT};
  border: {FRAME_W}mm solid {GOLD};
  box-shadow:
    0 0 0 {FRAME_GAP}mm {PARCHMENT},
    0 0 0 {FRAME_GAP + FRAME_W}mm {GOLD},
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
  overflow: hidden;
}}

/* HEADER (identical on A, B, C) */
.header {{
  flex: 0 0 {HEADER_H}mm;
  height: {HEADER_H}mm;
  display: flex; align-items: center; justify-content: space-between;
  background: #f8f0dc;
  border-top: 0.6mm solid {GOLD_DEEP};
  border-bottom: 0.6mm solid {GOLD_DEEP};
  box-shadow: inset 0 0.6mm 0 {GOLD_LIGHT}, inset 0 -0.6mm 0 {GOLD_LIGHT};
  padding: 0 4mm;
  overflow: hidden;
}}
.header-juz, .header-page {{
  font-size: 9pt; font-weight: 700; color: {GOLD_DEEP};
  letter-spacing: 1.2px; text-transform: uppercase; width: 22mm;
  overflow: hidden; white-space: nowrap; text-overflow: clip;
}}
.header-page {{ text-align: right; }}
.header-mid {{
  display: flex; align-items: center; gap: 3mm;
  overflow: hidden; max-width: 130mm;
}}
.header-orn {{ font-size: 11pt; color: {GOLD}; line-height: 1; }}
.header-name {{
  font-size: 12pt; font-weight: 700; letter-spacing: 2.4px;
  color: {INK_DARK}; text-transform: uppercase;
  overflow: hidden; white-space: nowrap; text-overflow: clip;
}}

/* FOOTER (identical on A, B, C) */
.footer {{
  flex: 0 0 {FOOTER_H}mm;
  height: {FOOTER_H}mm;
  display: flex; align-items: center; justify-content: space-between;
  border-top: 0.6mm solid {GOLD_DEEP};
  padding: 0 4mm;
  font-size: 9pt; font-weight: 600; color: {GOLD_DEEP};
  letter-spacing: 0.4px;
  overflow: hidden; white-space: nowrap;
}}
"""



# ─── CSS — STANDARD PAGE (Template C) ────────────────────────────
CSS_STD = f"""
.body-c {{
  flex: 0 0 {BODY_H}mm;
  height: {BODY_H}mm;
  display: flex; flex-direction: row;
  border: 0.3mm solid {ROW_BORDER};
  overflow: hidden;
}}

/* LEFT — meaning panel, free-flowing, no slot height constraints */
.panel {{
  flex: 0 0 {LEFT_PCT}%;
  width: {LEFT_PCT}%;
  background: {PARCHMENT_2};
  border-right: 0.4mm solid {ROW_BORDER};
  display: flex; flex-direction: column;
  overflow: hidden;
  padding: 2mm 2mm;
  gap: 0;
}}
.slot {{
  padding: 2mm 1.5mm;
  border-bottom: 0.3mm dashed {HAIRLINE};
}}
.slot:last-child {{ border-bottom: none; }}
.slot-num {{
  font-family: 'Amiri', serif;
  font-size: {MEANING_NUM_PT}pt; font-weight: 700;
  color: {GOLD_DEEP}; line-height: 1.4;
}}
.slot-text {{
  font-size: {MEANING_PT}pt; font-style: italic;
  color: {INK_BODY}; line-height: 1.5;
  word-wrap: break-word;
}}

/* RIGHT — word rows, no fixed row count or height */
.grid {{
  flex: 1 1 auto;
  display: flex; flex-direction: column;
  overflow: hidden;
  background: {PARCHMENT};
}}
/* Each row sizes to tallest cell — no fixed height */
.row {{
  display: flex;
  flex-direction: row-reverse;
  align-items: stretch;
  border-bottom: 0.3mm solid {HAIRLINE};
  flex-shrink: 0;
}}
.row:last-child {{ border-bottom: none; }}

/* Cells: CSS grid with 3 guaranteed rows — transliteration / arabic / meaning.
   Each section has a hard minimum slot. Text wraps within its slot.
   Nothing can collapse into or overlap another section. */
.cell {{
  flex: 3;
  min-width: 0;
  display: grid;
  grid-template-rows: minmax(8mm, auto) minmax(11mm, auto) minmax(8mm, auto);
  border-left: 0.2mm dotted rgba(200,180,140,.35);
}}
.cell:last-child {{ border-left: none; }}

/* Transliteration — top grid row, wraps freely within its slot */
.tr {{
  font-size: {TR_PT}pt; font-style: italic;
  color: {AMBER};
  text-align: center;
  padding: 2px 3px;
  line-height: 1.4;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  align-self: center;
}}

/* Arabic — middle grid row, always occupies its full minimum slot */
.ar {{
  font-family: 'Amiri', serif;
  font-size: {AR_PT}pt;
  color: {GRAY_TRACE};
  direction: rtl; text-align: center;
  padding: 3px 2px;
  white-space: nowrap;
  align-self: center;
}}

/* Meaning — bottom grid row, wraps freely within its slot */
.mn {{
  font-size: {MN_PT_CELL}pt;
  color: {INK_BODY};
  text-align: center;
  padding: 2px 3px;
  line-height: 1.4;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  align-self: center;
}}

"""



# ─── CSS — SURAH OPENING (Template B) ────────────────────────────
CSS_SURAH = f"""
.body-b {{
  flex: 0 0 {BODY_H}mm;
  height: {BODY_H}mm;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 18mm 16mm;
  background: linear-gradient(180deg, {PARCHMENT} 0%, #faedc6 50%, {PARCHMENT} 100%);
  overflow: hidden;
  position: relative;
}}
.body-b::before, .body-b::after {{
  content: '';
  position: absolute; left: 0; right: 0;
  height: 0; border-top: 0.4mm double {GOLD};
  pointer-events: none;
}}
.body-b::before {{ top: 8mm; }}
.body-b::after  {{ bottom: 8mm; }}

.b-orn-top, .b-orn-bot {{
  font-size: 18pt; color: {GOLD};
  letter-spacing: 12px; text-align: center;
  height: 10mm; line-height: 10mm;
  flex: 0 0 10mm;
  overflow: hidden;
}}
.b-arabic {{
  flex: 0 0 28mm; height: 28mm;
  font-family: 'Amiri', serif; font-weight: 700;
  font-size: 38pt; color: {INK_DARK};
  direction: rtl; text-align: center;
  letter-spacing: 1px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; white-space: nowrap;
}}
.b-english {{
  flex: 0 0 10mm; height: 10mm;
  font-size: 18pt; font-weight: 700;
  letter-spacing: 6px; text-transform: uppercase;
  color: {GOLD_DEEP}; text-align: center;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; white-space: nowrap;
}}
.b-meta {{
  flex: 0 0 8mm; height: 8mm;
  font-size: 10pt; color: {GOLD_DEEP};
  letter-spacing: 1.2px;
  text-align: center;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; white-space: nowrap;
}}
.b-divider {{
  flex: 0 0 8mm; height: 8mm;
  text-align: center;
  font-size: 14pt; color: {GOLD};
  letter-spacing: 8px;
  line-height: 8mm;
  overflow: hidden;
}}
.b-overview {{
  flex: 0 0 60mm; height: 60mm;
  font-size: 12pt; font-style: italic;
  color: {INK_BODY};
  text-align: center; line-height: 1.65;
  padding: 0 8mm;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 8;
  -webkit-box-orient: vertical;
}}
.b-bismillah {{
  flex: 0 0 22mm; height: 22mm;
  font-family: 'Amiri', serif;
  font-size: 28pt; color: rgba(0,0,0,0.18);
  direction: rtl; text-align: center;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; white-space: nowrap;
}}
"""



# ─── CSS — JUZ OPENING (Template A) ──────────────────────────────
CSS_JUZ = f"""
.body-a {{
  flex: 0 0 {BODY_H}mm;
  height: {BODY_H}mm;
  display: flex; flex-direction: column;
  align-items: center;
  padding: 14mm 16mm;
  background: {PARCHMENT};
  overflow: hidden;
  position: relative;
}}

.a-eyebrow {{
  flex: 0 0 10mm; height: 10mm;
  font-size: 11pt; font-weight: 700;
  letter-spacing: 8px; text-transform: uppercase;
  color: {GOLD_DEEP};
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; white-space: nowrap;
}}
.a-divider-top {{
  flex: 0 0 6mm; height: 6mm;
  text-align: center;
  font-size: 13pt; color: {GOLD};
  letter-spacing: 10px;
  line-height: 6mm;
  overflow: hidden;
}}
.a-number {{
  flex: 0 0 70mm; height: 70mm;
  font-family: 'Amiri', serif; font-weight: 700;
  font-size: 80pt;
  color: {INK_DARK};
  text-align: center;
  display: flex; align-items: center; justify-content: center;
  line-height: 1;
  overflow: hidden;
}}
.a-arabic-label {{
  flex: 0 0 14mm; height: 14mm;
  font-family: 'Amiri', serif;
  font-size: 22pt; color: {GOLD_DEEP};
  direction: rtl; text-align: center;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden; white-space: nowrap;
}}
.a-divider-mid {{
  flex: 0 0 6mm; height: 6mm;
  text-align: center;
  font-size: 13pt; color: {GOLD};
  letter-spacing: 10px;
  line-height: 6mm;
  overflow: hidden;
}}
.a-intro {{
  flex: 0 0 60mm; height: 60mm;
  font-size: 11pt; font-style: italic;
  color: {INK_BODY};
  text-align: center; line-height: 1.7;
  padding: 0 8mm;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 8;
  -webkit-box-orient: vertical;
}}
.a-themes {{
  flex: 0 0 30mm; height: 30mm;
  width: 100%;
  border-top: 0.3mm solid {ROW_BORDER};
  padding: 4mm 8mm 0 8mm;
  overflow: hidden;
}}
.a-themes-title {{
  font-size: 9pt; font-weight: 700;
  letter-spacing: 3px; text-transform: uppercase;
  color: {GOLD_DEEP};
  text-align: center;
  margin-bottom: 2mm;
}}
.a-themes-text {{
  font-size: 11pt; font-style: italic;
  color: {INK_BODY}; text-align: center;
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}}
"""



CSS_PRINT = """
@media print {
  @page { size: A4; margin: 0; }
  body  { background: #fdf7ed; padding: 0; gap: 0; }
  .page { box-shadow: none; margin: 0; page-break-after: always; break-after: page; }
  .page:last-of-type { page-break-after: auto; break-after: auto; }
  .row, .slot { page-break-inside: avoid; break-inside: avoid; }
}
"""

CSS = CSS_BASE + CSS_STD + CSS_SURAH + CSS_JUZ + CSS_PRINT


# ─── COMPONENTS — Header & Footer ────────────────────────────────

def header(juz, mid, page):
    return (
        f'<div class="header">'
        f'<span class="header-juz">{juz}</span>'
        f'<div class="header-mid">'
        f'<span class="header-orn">&#10022;</span>'
        f'<span class="header-name">{mid}</span>'
        f'<span class="header-orn">&#10022;</span>'
        f'</div>'
        f'<span class="header-page">{page}</span>'
        f'</div>'
    )

def footer(left, page, juz=1):
    return (
        f'<div class="footer">'
        f'<span>{left}</span>'
        f'<span>Page {page} &nbsp;|&nbsp; Juz {juz}</span>'
        f'</div>'
    )


# ─── TEMPLATE A — JUZ OPENING ────────────────────────────────────

def render_juz_opener(juz_no=1, page_no=1):
    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', '[ JUZ OPENING ]', f'PAGE {page_no}')}
    <div class="body-a">
      <div class="a-eyebrow">PARA &middot; JUZ</div>
      <div class="a-divider-top">&middot; &middot; &middot;</div>
      <div class="a-number">{juz_no}</div>
      <div class="a-arabic-label">[ &#1580;&#1586;&#1569; ]</div>
      <div class="a-divider-mid">&middot; &middot; &middot;</div>
      <div class="a-intro">
        [ short introduction placeholder &mdash; one or two paragraphs orienting the
        reader to this Juz: which surahs are covered, the central themes, and what
        the reader will learn. Italic, comfortable for older readers. ]
      </div>
      <div class="a-themes">
        <div class="a-themes-title">Key Themes</div>
        <div class="a-themes-text">
          [ theme one &middot; theme two &middot; theme three &middot; theme four ]
        </div>
      </div>
    </div>
    {footer('[ Juz Opening ]', page_no, juz_no)}
  </div>
</div>'''



# ─── TEMPLATE B — SURAH OPENING ──────────────────────────────────

def render_surah_opener(juz_no=1, page_no=2):
    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', '[ SURAH OPENING ]', f'PAGE {page_no}')}
    <div class="body-b">
      <div class="b-orn-top">&#10022; &#10022; &#10022;</div>
      <div class="b-arabic">[ &#1587;&#1615;&#1608;&#1585;&#1614;&#1577; ]</div>
      <div class="b-english">[ SURAH NAME ]</div>
      <div class="b-meta">
        Surah [ # ] &nbsp;&middot;&nbsp; [ Meaning ] &nbsp;&middot;&nbsp;
        [ Place ] &nbsp;&middot;&nbsp; [ # ] Verses
      </div>
      <div class="b-divider">&middot; &middot; &middot;</div>
      <div class="b-overview">
        [ overview placeholder &mdash; a short, calm introduction to this Surah&apos;s
        central message, when it was revealed, and why it matters. Three to five lines
        of italic text, generously spaced, easy to read. ]
      </div>
      <div class="b-bismillah">[ &#1576;&#1614;&#1587;&#1614;&#1605; ]</div>
      <div class="b-orn-bot">&#10022; &#10022; &#10022;</div>
    </div>
    {footer('[ Surah Opening ]', page_no, juz_no)}
  </div>
</div>'''


# ─── TEMPLATE C — STANDARD WORKBOOK ──────────────────────────────

def render_standard(juz_no=1, page_no=3, surah_label='[ SURAH PLACEHOLDER ]'):
    # 12 fixed meaning slots
    slots = ''.join(
        f'<div class="slot">'
        f'<div class="slot-num">[ {i+1} ]</div>'
        f'<div class="slot-text">[ verse meaning placeholder &mdash; a comfortable italic '
        f'summary, capped at three lines and clipped beyond ]</div>'
        f'</div>'
        for i in range(ROW_COUNT)
    )

    # 12 rows × 10 cells, each cell with 5 fixed sections
    cells = ''.join(
        f'<div class="cell">'
        f'<div class="tr">tr-{i+1}</div>'
        f'<div class="ar">&#1593;</div>'
        f'<div class="mn">m-{i+1}</div>'
        f'</div>'
        for i in range(WORDS_PER_ROW)
    )
    rows = ''.join(
        f'<div class="row" data-row="{r+1}">{cells}</div>'
        for r in range(ROW_COUNT)
    )

    return f'''<div class="page">
  <div class="page-inner">
    {header(f'JUZ {juz_no}', surah_label, f'PAGE {page_no}')}
    <div class="body-c">
      <div class="panel">{slots}</div>
      <div class="grid">{rows}</div>
    </div>
    {footer('[ Standard Page ]', page_no, juz_no)}
  </div>
</div>'''



# ─── BUILD ───────────────────────────────────────────────────────

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
  <title>Traceable Quran &#8212; Workbook Framework v3</title>
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
    # Verify maths
    row_sum = TR_H + DIV_H + AR_H + DIV_H + MN_H
    print(f'Written: {out.name}')
    print(f'  Page:           {PAGE_W}mm x {PAGE_H}mm  (A4)')
    print(f'  Header / Footer:{HEADER_H}mm / {FOOTER_H}mm')
    print(f'  Body:           {BODY_H}mm  (= {ROW_COUNT} rows x {ROW_H:.3f}mm)')
    print(f'  Row sub-sections sum: {row_sum:.3f}mm  (must equal row {ROW_H:.3f}mm)')
    print(f'  Standard cell sections (fixed mm): tr={TR_H} ar={AR_H} mn={MN_H}')
    print(f'  Words per row:  {WORDS_PER_ROW}  (cell width = {BODY_W * (1 - LEFT_PCT/100) / WORDS_PER_ROW:.2f}mm)')
    print(f'  Left panel:     {LEFT_PCT}%, {ROW_COUNT} slots x {MEANING_SLOT_H:.3f}mm')
    print(f'  Removed:        tracker, checkboxes, date, notes, reflection')
