#!/usr/bin/env python3
"""
Generate Front Matter and Back Matter HTML for the Traceable Quran Workbook.
Output:  juz/Front-Matter.html   (20 pages)
         juz/Back-Matter.html    ( 9 pages)

Uses the identical page shell (A4, gold border, ivory, EB Garamond / Amiri)
as all 30 Juz files.
"""
import json, base64, re
from pathlib import Path

BASE     = Path(__file__).parent
FONT_DIR = BASE / 'fonts'
OUTDIR   = BASE / 'juz'
DATA     = json.loads((BASE / 'quran_data.json').read_text(encoding='utf-8'))
CH       = DATA['chapters']

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

# ─── Fonts ────────────────────────────────────────────────────────
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


# ─── CSS ──────────────────────────────────────────────────────────
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#9e8f72;font-family:'EB Garamond','Georgia',serif;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
body{display:flex;flex-direction:column;align-items:center;padding:28px 0;gap:28px}

/* PAGE */
.page{position:relative;width:210mm;height:297mm;padding:12mm;
  background:#fdf7ed;border:0.5mm solid #c9a84c;
  box-shadow:0 0 0 1.5mm #fdf7ed,0 0 0 2mm #c9a84c,0 12px 50px rgba(0,0,0,.30);
  overflow:hidden}
.page::before{content:'';position:absolute;top:4.5mm;right:4.5mm;
  bottom:4.5mm;left:4.5mm;border:0.3mm solid rgba(201,168,76,.4);pointer-events:none}
.inner{position:relative;width:100%;height:100%;
  display:flex;flex-direction:column}

/* HEADER / FOOTER */
.header{flex:0 0 14mm;display:flex;align-items:center;
  justify-content:space-between;background:#f8f0dc;
  border-top:0.6mm solid #8b6c14;border-bottom:0.6mm solid #8b6c14;
  box-shadow:inset 0 0.6mm 0 #e8d49a,inset 0 -0.6mm 0 #e8d49a;padding:0 5mm}
.h-side{font-size:9pt;font-weight:700;color:#8b6c14;letter-spacing:1.2px;width:24mm}
.h-r{text-align:right}
.h-mid{font-size:12pt;font-weight:700;letter-spacing:2px;color:#1a0e04;text-transform:uppercase}
.footer{flex:0 0 10mm;display:flex;align-items:center;
  justify-content:space-between;border-top:0.6mm solid #8b6c14;padding:0 5mm;
  font-size:9pt;font-weight:600;color:#8b6c14}

/* TEXT BODY */
.body{flex:1 1 auto;padding:5mm 4mm 3mm;overflow:hidden}

/* ─── TYPOGRAPHY ─── */
.c-title{font-size:32pt;font-weight:700;color:#1a0e04;text-align:center;
  letter-spacing:2px;margin-bottom:3mm}
.c-subtitle{font-size:14pt;font-style:italic;color:#8b6c14;text-align:center;
  letter-spacing:1px;margin-bottom:6mm}
.c-arabic-main{font-family:'Amiri',serif;font-size:44pt;font-weight:700;
  color:#1a0e04;direction:rtl;text-align:center;line-height:1.3;margin:4mm 0}
.c-rule{border:none;border-top:0.4mm solid #c9a84c;margin:5mm 0}
.c-ornament{text-align:center;font-size:16pt;color:#c9a84c;letter-spacing:10px;margin:3mm 0}
.c-section{font-size:13pt;font-weight:700;color:#8b6c14;letter-spacing:2px;
  text-transform:uppercase;margin:5mm 0 2mm;border-bottom:0.3mm dashed #d4b870;
  padding-bottom:1.5mm}
.c-para{font-size:11pt;color:#2a1a06;line-height:1.7;margin-bottom:3.5mm;
  text-align:justify}
.c-hadith{font-size:11pt;font-style:italic;color:#2a1a06;line-height:1.7;
  background:#f6ead6;border-left:1mm solid #c9a84c;padding:3mm 4mm;
  margin:4mm 0;border-radius:0 2mm 2mm 0}
.c-hadith-src{font-size:9pt;color:#8b6c14;font-weight:700;font-style:normal;
  margin-top:1.5mm;display:block}
.c-arabic-hadith{font-family:'Amiri',serif;font-size:16pt;direction:rtl;
  text-align:right;color:#1a0e04;line-height:1.6;margin-bottom:2mm}
.c-note{font-size:10pt;font-style:italic;color:#8b6c14;
  border:0.3mm dashed #d4b870;padding:2mm 3mm;margin:3mm 0}
.c-list{list-style:none;padding:0;margin:2mm 0}
.c-list li{font-size:11pt;color:#2a1a06;line-height:1.6;padding:1mm 0;
  padding-left:4mm;position:relative}
.c-list li::before{content:'❖';position:absolute;left:0;color:#c9a84c;font-size:8pt;top:1.5mm}
.c-numlist li{font-size:11pt;color:#2a1a06;line-height:1.6;padding:1mm 0;
  padding-left:6mm;position:relative}
.c-numlist li::before{content:counter(li);counter-increment:li;position:absolute;
  left:0;color:#8b6c14;font-weight:700;font-size:10pt}
.c-numlist{counter-reset:li}
.c-col2{display:grid;grid-template-columns:1fr 1fr;gap:4mm;margin:2mm 0}
.c-col3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:3mm;margin:2mm 0}
.c-card{background:#f6ead6;border:0.3mm solid #d4b870;padding:2.5mm 3mm;
  border-radius:1.5mm}
.c-card-title{font-size:10pt;font-weight:700;color:#8b6c14;margin-bottom:1mm}
.c-card-txt{font-size:9.5pt;color:#2a1a06;line-height:1.5}

/* ─── COVER PAGE ─── */
.cover-inner{width:100%;height:100%;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:4mm}
.cover-eyebrow{font-size:10pt;font-weight:700;letter-spacing:8px;color:#8b6c14;
  text-transform:uppercase}
.cover-main-ar{font-family:'Amiri',serif;font-size:52pt;font-weight:700;
  color:#1a0e04;direction:rtl;text-align:center;line-height:1.2}
.cover-main-en{font-size:36pt;font-weight:700;letter-spacing:4px;color:#1a0e04;
  text-transform:uppercase;text-align:center}
.cover-sub{font-size:14pt;font-style:italic;color:#8b6c14;text-align:center;
  letter-spacing:1.5px}
.cover-rule{width:60%;border-top:0.5mm solid #c9a84c;margin:2mm auto}
.cover-desc{font-size:12pt;font-style:italic;color:#2a1a06;text-align:center;
  max-width:130mm;line-height:1.7}
.cover-edition{font-size:10pt;color:#8b6c14;letter-spacing:2px;text-transform:uppercase}
.cover-juz{font-family:'Amiri',serif;font-size:28pt;color:rgba(0,0,0,0.15);
  direction:rtl;text-align:center;margin:2mm 0}

/* ─── TABLES ─── */
.c-table{width:100%;border-collapse:collapse;font-size:9.5pt;color:#2a1a06}
.c-table th{background:#f6ead6;color:#8b6c14;font-weight:700;text-align:left;
  padding:1.5mm 2mm;border-bottom:0.4mm solid #d4b870;font-size:9pt;letter-spacing:.5px}
.c-table td{padding:1.2mm 2mm;border-bottom:0.2mm solid #ece0c4;line-height:1.4}
.c-table tr:nth-child(even) td{background:#faf4ea}
.c-table .ar{font-family:'Amiri',serif;font-size:12pt;direction:rtl;text-align:right}

/* INDEX TABLE */
.idx-table{width:100%;border-collapse:collapse;font-size:8.5pt}
.idx-table th{background:#8b6c14;color:#fdf7ed;font-weight:700;padding:1.5mm 2mm;
  text-align:left}
.idx-table td{padding:0.8mm 2mm;border-bottom:0.15mm solid #ece0c4;color:#1a0e04}
.idx-table tr:nth-child(even) td{background:#faf4ea}
.idx-table .ar{font-family:'Amiri',serif;font-size:10pt;direction:rtl;text-align:right}

/* ─── KHATM PAGE ─── */
.khatm-body{width:100%;height:100%;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:5mm}
.khatm-ar{font-family:'Amiri',serif;font-size:36pt;color:#1a0e04;
  direction:rtl;text-align:center;line-height:1.5}
.khatm-msg{font-size:14pt;font-style:italic;color:#8b6c14;text-align:center;
  line-height:1.8;max-width:150mm}
.khatm-date{font-size:11pt;color:#8b6c14;letter-spacing:2px}

/* PRINT */
@media print{@page{size:A4;margin:0}body{background:#fdf7ed;padding:0;gap:0}
  .page{box-shadow:none;margin:0;page-break-after:always;break-after:page;overflow:visible}
  .page:last-of-type{page-break-after:auto;break-after:auto}}
"""


# ─── Page Shell ───────────────────────────────────────────────────
def page(content, hdr_mid='', hdr_left='', hdr_right='', ftr_left='', ftr_right='', no_header=False):
    h = (f'<div class="header"><span class="h-side">{hdr_left}</span>'
         f'<span class="h-mid">{hdr_mid}</span>'
         f'<span class="h-side h-r">{hdr_right}</span></div>') if not no_header else ''
    f = f'<div class="footer"><span>{ftr_left}</span><span>{ftr_right}</span></div>'
    return (f'<div class="page"><div class="inner">{h}'
            f'{content}{f}</div></div>')

def body(html):
    return f'<div class="body">{html}</div>'

# ─── HELPERS ─────────────────────────────────────────────────────
def rule(): return '<hr class="c-rule"/>'
def orn(): return '<div class="c-ornament">&#10022; &#10022; &#10022;</div>'
def section(t): return f'<div class="c-section">{t}</div>'
def para(t): return f'<p class="c-para">{t}</p>'
def hadith(ar_txt, en_txt, source):
    return (f'<div class="c-hadith"><div class="c-arabic-hadith">{ar_txt}</div>'
            f'<em>"{en_txt}"</em><span class="c-hadith-src">&mdash; {source}</span></div>')
def note(t): return f'<div class="c-note">{t}</div>'
def ul(items): return '<ul class="c-list">'+''.join(f'<li>{i}</li>' for i in items)+'</ul>'
def ol(items): return '<ol class="c-numlist">'+''.join(f'<li>{i}</li>' for i in items)+'</ol>'

def hdr(mid, left='TRACEABLE QURAN', right='WORKBOOK'):
    return mid, left, right


# ═══════════════════════════════════════════════════════════
# FRONT MATTER PAGES
# ═══════════════════════════════════════════════════════════

def p_cover():
    c = '''<div class="cover-inner">
<div class="cover-eyebrow">The Complete Word-by-Word Learning &amp; Tracing Edition</div>
<div class="c-ornament" style="font-size:22pt">&#10022; &#10022; &#10022;</div>
<div class="cover-main-ar">&#1575;&#1604;&#1602;&#1615;&#1585;&#1618;&#1570;&#1606;&#1615; &#1575;&#1604;&#1603;&#1614;&#1585;&#1616;&#1610;&#1605;&#1615;</div>
<div class="cover-main-en">THE TRACEABLE QURAN</div>
<div class="cover-sub">A Complete Workbook for Learning &amp; Reflection</div>
<div class="cover-rule"></div>
<div class="cover-desc">
  Word-by-word Arabic tracing &middot; Transliteration &middot; Meanings<br/>
  All 30 Juz &middot; 114 Surahs &middot; 6,236 Verses &middot; 77,429 Words
</div>
<div class="c-ornament" style="font-size:22pt">&#10022; &#10022; &#10022;</div>
<div class="cover-edition">First Edition</div>
</div>'''
    return page(c, no_header=True, ftr_left='', ftr_right='')

def p_title():
    c = body('''
<div style="height:20mm"></div>
<div class="c-arabic-main">&#1575;&#1604;&#1602;&#1615;&#1585;&#1618;&#1570;&#1606;&#1615; &#1575;&#1604;&#1603;&#1614;&#1585;&#1616;&#1610;&#1605;&#1615;</div>
<div class="c-title">THE TRACEABLE QURAN</div>
<div class="c-subtitle">A Complete Word-by-Word Learning &amp; Tracing Workbook</div>
<hr class="c-rule"/>
<div style="height:12mm"></div>
<p class="c-para" style="text-align:center;font-size:12pt">
  Containing the complete text of the Noble Qur&#8217;an<br/>
  with word-by-word transliteration, English meanings,<br/>
  and dedicated tracing space for every Arabic word.
</p>
<div style="height:10mm"></div>
<p class="c-para" style="text-align:center;font-size:11pt;color:#8b6c14">
  All 30 Juz &nbsp;&middot;&nbsp; 114 Surahs &nbsp;&middot;&nbsp;
  6,236 Verses &nbsp;&middot;&nbsp; 77,429 Words
</p>
<div style="flex:1"></div>
<p class="c-para" style="text-align:center;font-size:10pt">
  First Edition<br/>
  Printed on A4 &nbsp;&middot;&nbsp; Designed for print and digital use
</p>
''')
    return page(c, 'TITLE PAGE', 'TRACEABLE QURAN', '', '', '')

def p_copyright():
    c = body('''
<div style="height:10mm"></div>
<div class="c-ornament">&#10022; &#10022; &#10022;</div>
<div style="height:6mm"></div>
<p class="c-para" style="text-align:center;font-size:13pt;font-weight:700">
  &#1576;&#1616;&#1587;&#1618;&#1605;&#1616; &#1649;&#1604;&#1604;&#1617;&#1614;&#1607;&#1616; &#1649;&#1604;&#1585;&#1617;&#1614;&#1581;&#1618;&#1605;&#1614;&#1610;&#1606;&#1616; &#1649;&#1604;&#1585;&#1617;&#1614;&#1581;&#1616;&#1610;&#1605;&#1616;
</p>
<p class="c-para" style="text-align:center;font-size:11pt;font-style:italic">
  In the name of Allah, the Most Gracious, the Most Merciful
</p>
<hr class="c-rule"/>
<p class="c-para">The Qur&#8217;anic text used in this workbook is sourced from the Uthmani script
as preserved and transmitted across generations. The Arabic text of the Qur&#8217;an
is in the public domain and belongs to all of humanity.</p>
<p class="c-para">Word-by-word transliterations and English word meanings are sourced from
the Quran Word-by-Word dataset and are used for educational purposes.</p>
<p class="c-para">The workbook layout, design, page structure, typographic system,
and educational framework are original works produced for this edition.</p>
<hr class="c-rule"/>
<p class="c-para" style="font-size:10pt;color:#8b6c14">
  <strong>Educational Use:</strong> This workbook is intended for personal study,
  classroom instruction, and community education. It may be reproduced for
  non-commercial educational purposes with attribution.
</p>
<p class="c-para" style="font-size:10pt;color:#8b6c14">
  <strong>Note on Translation:</strong> English meanings provided are word-level
  approximations to aid learning. For authoritative translation, consult a
  complete Qur&#8217;anic translation reviewed by qualified scholars.
</p>
<div style="flex:1"></div>
<p class="c-para" style="text-align:center;font-size:9.5pt">
  First Edition &nbsp;&middot;&nbsp;
  Typeset in Amiri (Arabic) and EB Garamond (Latin)
</p>
''')
    return page(c, 'COPYRIGHT', 'TRACEABLE QURAN', '', '', '')


def p_how_to_use():
    c = body(f'''
{section("How to Use This Workbook")}
{para("This workbook is designed to make the Qur&#8217;an accessible to every learner — from complete beginners to those with existing Qur&#8217;anic knowledge. Each page follows a consistent three-layer structure that guides you from sound to script to meaning.")}
{section("The Three Layers of Every Word")}
<div class="c-card" style="margin-bottom:3mm">
<div class="c-card-title">① Transliteration (Top)</div>
<div class="c-card-txt">The romanised pronunciation guide. Read this first to learn how the word sounds. Written in italic amber text directly above the Arabic.</div>
</div>
<div class="c-card" style="margin-bottom:3mm">
<div class="c-card-title">② Arabic Tracing Text (Centre)</div>
<div class="c-card-txt">The authentic Qur&#8217;anic Arabic word, printed in light grey. This is the tracing guide. Trace over it with a pen or pencil to build muscle memory for the script.</div>
</div>
<div class="c-card" style="margin-bottom:3mm">
<div class="c-card-title">③ English Meaning (Below)</div>
<div class="c-card-txt">The approximate meaning of that individual word. Note that word meanings in context may differ slightly from literal meanings.</div>
</div>
{section("The Verse Meaning Panel")}
{para("The left column on every page displays the full meaning of each verse that completes on that page. Use this to understand the overall message before tracing individual words.")}
{section("Ayah Markers")}
{para("Each verse ends with the traditional Qur&#8217;anic verse marker &#1757; followed by the verse number in Arabic-Indic numerals. This marks the boundary between verses.")}
{section("Ruku Markers")}
{para("A green &#1593; (Ain) symbol marks the end of each Ruk&#363;&#8216; (section). The number indicates which Ruk&#363;&#8216; within the Juz has been completed.")}
''')
    return page(c, 'HOW TO USE', 'TRACEABLE QURAN', 'FRONT MATTER',
                'How to Use This Workbook', '')

def p_methodology():
    c = body(f'''
{section("Workbook Methodology")}
{para("The Traceable Quran is built on four educational principles that together create an immersive, multi-sensory learning experience.")}
{section("1. Multi-Sensory Engagement")}
{para("Learning is deepened when multiple senses are engaged simultaneously. Tracing the Arabic script activates motor memory. Reading the transliteration engages auditory processing. Connecting words to their meanings engages semantic understanding. All three reinforce one another.")}
{section("2. Word-Level Granularity")}
{para("Rather than presenting verses as undivided units, this workbook breaks each verse into its individual words. This allows the learner to build a genuine vocabulary of Qur&#8217;anic Arabic over time, recognising repeated words across different surahs and contexts.")}
{section("3. Context Preservation")}
{para("While individual words are the study unit, the verse meaning is always displayed in full alongside them. The learner never loses sight of the larger message. This prevents the fragmentation that can occur when words are studied in complete isolation.")}
{section("4. Consistent Repetition")}
{para("The uniform layout on every page — the same three layers, the same left panel, the same header and footer — removes cognitive load. Once the reader learns the page format, they can focus entirely on the content.")}
{rule()}
{note("Recommendation: Work through this workbook at a pace that feels meaningful, not rushed. Ten minutes of attentive tracing each day is more effective than an hour of rushed repetition.")}
''')
    return page(c, 'METHODOLOGY', 'TRACEABLE QURAN', 'FRONT MATTER',
                'Workbook Methodology', '')

def p_transliteration_guide():
    c = body(f'''
{section("Transliteration Guide")}
{para("Transliteration is the process of representing Arabic sounds using Latin letters. The system used in this workbook follows the Qur&#8217;an word-by-word convention. The key principles are:")}
<table class="c-table">
<tr><th>Arabic Letter</th><th>Transliteration</th><th>Approximate English Sound</th></tr>
<tr><td class="ar">ب</td><td><strong>b</strong></td><td>as in <em>book</em></td></tr>
<tr><td class="ar">ت</td><td><strong>t</strong></td><td>as in <em>tea</em></td></tr>
<tr><td class="ar">ث</td><td><strong>th</strong></td><td>as in <em>think</em></td></tr>
<tr><td class="ar">ج</td><td><strong>j</strong></td><td>as in <em>joy</em></td></tr>
<tr><td class="ar">خ</td><td><strong>kh</strong></td><td>guttural, as in Scottish <em>loch</em></td></tr>
<tr><td class="ar">ذ</td><td><strong>dh</strong></td><td>as in <em>this</em></td></tr>
<tr><td class="ar">ش</td><td><strong>sh</strong></td><td>as in <em>ship</em></td></tr>
<tr><td class="ar">ق</td><td><strong>q</strong></td><td>deep guttural k, from throat</td></tr>
<tr><td class="ar">ع</td><td><strong>&#8216;</strong></td><td>voiced pharyngeal — no English equivalent</td></tr>
<tr><td class="ar">ح</td><td><strong>&#7717;</strong></td><td>breathy h, from chest</td></tr>
<tr><td class="ar">ā</td><td><strong>ā</strong></td><td>long a, as in <em>father</em></td></tr>
<tr><td class="ar">ī</td><td><strong>ī</strong></td><td>long i, as in <em>seen</em></td></tr>
<tr><td class="ar">ū</td><td><strong>ū</strong></td><td>long u, as in <em>moon</em></td></tr>
</table>
{rule()}
{note("<strong>Important:</strong> Transliteration is a learning aid, not a substitute for learning the Arabic script and receiving oral instruction from a qualified teacher (Qari). Tajweed rules cannot be fully captured in writing.")}
''')
    return page(c, 'TRANSLITERATION', 'TRACEABLE QURAN', 'FRONT MATTER',
                'Transliteration Guide', '')


def p_symbols():
    c = body(f'''
{section("Symbols &amp; Conventions Used")}
{para("The following symbols appear throughout this workbook. Familiarity with them will make your study sessions more efficient.")}
<table class="c-table">
<tr><th>Symbol</th><th>Name</th><th>Meaning</th></tr>
<tr><td style="font-family:Amiri,serif;font-size:16pt;color:#c9a84c">&#1757;١</td>
    <td>Ra&#8217;s al-Ayah</td>
    <td>End of a verse (Ayah). The Arabic-Indic numeral shows the verse number.</td></tr>
<tr><td style="font-family:Amiri,serif;font-size:16pt;color:#1a7a4a">&#1593;</td>
    <td>Ruk&#363;&#8216; Marker</td>
    <td>End of a Ruk&#363;&#8216; (section). The number below it is the Ruk&#363;&#8216; count within the Juz.</td></tr>
<tr><td style="font-family:Amiri,serif;font-size:11pt;color:#a07830;font-style:italic">bis&#8217;mi</td>
    <td>Transliteration</td>
    <td>Romanised pronunciation guide, shown in amber italic above the Arabic.</td></tr>
<tr><td style="font-family:Amiri,serif;font-size:16pt;color:rgba(0,0,0,.18)">&#1576;&#1616;&#1587;&#1618;&#1605;&#1616;</td>
    <td>Arabic Trace Text</td>
    <td>Light grey Arabic — designed for tracing with a pen or pencil.</td></tr>
<tr><td>&#8230;</td>
    <td>Continuation</td>
    <td>A verse meaning continues from the previous page in the left panel.</td></tr>
<tr><td>&#10059;</td>
    <td>End Ornament</td>
    <td>Marks the end of a Surah on the current page.</td></tr>
</table>
{rule()}
{section("Left Panel Conventions")}
{para("The left panel on every workbook page displays verse meanings. Each entry is numbered with the Arabic-Indic verse number. When a verse meaning is longer than the available panel space, it continues at the top of the next page's panel, marked with &#8230;.")}
{note("Arabic-Indic numerals are used throughout: &#1633;&#1634;&#1635;&#1636;&#1637; = 1 2 3 4 5 &nbsp; &#1638;&#1639;&#1640;&#1641;&#1632; = 6 7 8 9 0")}
''')
    return page(c, 'SYMBOLS', 'TRACEABLE QURAN', 'FRONT MATTER',
                'Symbols &amp; Conventions', '')

def p_learning_roadmap():
    c = body(f'''
{section("Suggested Learning Roadmap")}
{para("This workbook can be used at any pace. The following roadmap is a suggested approach for learners who wish to work through the complete Qur&#8217;an systematically.")}
<table class="c-table">
<tr><th>Phase</th><th>Focus</th><th>Suggested Duration</th></tr>
<tr><td><strong>Phase 1</strong></td><td>Juz 30 — short surahs, familiar vocabulary</td><td>4–6 weeks</td></tr>
<tr><td><strong>Phase 2</strong></td><td>Juz 29 &amp; 28 — continue building vocabulary</td><td>4–6 weeks</td></tr>
<tr><td><strong>Phase 3</strong></td><td>Juz 1 (Al-Fatiha &amp; Al-Baqarah)</td><td>6–8 weeks</td></tr>
<tr><td><strong>Phase 4</strong></td><td>Juz 2–5 — continue Al-Baqarah &amp; early Surahs</td><td>3–4 months</td></tr>
<tr><td><strong>Phase 5</strong></td><td>Remaining Juz in sequence</td><td>1–2 years</td></tr>
</table>
{section("Daily Study Session")}
{ol([
    "Begin with Isti&#8216;adhah (seeking refuge in Allah from Shaytan) and Bismillah.",
    "Review the previous session&#8217;s words — check you still remember them.",
    "Trace each new word three times: once following the guide, twice from memory.",
    "Read the transliteration aloud as you trace.",
    "Read the verse meaning in the left panel before and after tracing.",
    "Close the session with Du&#8216;a for beneficial knowledge."
])}
{rule()}
{note("Consistency is more valuable than intensity. Five minutes daily, every day, is far more effective than one long session per week.")}
''')
    return page(c, 'LEARNING ROADMAP', 'TRACEABLE QURAN', 'FRONT MATTER',
                'Learning Roadmap', '')

def p_quran_structure():
    c = body(f'''
{section("The Structure of the Qur&#8217;an")}
{para("The Qur&#8217;an (Arabic: &#1575;&#1604;&#1602;&#1615;&#1585;&#1618;&#1570;&#1606;) is the central religious text of Islam, believed by Muslims to be the word of Allah as revealed to the Prophet Muhammad &#65018; over approximately 23 years.")}
<div class="c-col2">
<div class="c-card"><div class="c-card-title">Surahs (Chapters)</div>
<div class="c-card-txt">114 chapters of varying length. Each has a name, a classification (Makki or Madani), and a fixed number of verses.</div></div>
<div class="c-card"><div class="c-card-title">Ayat (Verses)</div>
<div class="c-card-txt">6,236 verses in total. Each verse is a unit of revelation, ending with the Ra&#8217;s al-Ayah marker.</div></div>
<div class="c-card"><div class="c-card-title">Juz / Para (Sections)</div>
<div class="c-card-txt">The Qur&#8217;an is divided into 30 equal parts (Juz) to facilitate completion in 30 days, one Juz per day.</div></div>
<div class="c-card"><div class="c-card-title">Ruk&#363;&#8216; (Sections)</div>
<div class="c-card-txt">Each Juz is further divided into Ruk&#363;&#8216; — thematic or recitational sections. Juz 1 has 17 Ruk&#363;&#8216;.</div></div>
<div class="c-card"><div class="c-card-title">Hizb &amp; Manzil</div>
<div class="c-card-txt">Alternative divisions: 60 Ahzab (groups of 8 pages), and 7 Manazil for weekly completion.</div></div>
<div class="c-card"><div class="c-card-title">Makki &amp; Madani</div>
<div class="c-card-txt">Verses revealed in Makkah before Hijrah (Makki) tend to focus on faith and theology. Verses revealed in Madinah (Madani) tend to address law and community life.</div></div>
</div>
{rule()}
<p class="c-para" style="font-size:10pt;text-align:center;color:#8b6c14">
Total words: approximately 77,429 &nbsp;&middot;&nbsp;
Total letters: approximately 323,015
</p>
''')
    return page(c, 'QURAN STRUCTURE', 'TRACEABLE QURAN', 'FRONT MATTER',
                'Qur&#8217;an Structure Overview', '')


def p_juz_index():
    rows=''
    for j in range(1,31):
        surahs=[]; vm=JUZ_MAP[j]
        for ch,rng in vm.items():
            a,b=rng.split('-')
            name=CH[ch]['name_en']
            surahs.append(f"{name} ({a}&ndash;{b})")
        rows+=(f'<tr><td><strong>{j}</strong></td>'
               f'<td class="ar">&#1575;&#1604;&#1580;&#1586;&#1569; {j}</td>'
               f'<td>{" &nbsp;|&nbsp; ".join(surahs)}</td>'
               f'<td><a href="Juz-{j:02d}.html">Juz-{j:02d}.html</a></td></tr>')
    c = body(f'''
{section("Juz Index")}
{para("The Qur&#8217;an is divided into 30 Juz (Para). Each Juz in this workbook is a separate downloadable and printable file.")}
<table class="idx-table">
<tr><th>#</th><th>Arabic</th><th>Surahs Covered</th><th>File</th></tr>
{rows}
</table>''')
    return page(c, 'JUZ INDEX', 'TRACEABLE QURAN', 'FRONT MATTER',
                'Juz Index', '')

def p_surah_index_1():
    rows=''
    for ch in range(1,58):
        m=CH[str(ch)]
        rows+=(f'<tr><td>{ch}</td>'
               f'<td class="ar">{m["name_ar"]}</td>'
               f'<td>{m["name_en"]}</td>'
               f'<td>{m["meaning"]}</td>'
               f'<td>{m["revealed"]}</td>'
               f'<td>{m["verses"]}</td></tr>')
    c = body(f'''
{section("Surah Index (1–57)")}
<table class="idx-table">
<tr><th>#</th><th>Arabic</th><th>Name</th><th>Meaning</th><th>Type</th><th>Verses</th></tr>
{rows}
</table>''')
    return page(c, 'SURAH INDEX', 'TRACEABLE QURAN', 'FRONT MATTER',
                'Surah Index (1–57)', '')

def p_surah_index_2():
    rows=''
    for ch in range(58,115):
        m=CH[str(ch)]
        rows+=(f'<tr><td>{ch}</td>'
               f'<td class="ar">{m["name_ar"]}</td>'
               f'<td>{m["name_en"]}</td>'
               f'<td>{m["meaning"]}</td>'
               f'<td>{m["revealed"]}</td>'
               f'<td>{m["verses"]}</td></tr>')
    c = body(f'''
{section("Surah Index (58–114)")}
<table class="idx-table">
<tr><th>#</th><th>Arabic</th><th>Name</th><th>Meaning</th><th>Type</th><th>Verses</th></tr>
{rows}
</table>''')
    return page(c, 'SURAH INDEX', 'TRACEABLE QURAN', 'FRONT MATTER',
                'Surah Index (58–114)', '')


def p_introduction():
    c = body(f'''
{section("Introduction to the Qur&#8217;an")}
{para("The Qur&#8217;an is the sacred scripture of Islam. Muslims believe it is the literal word of Allah (God), revealed in the Arabic language to the Prophet Muhammad &#65018; through the angel Jibr&#299;l (Gabriel) over a period of approximately 23 years — from 610 CE until the Prophet&#8217;s passing in 632 CE.")}
{para("The name <em>Qur&#8217;an</em> (&#1575;&#1604;&#1602;&#1615;&#1585;&#1618;&#1570;&#1606;) derives from the Arabic root meaning &#8220;to recite&#8221; or &#8220;to read.&#8221; It is also known as Al-Furqan (the Criterion), Al-Kitab (the Book), and Al-Dhikr (the Reminder).")}
{section("Preservation")}
{para("From the moment of its revelation, the Qur&#8217;an was both memorised by the Companions and written down. The standardised written text was compiled under the Caliph &#8216;Uthm&#257;n ibn &#8216;Aff&#257;n, and the same text — letter for letter — is recited and preserved across the Muslim world to this day. This continuity of preservation is regarded by Muslims as a divine promise, referenced in Qur&#8217;an 15:9.")}
{section("The Language")}
{para("The Qur&#8217;an was revealed in Classical Arabic — a language of remarkable precision and expressiveness. The Arabic of the Qur&#8217;an is considered by Muslims to be at the highest level of eloquence, and its literary style is held to be inimitable (I&#8216;jaz al-Qur&#8217;an).")}
{section("Its Role in Muslim Life")}
{para("The Qur&#8217;an is recited in the five daily prayers, studied throughout life, memorised in its entirety by millions of people (who are honoured with the title <em>Hafiz</em>), and consulted as the primary source of Islamic guidance.")}
{rule()}
{note("This workbook does not attempt to replace complete Qur&#8217;anic translation or scholarly tafsir (exegesis). It is a learning aid for building connection with the Arabic text. For deep understanding, consult qualified Islamic scholars and authoritative translations.")}
''')
    return page(c, 'INTRODUCTION', 'TRACEABLE QURAN', 'FRONT MATTER',
                "Introduction to the Quran", "")

def p_virtues():
    c = body(f'''
{section("Virtues of Learning the Qur&#8217;an")}
{para("The Prophet Muhammad &#65018; frequently encouraged his Companions and followers to learn, recite, and teach the Qur&#8217;an. The following are among the most well-known and authentic narrations on this subject.")}
{hadith("خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ",
        "The best among you is the one who learns the Qur&#8217;an and teaches it.",
        "Sahih Al-Bukhari, No. 5027")}
{hadith("اقْرَؤُوا الْقُرْآنَ فَإِنَّهُ يَأْتِي يَوْمَ الْقِيَامَةِ شَفِيعًا لِأَصْحَابِهِ",
        "Recite the Qur&#8217;an, for it will come as an intercessor for its companions on the Day of Resurrection.",
        "Sahih Muslim, No. 804")}
{hadith("الَّذِي يَقْرَأُ الْقُرْآنَ وَهُوَ مَاهِرٌ بِهِ مَعَ السَّفَرَةِ الْكِرَامِ الْبَرَرَةِ",
        "The one who is proficient with the Qur&#8217;an will be with the noble, righteous scribes (angels).",
        "Sahih Al-Bukhari and Sahih Muslim")}
{hadith("مَثَلُ الْمُؤْمِنِ الَّذِي يَقْرَأُ الْقُرْآنَ كَمَثَلِ الأُتْرُجَّةِ طَعْمُهَا طَيِّبٌ وَرِيحُهَا طَيِّبٌ",
        "The example of a believer who recites the Qur&#8217;an is like a citrus fruit — its taste is good and its fragrance is good.",
        "Sahih Al-Bukhari, No. 5427")}
{rule()}
{note("Every letter of the Qur&#8217;an that is recited earns reward. The Prophet &#65018; said: &#8220;I do not say that Alif-Lam-Mim is one letter, rather Alif is a letter, Lam is a letter, and Mim is a letter.&#8221; (Al-Tirmidhi, Hasan)")}
''')
    return page(c, 'VIRTUES', 'TRACEABLE QURAN', 'FRONT MATTER',
                "Virtues of Learning the Quran", "")

def p_etiquettes():
    c = body(f'''
{section("Etiquettes of Qur&#8217;an Study")}
{para("Islamic scholarship has outlined a set of etiquettes (Adab) for engaging with the Qur&#8217;an. Observing these deepens the quality and blessing of one&#8217;s study.")}
{section("Before Beginning")}
{ul(["Be in a state of ritual purity (Wudu) when possible, especially when handling or touching the Mushaf.",
     "Begin with Isti&#8216;adhah: <em>A&#8216;&#363;dhu billahi min al-shaytan il-rajim</em> (I seek refuge in Allah from the accursed devil).",
     "Then recite Bismillah: <em>Bismillah ir-Rahman ir-Rahim</em>.",
     "Sit respectfully, with sincerity and focus. Face the Qiblah if possible.",
     "Set a clear intention (Niyyah) for your study session."])}
{section("During Study")}
{ul(["Recite or read slowly and reflectively (Tartil). Do not rush through the words.",
     "When you encounter a verse of mercy, pause and ask Allah for His mercy.",
     "When you encounter a verse of warning, pause and seek Allah&#8217;s protection.",
     "Treat the words with reverence — they are the speech of Allah.",
     "Keep the study space clean and free from distractions."])}
{section("After Study")}
{ul(["Thank Allah for the ability and opportunity to engage with His words.",
     "Make du&#8216;a for understanding, guidance, and the ability to act upon what you have learned.",
     "Teach others what you have learned, even a single verse."])}
{rule()}
{note("These etiquettes are recommendations from the scholarly tradition, not mandatory requirements. The most important etiquette is a sincere heart and genuine intention to seek guidance.")}
''')
    return page(c, 'ETIQUETTES', 'TRACEABLE QURAN', 'FRONT MATTER',
                "Etiquettes of Quran Study", "")

def p_preface():
    c = body(f'''
<div style="height:8mm"></div>
<div class="c-title" style="font-size:22pt">Preface</div>
<div class="c-ornament">&#10022; &#10022; &#10022;</div>
<div style="height:4mm"></div>
{para("This workbook began as a simple question: <em>What would it look like if a Qur&#8217;an learner could trace every single Arabic word, read its pronunciation, understand its meaning &mdash; and do all of this on the same page, in the same breath?</em>")}
{para("The Qur&#8217;an has been taught, memorised, and transmitted for over fourteen centuries. Millions of people around the world learn it through oral transmission &mdash; teacher to student, voice to voice. That tradition is irreplaceable. But many learners also benefit from the act of writing: the pen as a tool of attention, the hand as a path to the heart.")}
{para("This workbook is for those learners. It is for the child beginning their Qur&#8217;anic journey. It is for the adult who can recite but wants to connect with the meaning. It is for the elderly reader approaching the text with patience and dedication. It is for every person who has ever wanted to feel closer to the words of Allah through the act of writing them.")}
{para("The design principle throughout has been: <em>the Qur&#8217;an first, always.</em> Every layout decision &mdash; the size of the Arabic text, the width of the panels, the spacing between words &mdash; was made in service of the sacred text, not in spite of it.")}
{para("May Allah accept this effort, forgive its shortcomings, and make it a means of benefit for every person who opens its pages.")}
<div style="margin-top:6mm;text-align:right;font-style:italic;font-size:11pt;color:#8b6c14">
  <em>Wa billahi al-tawfiq</em><br/>And with Allah is all success.
</div>
''')
    return page(c, 'PREFACE', 'TRACEABLE QURAN', 'FRONT MATTER', 'Preface', '')


def p_about_arabic_text():
    c = body(f'''
<div class="c-title" style="font-size:20pt;margin-bottom:2mm">About the Arabic Text</div>
<div class="c-ornament">&#10022; &#10022; &#10022;</div>
<div style="height:3mm"></div>

{section("Script &amp; Narration")}
{para("The Arabic text in this workbook follows the <strong>Uthmani script (Rasm Uthmani)</strong> in the narration of <strong>Hafs &#8216;an &#8216;Asim</strong> — the most widely read transmission of the Qur&#8217;an in the world, used by over 95% of Muslims globally.")}
<div class="c-col2">
<div class="c-card">
<div class="c-card-title">Uthmani Script</div>
<div class="c-card-txt">The standardised written form of the Qur&#8217;an, established under the third Caliph &#8216;Uthm&#257;n ibn &#8216;Aff&#257;n (r.a.) approximately 650 CE. This orthography is the global standard for all printed Qurans today.</div>
</div>
<div class="c-card">
<div class="c-card-title">Hafs &#8216;an &#8216;Asim</div>
<div class="c-card-txt">One of the ten recognised Quranic narrations (Riwayat). It travels from the Prophet &#65018; through &#8216;Ali, &#8216;Asim al-Kufi, and Hafs. This narration is the basis for Qurans printed in Egypt, Saudi Arabia, the Subcontinent, and most of the world.</div>
</div>
</div>

{section("Harakat (Diacritics)")}
{para("The Arabic text includes <strong>full harakat</strong> — all diacritical marks (zabar/fatha, zer/kasra, pesh/damma, sukun, shadda, tanwin) — enabling correct recitation without prior knowledge of classical Arabic morphology.")}

{section("Arabic Font: Amiri")}
<div class="c-card" style="margin-bottom:3mm">
<div class="c-card-title">Font Name: Amiri &nbsp;&nbsp; Designer: Khaled Hosny</div>
<div class="c-card-txt">An open-source Arabic typeface based on the <em>Bulaq Press</em> tradition — the same typographic lineage used in Egyptian Royal Press Quran printing since the 19th century. Amiri renders all Quranic ligatures, diacritics, and special characters with precision. It is used extensively in academic and scholarly Arabic publishing.</div>
</div>
<div class="c-col2">
<div class="c-card">
<div class="c-card-title">Style</div>
<div class="c-card-txt">Traditional Naskh — the standard calligraphic hand for Quran printing in the Arab world. Clear, readable, and historically rooted.</div>
</div>
<div class="c-card">
<div class="c-card-title">License</div>
<div class="c-card-txt">SIL Open Font License. Fully free and open source. No copyright restrictions on use in published works.</div>
</div>
</div>

{section("Source")}
{para("Arabic text is sourced from the <strong>quran.com word-by-word dataset</strong>, which maintains the Uthmani script digitally and is used by millions of learners and applications worldwide.")}

{rule()}
{note("<strong>Language:</strong> The Qur&#8217;an is in Classical Arabic (Al-Fus&#7717;a) — not a spoken dialect. It represents the highest literary register of the Arabic language and is considered by Muslims to be inimitable in its eloquence (I&#8216;j&#257;z al-Qur&#8217;an).")}
''')
    return page(c, 'ABOUT THE ARABIC TEXT', 'TRACEABLE QURAN', 'FRONT MATTER',
                'About the Arabic Text', '')


def p_about_translation():
    c = body(f'''
<div class="c-title" style="font-size:20pt;margin-bottom:2mm">About the Translation &amp; Meanings</div>
<div class="c-ornament">&#10022; &#10022; &#10022;</div>
<div style="height:3mm"></div>

{section("Verse Meanings — Saheeh International")}
<div class="c-card" style="margin-bottom:4mm">
<div class="c-card-title">Translation: Saheeh International</div>
<div class="c-card-txt">Published 1997, revised 2004. Abul Qasim Publishing House, Jeddah, Saudi Arabia.<br/>
Produced by a team of scholars including Mary Umm Muhammad, Amatullah Bantley, and Umm Muhammad.<br/><br/>
<strong>Philosophy:</strong> Meaning-based translation. Aims for precision and clarity in Modern English while maintaining complete fidelity to the Arabic. Avoids archaic language. Widely used by Islamic universities, scholars, and research institutions worldwide.</div>
</div>
{note("Verse meanings shown in the left panel of each workbook page are drawn from the Saheeh International translation. They are displayed to provide overall verse context — always consult the complete authorised text and qualified scholars for matters of Islamic guidance.")}

{section("Word-by-Word Meanings")}
{para("Individual word meanings for each Arabic word are drawn from the <strong>quran.com word-by-word database</strong>, itself grounded in the classical Qur&#8217;anic lexicographic tradition:")}
<table class="c-table">
<tr><th>Reference Work</th><th>Author</th><th>Era</th></tr>
<tr><td><em>Lis&#257;n al-&#8216;Arab</em></td><td>Ibn Manz&#363;r</td><td>711 AH / 1290 CE</td></tr>
<tr><td><em>Al-Mufrad&#257;t f&#299; Ghar&#299;b al-Qur&#8217;an</em></td><td>Al-R&#257;ghib al-Isf&#257;h&#257;n&#299;</td><td>d. 502 AH / 1108 CE</td></tr>
<tr><td><em>T&#257;j al-&#8216;Ar&#363;s</em></td><td>Al-Zab&#299;d&#299;</td><td>1205 AH / 1790 CE</td></tr>
<tr><td><em>Al-Qam&#363;s al-Mu&#7717;&#299;&#7789;</em></td><td>Al-F&#299;r&#363;z&#257;b&#257;d&#299;</td><td>d. 817 AH / 1414 CE</td></tr>
</table>

{section("Transliteration System")}
{para("Transliteration follows a <strong>modified academic romanisation</strong> as used by the quran.com platform — a learner-accessible adaptation of standard Arabic romanisation conventions.")}
<div class="c-col2">
<div class="c-card">
<div class="c-card-title">Long vowels</div>
<div class="c-card-txt">&#257; (alif madd) &nbsp; &#299; (ya madd) &nbsp; &#363; (waw madd)</div>
</div>
<div class="c-card">
<div class="c-card-title">Emphatic / Pharyngeal</div>
<div class="c-card-txt">&#7717; (ha) &nbsp; &#7779; (sad) &nbsp; &#7693; (dad) &nbsp; &#7789; (ta) &nbsp; &#7827; (za) &nbsp; &#8216; (ain)</div>
</div>
</div>
{note("<strong>Important:</strong> Transliteration cannot fully represent Tajweed rules (idgh&#257;m, ikhf&#257;&#8217;, madd, etc.). It is a learning aid only. For correct recitation, oral instruction from a qualified Q&#257;ri&#8217; is essential.")}

{section("Latin Font: EB Garamond")}
{para("All Latin text — transliterations, meanings, headers, and panels — is set in <strong>EB Garamond</strong>, a digital revival by Georg Duffner of the 16th-century typefaces of Claude Garamond. SIL Open Font License.")}

{rule()}
{para("For deeper study, the following are recommended alongside this workbook:")}
{ul(["<em>Tafsir Ibn Kathir</em> — classical verse-by-verse commentary (English available)",
     "<em>Tafh&#299;m al-Qur&#8217;an</em> — Mawdudi (accessible modern commentary)",
     "King Fahd Quran Complex (qurancomplex.gov.sa) — official Medina Mushaf source",
     "<em>An Introduction to the Sciences of the Qur&#8217;an</em> — Yasir Qadhi"])}
''')
    return page(c, 'ABOUT THE TRANSLATION', 'TRACEABLE QURAN', 'FRONT MATTER',
                'About the Translation &amp; Meanings', '')
    c = body(f'''
<div style="height:8mm"></div>
<div class="c-title" style="font-size:22pt">Preface</div>
<div class="c-ornament">&#10022; &#10022; &#10022;</div>
<div style="height:4mm"></div>
{para("This workbook began as a simple question: <em>What would it look like if a Qur&#8217;an learner could trace every single Arabic word, read its pronunciation, understand its meaning — and do all of this on the same page, in the same breath?</em>")}
{para("The Qur&#8217;an has been taught, memorised, and transmitted for over fourteen centuries. Millions of people around the world learn it through oral transmission — teacher to student, voice to voice. That tradition is irreplaceable. But many learners also benefit from the act of writing: the pen as a tool of attention, the hand as a path to the heart.")}
{para("This workbook is for those learners. It is for the child beginning their Qur&#8217;anic journey. It is for the adult who can recite but wants to connect with the meaning. It is for the elderly reader approaching the text with patience and dedication. It is for every person who has ever wanted to feel closer to the words of Allah through the act of writing them.")}
{para("The design principle throughout has been: <em>the Qur&#8217;an first, always.</em> Every layout decision — the size of the Arabic text, the width of the panels, the spacing between words — was made in service of the sacred text, not in spite of it.")}
{para("May Allah accept this effort, forgive its shortcomings, and make it a means of benefit for every person who opens its pages.")}
<div style="margin-top:6mm;text-align:right;font-style:italic;font-size:11pt;color:#8b6c14">
  <em>Wa billahi al-tawfiq</em><br/>And with Allah is all success.
</div>
''')
    return page(c, 'PREFACE', 'TRACEABLE QURAN', 'FRONT MATTER', 'Preface', '')


# ═══════════════════════════════════════════════════════════
# BACK MATTER PAGES
# ═══════════════════════════════════════════════════════════

def p_khatm():
    c = '''<div class="khatm-body">
<div class="c-ornament" style="font-size:24pt">&#10022; &#10022; &#10022;</div>
<div class="khatm-ar">&#1578;&#1614;&#1605;&#1617; &#1576;&#1616;&#1581;&#1614;&#1605;&#1618;&#1583;&#1616; &#1575;&#1604;&#1604;&#1614;&#1617;&#1607;&#1616;</div>
<div class="c-rule" style="width:60%;margin:4mm auto"></div>
<div class="khatm-msg">
  Congratulations on completing your reading of the Noble Qur&#8217;an.<br/><br/>
  May Allah accept your effort, bless your time, and make the Qur&#8217;an
  a light for your path, a companion in your solitude,
  and an intercessor on the Day when intercession will matter most.
</div>
<div class="c-ornament" style="font-size:20pt">&#10022; &#10022; &#10022;</div>
<div class="khatm-date">
  Date of Completion: ___________________
</div>
<div style="height:4mm"></div>
<div class="khatm-date">
  Witness: ___________________
</div>
</div>'''
    return page(c, 'KHATM UL-QURAN', 'TRACEABLE QURAN', 'BACK MATTER',
                "Completion of the Quran", "")

def p_dua_khatm():
    c = body(f'''
{section("Du&#8216;a After Completing the Qur&#8217;an")}
{para("It is a beloved tradition to make du&#8216;a (supplication) upon completing a reading of the Qur&#8217;an. The following is a well-known supplication drawing upon Qur&#8217;anic phrases and the spirit of the completion.")}
{rule()}
<div class="c-hadith">
<div class="c-arabic-hadith" style="font-size:18pt;line-height:1.7">
&#1575;&#1604;&#1604;&#1617;&#1614;&#1607;&#1615;&#1605;&#1617; &#1575;&#1585;&#1618;&#1581;&#1614;&#1605;&#1618;&#1606;&#1616;&#1610; &#1576;&#1616;&#1575;&#1604;&#1618;&#1602;&#1615;&#1585;&#1618;&#1570;&#1606;&#1616; &#1575;&#1604;&#1618;&#1593;&#1614;&#1592;&#1616;&#1610;&#1605;&#1616;&#8203;،
&#1608;&#1575;&#1580;&#1618;&#1593;&#1614;&#1604;&#1618;&#1607;&#1615; &#1604;&#1616;&#1610; &#1573;&#1616;&#1605;&#1614;&#1575;&#1605;&#1611;&#1575; &#1608;&#1606;&#1615;&#1608;&#1585;&#1611;&#1575; &#1608;&#1607;&#1615;&#1583;&#1611;&#1609; &#1608;&#1585;&#1614;&#1581;&#1618;&#1605;&#1614;&#1577;&#8203;.
</div>
<p class="c-para" style="font-style:italic">
O Allah, have mercy on me through the Great Qur&#8217;an,
and make it for me a guide, a light, a direction, and a mercy.
</p>
</div>
<div class="c-hadith">
<div class="c-arabic-hadith" style="font-size:18pt;line-height:1.7">
&#1575;&#1604;&#1604;&#1617;&#1614;&#1607;&#1615;&#1605;&#1617; &#1593;&#1604;&#1617;&#1616;&#1605;&#1618;&#1606;&#1616;&#1610; &#1605;&#1616;&#1606;&#1618;&#1607;&#1615; &#1605;&#1614;&#1575; &#1580;&#1614;&#1607;&#1616;&#1604;&#1618;&#1578;&#1615;&#8203;،
&#1608;&#1584;&#1614;&#1603;&#1617;&#1616;&#1585;&#1618;&#1606;&#1616;&#1610; &#1605;&#1616;&#1606;&#1618;&#1607;&#1615; &#1605;&#1614;&#1575; &#1606;&#1614;&#1587;&#1616;&#1610;&#1578;&#1615;&#8203;.
</div>
<p class="c-para" style="font-style:italic">
O Allah, teach me from it what I do not know,
and remind me through it of what I have forgotten.
</p>
</div>
{rule()}
{note("These are personal supplications, not narrated du&#8216;as with specific attribution. They draw on the style of Prophetic supplication and Qur&#8217;anic language. Feel free to add your own heartfelt du&#8216;a in your own words — Allah hears every tongue.")}
''')
    return page(c, 'DU&#8216;A KHATM', 'TRACEABLE QURAN', 'BACK MATTER',
                "Du&#8216;a After Completing the Quran", "")

def p_reflection():
    c = body(f'''
{section("Reflection on the Qur&#8217;an Journey")}
{para("Completing a reading or study of the Qur&#8217;an is a significant milestone. Before you close this workbook, take a moment to reflect.")}
{rule()}
<div class="c-card" style="margin-bottom:4mm">
<div class="c-card-title">Which verse touched you most deeply?</div>
<div class="c-card-txt">
&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;<br/>
&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;
</div></div>
<div class="c-card" style="margin-bottom:4mm">
<div class="c-card-title">What did you learn about yourself during this journey?</div>
<div class="c-card-txt">
&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;<br/>
&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;
</div></div>
<div class="c-card" style="margin-bottom:4mm">
<div class="c-card-title">One Qur&#8217;anic lesson I want to carry forward:</div>
<div class="c-card-txt">
&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;<br/>
&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;
</div></div>
<div class="c-card" style="margin-bottom:4mm">
<div class="c-card-title">My next goal with the Qur&#8217;an:</div>
<div class="c-card-txt">
&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;<br/>
&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;&#8212;
</div></div>
{rule()}
{hadith("وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِرٍ",
        "And We have certainly made the Qur'an easy for remembrance, so is there any who will remember?",
        "Quran 54:17")}
''')
    return page(c, 'REFLECTION', 'TRACEABLE QURAN', 'BACK MATTER',
                'Reflection on the Journey', '')

def p_about_workbook():
    c = body(f'''
{section("About This Workbook")}
{para("The Traceable Quran is a word-by-word learning and tracing workbook covering the complete text of the Noble Qur&#8217;an.")}
<table class="c-table">
<tr><th>Property</th><th>Detail</th></tr>
<tr><td>Format</td><td>A4 print-ready HTML, 30 separate Juz files</td></tr>
<tr><td>Arabic Text</td><td>Uthmani script with full harakat (diacritics)</td></tr>
<tr><td>Transliteration</td><td>Word-by-word romanisation (quran.com convention)</td></tr>
<tr><td>Word Meanings</td><td>Word-by-word English meanings</td></tr>
<tr><td>Verse Meanings</td><td>Sahih International English translation (word-count: ~150,000)</td></tr>
<tr><td>Surahs</td><td>All 114 Surahs</td></tr>
<tr><td>Juz</td><td>All 30 Juz</td></tr>
<tr><td>Verses</td><td>6,236 Ayat</td></tr>
<tr><td>Arabic Words</td><td>77,429 (with individual tracing cells)</td></tr>
<tr><td>Ruku Markers</td><td>All Ruk&#363;&#8216; endings marked in every Juz</td></tr>
<tr><td>Arabic Font</td><td>Amiri (Open Source, SIL Open Font License)</td></tr>
<tr><td>Latin Font</td><td>EB Garamond (Open Source, SIL Open Font License)</td></tr>
<tr><td>Offline capable</td><td>Yes — fonts embedded in every file</td></tr>
<tr><td>Print specification</td><td>A4, no margins, background graphics enabled</td></tr>
</table>
{rule()}
{section("Technical Notes")}
{ul(["Arabic text is rendered using CSS flex layout with direction:rtl and white-space:nowrap.",
     "Verse meanings flow across pages when too long for a single panel.",
     "Page pagination is pre-computed — no row or word is ever split across a page break.",
     "All 30 Juz files have been validated for content integrity, encoding accuracy, and layout overflow."])}
''')
    return page(c, 'ABOUT', 'TRACEABLE QURAN', 'BACK MATTER',
                'About This Workbook', '')

def p_final_message():
    c = body(f'''
<div style="height:16mm"></div>
<div class="c-arabic-main">&#1585;&#1614;&#1576;&#1617;&#1616; &#1586;&#1616;&#1583;&#1618;&#1606;&#1616;&#1610; &#1593;&#1616;&#1604;&#1618;&#1605;&#1611;&#1575;</div>
<div class="c-subtitle">&#8220;My Lord, increase me in knowledge.&#8221; &nbsp; (Qur&#8217;an 20:114)</div>
<hr class="c-rule"/>
<div style="height:6mm"></div>
{para("The journey through the Qur&#8217;an does not end — it deepens. Each reading reveals something the previous reading did not. Each year of life brings a new lens. Each difficulty you carry to the Qur&#8217;an will be met with words that seem written for that very moment.")}
{para("The scholars of Islam say: <em>The Qur&#8217;an does not grow old with repetition.</em> Its freshness is preserved across centuries and lifetimes, across languages and cultures.")}
{para("You have now traced the words of Allah with your hand, sounded them with your lips, and carried them in your mind. That effort — however imperfect, however slow — is recorded.")}
<div class="c-hadith">
<p class="c-para" style="font-style:italic;text-align:center;font-size:13pt">
&#8220;Verily the deeds are according to intentions,<br/>
and every person will have what they intended.&#8221;
</p>
<span class="c-hadith-src" style="text-align:center;display:block">&mdash; Sahih Al-Bukhari, No. 1; Sahih Muslim, No. 1907</span>
</div>
<div style="height:8mm"></div>
<div class="c-ornament" style="font-size:20pt">&#10022; &#10022; &#10022;</div>
<p class="c-para" style="text-align:center;font-size:13pt;margin-top:4mm">
  May Allah make the Qur&#8217;an the light of your heart,<br/>
  the rest of your chest, and the remover of your grief.<br/>
  <em>Ameen.</em>
</p>
''')
    return page(c, 'CLOSING', 'TRACEABLE QURAN', 'BACK MATTER',
                'Final Message', '')


# ═══════════════════════════════════════════════════════════
# ASSEMBLE & WRITE
# ═══════════════════════════════════════════════════════════

def build_html(pages_list, title):
    body_pages = '\n\n'.join(pages_list)
    import build_all as _B
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>'
            f'<meta name="viewport" content="width=device-width,initial-scale=1.0"/>'
            f'<title>{title}</title>'
            f'{fonts_block()}<style>{CSS}{_B.EDITOR_CSS}</style></head><body>'
            f'{_B.EDITOR_BAR}{body_pages}{_B.EDITOR_JS}</body></html>')

def main():
    # ── FRONT MATTER ──────────────────────────────────────
    front = [
        p_cover(),
        p_title(),
        p_copyright(),
        p_preface(),
        p_how_to_use(),
        p_methodology(),
        p_transliteration_guide(),
        p_symbols(),
        p_learning_roadmap(),
        p_quran_structure(),
        p_about_arabic_text(),
        p_about_translation(),
        p_juz_index(),
        p_surah_index_1(),
        p_surah_index_2(),
        p_introduction(),
        p_virtues(),
        p_etiquettes(),
    ]
    fm_out = OUTDIR / 'Front-Matter.html'
    fm_out.write_text(build_html(front, 'Traceable Quran — Front Matter'),
                      encoding='utf-8')
    print(f'Written {fm_out.name}: {len(front)} pages, {fm_out.stat().st_size//1024} KB')

    # ── BACK MATTER ───────────────────────────────────────
    back = [
        p_khatm(),
        p_dua_khatm(),
        p_reflection(),
        p_about_workbook(),
        p_final_message(),
    ]
    bm_out = OUTDIR / 'Back-Matter.html'
    bm_out.write_text(build_html(back, 'Traceable Quran — Back Matter'),
                      encoding='utf-8')
    print(f'Written {bm_out.name}: {len(back)} pages, {bm_out.stat().st_size//1024} KB')

if __name__ == '__main__':
    main()
