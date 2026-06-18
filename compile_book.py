#!/usr/bin/env python3
"""
Compile the ENTIRE Traceable Quran into ONE printed-book HTML file:
  * Front matter (roman numerals i, ii, iii ...)
  * All 30 Juz (arabic page numbers 1 ...)
  * Back matter (arabic, continuing)
  * Juz Index & Surah Index show REAL page numbers (no file names)
  * No digital references anywhere — pure offline book
  * Fonts embedded once

Output: Traceable-Quran-Complete.html
"""
import re, base64
from pathlib import Path
import build_all as B
import build_front_back as F

BASE = Path(__file__).parent
OUT  = BASE / 'Traceable-Quran-Complete.html'
CH   = B.CH

# ─── roman numerals (front matter) ───────────────────────────────
def roman(n):
    vals=[(1000,'m'),(900,'cm'),(500,'d'),(400,'cd'),(100,'c'),(90,'xc'),
          (50,'l'),(40,'xl'),(10,'x'),(9,'ix'),(5,'v'),(4,'iv'),(1,'i')]
    out=''
    for v,s in vals:
        while n>=v: out+=s; n-=v
    return out

# ─── strip a builder's full page down to its inner content ───────
def inner_of(full_page_html):
    m = re.search(r'<div class="inner">(.*)</div></div>\s*$', full_page_html, re.S)
    inner = m.group(1) if m else full_page_html
    inner = re.sub(r'^\s*<div class="header">.*?</div>\s*', '', inner, count=1, flags=re.S)
    inner = re.sub(r'\s*<div class="footer">.*?</div>\s*$', '', inner, count=1, flags=re.S)
    return inner

# ─── unified book page shell ─────────────────────────────────────
def shell(inner, running, pageno_str, chrome=True):
    if not chrome:
        return f'<div class="page"><div class="inner">{inner}</div></div>'
    header = (f'<div class="header"><span class="h-side"></span>'
              f'<span class="h-mid">{running}</span>'
              f'<span class="h-side h-r"></span></div>')
    footer = (f'<div class="footer bookftr"><span class="pageno">'
              f'&mdash;&nbsp;{pageno_str}&nbsp;&mdash;</span></div>')
    return f'<div class="page"><div class="inner">{header}{inner}{footer}</div></div>'



# ─── BODY: build all 30 juz pages with metadata ──────────────────
def build_body():
    """Return list of (inner_html, running_title) and record start pages."""
    pages = []                      # (inner_html, running_title)
    juz_start = {}                  # juz -> 1-based body page number
    surah_start = {}                # chapter(str) -> 1-based body page number
    for juz in range(1, 31):
        rmap = B.ruku_end_map(B.juz_verse_keys(juz))
        layout = [('openjuz',)]
        for ch, vks in B.chapter_segments(juz):
            label = CH[ch]['name_en'].upper()
            if vks and vks[0].endswith(':1'):
                layout.append(('opensurah', ch))
            rows_pages = B.paginate(B.pack(B.make_items(vks, rmap)))
            for k, pr in enumerate(rows_pages):
                is_last = (k == len(rows_pages)-1)
                layout.append(('std', label, pr, B.completing_keys(pr), is_last))
        carry = []
        last_label = 'JUZ'
        for item in layout:
            if item[0] == 'openjuz':
                full = B.page_juz_opener(juz, 0)
                running = f'Juz {juz}'
                juz_start[juz] = len(pages) + 1
            elif item[0] == 'opensurah':
                ch = item[1]
                full = B.page_surah_opener(juz, 0, ch)
                running = CH[ch]['name_en']
                surah_start[ch] = len(pages) + 1
            else:
                _, label, rows, comp, is_last = item
                last_label = label
                blocks = [B.meaning_block(vk) for vk in comp]
                panel_html, carry = B.flow_panel(blocks, carry)
                decorate = is_last and (B.row_fill_mm(rows) < B.BODY_H*0.55) and not carry
                full = B.page_std(juz, 0, label, rows, panel_html, decorate)
                running = label.title()
            pages.append((inner_of(full), running))
        while carry:
            panel_html, carry = B.flow_panel([], carry)
            full = B.page_panel_cont(juz, 0, last_label, panel_html)
            pages.append((inner_of(full), last_label.title()))
    return pages, juz_start, surah_start



# ─── Regenerated INDEX pages with real page numbers ──────────────
def juz_index_inner(juz_start, body_offset):
    rows = ''
    for j in range(1, 31):
        surahs = []
        for ch, rng in B.JUZ_MAP[j].items():
            a, b = rng.split('-')
            surahs.append(f"{CH[ch]['name_en']} ({a}&ndash;{b})")
        pg = juz_start[j] + body_offset - 1 + 1  # arabic page number
        rows += (f'<tr><td><strong>{j}</strong></td>'
                 f'<td class="ar">&#1575;&#1604;&#1580;&#1586;&#1569; {j}</td>'
                 f'<td>{" &nbsp;|&nbsp; ".join(surahs)}</td>'
                 f'<td style="text-align:center"><strong>{pg}</strong></td></tr>')
    return (f'<div class="body">{F.section("Juz Index")}'
            f'{F.para("The Holy Qur&#8217;an is divided into 30 Juz (Para). The page number shows where each Juz begins in this book.")}'
            f'<table class="idx-table"><tr><th>#</th><th>Arabic</th>'
            f'<th>Surahs Covered</th><th>Page</th></tr>{rows}</table></div>')

def surah_index_inner(surah_start, body_offset, lo, hi):
    rows = ''
    for ch in range(lo, hi+1):
        m = CH[str(ch)]
        pg = surah_start.get(str(ch))
        pg_str = str(pg) if pg else '&mdash;'
        rows += (f'<tr><td>{ch}</td><td class="ar">{m["name_ar"]}</td>'
                 f'<td>{m["name_en"]}</td><td>{m["meaning"]}</td>'
                 f'<td>{m["revealed"]}</td><td style="text-align:center">{m["verses"]}</td>'
                 f'<td style="text-align:center"><strong>{pg_str}</strong></td></tr>')
    return (f'<div class="body">{F.section(f"Surah Index ({lo}&ndash;{hi})")}'
            f'<table class="idx-table"><tr><th>#</th><th>Arabic</th><th>Name</th>'
            f'<th>Meaning</th><th>Type</th><th>Verses</th><th>Page</th></tr>'
            f'{rows}</table></div>')



# ─── COMBINED CSS (body layout + front/back typography + book chrome) ──
def combined_css():
    return B.css() + F.CSS + """
/* book-specific page number footer */
.footer.bookftr{justify-content:center}
.pageno{font-size:10pt;font-weight:600;color:#8b6c14;letter-spacing:1px}
.idx-table td:last-child{font-variant-numeric:tabular-nums}
"""


# ─── ASSEMBLE THE BOOK ───────────────────────────────────────────
def main():
    # 1) Build body first to know surah/juz start page numbers
    body_pages, juz_start, surah_start = build_body()   # body page 1..N (arabic)

    # 2) Front matter: (running_title, inner_html, chrome)
    front = []
    front.append(('', inner_of(F.p_cover()), False))          # cover — no chrome
    front.append(('Title', inner_of(F.p_title()), True))
    front.append(('Copyright', inner_of(F.p_copyright()), True))
    front.append(('Preface', inner_of(F.p_preface()), True))
    front.append(('How to Use This Workbook', inner_of(F.p_how_to_use()), True))
    front.append(('Workbook Methodology', inner_of(F.p_methodology()), True))
    front.append(('Transliteration Guide', inner_of(F.p_transliteration_guide()), True))
    front.append(('Symbols &amp; Conventions', inner_of(F.p_symbols()), True))
    front.append(('Learning Roadmap', inner_of(F.p_learning_roadmap()), True))
    front.append(('Qur&#8217;an Structure', inner_of(F.p_quran_structure()), True))
    front.append(('Juz Index', juz_index_inner(juz_start, 0), True))
    front.append(('Surah Index', surah_index_inner(surah_start, 0, 1, 57), True))
    front.append(('Surah Index', surah_index_inner(surah_start, 0, 58, 114), True))
    front.append(('Introduction to the Qur&#8217;an', inner_of(F.p_introduction()), True))
    front.append(('Virtues of Learning the Qur&#8217;an', inner_of(F.p_virtues()), True))
    front.append(('Etiquettes of Qur&#8217;an Study', inner_of(F.p_etiquettes()), True))

    # 3) Back matter
    back = [
        ('Khatm ul-Qur&#8217;an', inner_of(F.p_khatm()), True),
        ('Du&#8216;a After Completion', inner_of(F.p_dua_khatm()), True),
        ('Reflection', inner_of(F.p_reflection()), True),
        ('About This Workbook', inner_of(F.p_about_workbook()), True),
        ('Closing Message', inner_of(F.p_final_message()), True),
    ]

    # 4) Render in order with continuous numbering
    html_pages = []
    # FRONT — roman
    rn = 0
    for running, inner, chrome in front:
        if not chrome:
            html_pages.append(shell(inner, '', '', chrome=False))
        else:
            rn += 1
            html_pages.append(shell(inner, running, roman(rn), True))
    # BODY — arabic 1..
    for i, (inner, running) in enumerate(body_pages, start=1):
        html_pages.append(shell(inner, running, str(i), True))
    # BACK — arabic continues
    n = len(body_pages)
    for running, inner, chrome in back:
        n += 1
        html_pages.append(shell(inner, running, str(n), True))

    doc = (f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>'
           f'<meta name="viewport" content="width=device-width,initial-scale=1.0"/>'
           f'<title>The Traceable Qur&#8217;an &mdash; Complete</title>'
           f'{B.fonts_block()}<style>{combined_css()}</style></head><body>'
           f'{"".join(html_pages)}</body></html>')
    OUT.write_text(doc, encoding='utf-8')
    total = len(html_pages)
    print(f'Written {OUT.name}: {total} pages total '
          f'(front {len(front)} + body {len(body_pages)} + back {len(back)}), '
          f'{OUT.stat().st_size//1024//1024} MB')

if __name__ == '__main__':
    main()
