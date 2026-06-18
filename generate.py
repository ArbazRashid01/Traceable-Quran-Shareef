#!/usr/bin/env python3
"""Traceable Quran — 5-Page Preview Generator
Layout: Per-verse synchronized sections + inline Quranic Ayah markers
"""

# ── ARABIC-INDIC NUMERAL CONVERTER ────────────────────────────────────────
_AR = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
def ar(n): return str(n).translate(_AR)

# ── WORD DATA: (arabic, transliteration, english) ────────────────────────
WORDS = {
    '1:1': [('بِسْمِ',"bis'mi",'In the name'),
            ('ٱللَّهِ','l-lahi','of Allah'),
            ('ٱلرَّحْمَـٰنِ','l-raḥmāni','the Most Gracious'),
            ('ٱلرَّحِيمِ','l-raḥīmi','the Most Merciful')],
    '1:2': [('ٱلْحَمْدُ','al-ḥamdu','All praise'),
            ('لِلَّهِ','lillahi','be to Allah'),
            ('رَبِّ','rabbi','the Lord'),
            ('ٱلْعَـٰلَمِينَ',"l-'ālamīna",'of all the worlds')],
    '1:3': [('ٱلرَّحْمَـٰنِ','al-raḥmāni','The Most Gracious'),
            ('ٱلرَّحِيمِ','l-raḥīmi','the Most Merciful')],
    '1:4': [('مَـٰلِكِ','māliki','Master'),
            ('يَوْمِ','yawmi','of the Day'),
            ('ٱلدِّينِ','l-dīni','of Judgment')],
    '1:5': [('إِيَّاكَ','iyyāka','You alone'),
            ('نَعْبُدُ',"na'budu",'we worship'),
            ('وَإِيَّاكَ','wa-iyyāka','and You alone'),
            ('نَسْتَعِينُ',"nasta'īnu",'we ask for help')],
    '1:6': [('ٱهْدِنَا',"ih'dinā",'Guide us'),
            ('ٱلصِّرَٰطَ','l-ṣirāṭa','to the path'),
            ('ٱلْمُسْتَقِيمَ',"l-mus'taqīma",'the straight')],
    '1:7': [('صِرَٰطَ','ṣirāṭa','The path'),
            ('ٱلَّذِينَ','alladhīna','of those'),
            ('أَنْعَمْتَ',"an'amta",'You bestowed favour'),
            ('عَلَيْهِمْ',"'alayhim",'on them'),
            ('غَيْرِ','ghayri','not of'),
            ('ٱلْمَغْضُوبِ','l-maghḍūbi','who earned wrath'),
            ('عَلَيْهِمْ',"'alayhim",'upon themselves'),
            ('وَلَا','walā','and not'),
            ('ٱلضَّآلِّينَ','l-ḍālīna','those who go astray')],
    '2:1': [('الٓمٓ','alif-lām-meem','Alif · Lam · Meem')],
    '2:2': [('ذَٰلِكَ','dhālika','That'),
            ('ٱلْكِتَـٰبُ','l-kitābu','is the Book'),
            ('لَا','lā','no'),('رَيْبَ','rayba','doubt'),
            ('فِيهِ','fīhi','in it'),('هُدًى','hudan','a Guidance'),
            ('لِّلْمُتَّقِينَ',"lil'muttaqīna",'for the God-conscious')],

    '2:3': [('ٱلَّذِينَ','alladhīna','Those who'),
            ('يُؤْمِنُونَ',"yu'minūna",'believe'),
            ('بِٱلْغَيْبِ','bil-ghaybi','in the unseen'),
            ('وَيُقِيمُونَ','wayuqīmūna','and establish'),
            ('ٱلصَّلَوٰةَ','l-ṣalata','the prayer'),
            ('وَمِمَّا','wamimmā','and out of what'),
            ('رَزَقْنَـٰهُمْ','razaqnāhum','We provided them'),
            ('يُنفِقُونَ','yunfiqūna','they spend')],
    '2:4': [('وَٱلَّذِينَ','wa-alladhīna','And those who'),
            ('يُؤْمِنُونَ',"yu'minūna",'believe'),
            ('بِمَآ','bimā','in what'),('أُنزِلَ','unzila','was revealed'),
            ('إِلَيْكَ','ilayka','to you'),('وَمَآ','wamā','and what'),
            ('أُنزِلَ','unzila','was revealed'),('مِن','min','from'),
            ('قَبْلِكَ','qablika','before you'),
            ('وَبِٱلْـَٔاخِرَةِ','wabil-ākhirati','and in the Hereafter'),
            ('هُمْ','hum','they'),('يُوقِنُونَ','yūqinūna','firmly believe')],
    '2:5': [('أُو۟لَـٰٓئِكَ','ulāika','Those'),
            ('عَلَىٰ',"'alā",'are on'),('هُدًى','hudan','Guidance'),
            ('مِّن','min','from'),('رَّبِّهِمْ','rabbihim','their Lord'),
            ('وَأُو۟لَـٰٓئِكَ','wa-ulāika','and those'),
            ('هُمُ','humu','they are'),
            ('ٱلْمُفْلِحُونَ',"l-muf'liḥūna",'the successful ones')],
    '2:6': [('إِنَّ','inna','Indeed'),
            ('ٱلَّذِينَ','alladhīna','those who'),
            ('كَفَرُوا۟','kafarū','disbelieved'),
            ('سَوَآءٌ','sawāon','it is the same'),
            ('عَلَيْهِمْ',"'alayhim",'to them'),
            ('ءَأَنذَرْتَهُمْ','a-andhartahum','whether you warn them'),
            ('أَمْ','am','or'),('لَمْ','lam','not'),
            ('تُنذِرْهُمْ',"tundhir'hum",'you warn them'),
            ('لَا','lā','not'),('يُؤْمِنُونَ',"yu'minūna",'they will believe')],
    '2:7': [('خَتَمَ','khatama','Has set a seal'),
            ('ٱللَّهُ','l-lahu','Allah'),
            ('عَلَىٰ',"'alā",'on'),('قُلُوبِهِمْ','qulūbihim','their hearts'),
            ('وَعَلَىٰ',"wa'alā",'and on'),
            ('سَمْعِهِمْ',"sam'ihim",'their hearing'),
            ('وَعَلَىٰٓ',"wa'alā",'and on'),
            ('أَبْصَـٰرِهِمْ','abṣārihim','their vision'),
            ('غِشَـٰوَةٌ','ghishāwatun','is a veil'),
            ('وَلَهُمْ','walahum','and for them'),
            ('عَذَابٌ',"'adhābun",'is a punishment'),
            ('عَظِيمٌ',"'aẓīmun",'great')],
    '2:8': [('وَمِنَ','wamina','And of'),
            ('ٱلنَّاسِ','l-nāsi','the people'),
            ('مَن','man','are some who'),('يَقُولُ','yaqūlu','say'),
            ('ءَامَنَّا','āmannā','We believe'),
            ('بِٱللَّهِ','bil-lahi','in Allah'),
            ('وَبِٱلْيَوْمِ','wabil-yawmi','and in the Day'),
            ('ٱلْـَٔاخِرِ','l-ākhiri','the Last'),
            ('وَمَا','wamā','but not'),('هُم','hum','they'),
            ('بِمُؤْمِنِينَ',"bimu'minīna",'are believers')],
    '2:9': [('يُخَـٰدِعُونَ',"yukhādi'ūna",'They seek to deceive'),
            ('ٱللَّهَ','l-laha','Allah'),
            ('وَٱلَّذِينَ','wa-alladhīna','and those who'),
            ('ءَامَنُوا۟','āmanū','believed'),
            ('وَمَا','wamā','and not'),
            ('يَخْدَعُونَ',"yakhdha'ūna",'they deceive'),
            ('إِلَّآ','illā','except'),
            ('أَنفُسَهُمْ','anfusahum','themselves'),
            ('وَمَا','wamā','and not'),
            ('يَشْعُرُونَ',"yash'urūna",'they realize')],

    '2:10': [('فِى','fī','In'),
             ('قُلُوبِهِم','qulūbihim','their hearts'),
             ('مَّرَضٌ','maraḍun','is a disease'),
             ('فَزَادَهُمُ','fazādahumu','so has increased them'),
             ('ٱللَّهُ','l-lahu','Allah'),
             ('مَرَضًا','maraḍan','in disease'),
             ('وَلَهُمْ','walahum','and for them'),
             ('عَذَابٌ',"'adhābun",'is a punishment'),
             ('أَلِيمٌ','alīmun','painful'),
             ('بِمَا','bimā','because'),
             ('كَانُوا۟','kānū','they used to'),
             ('يَكْذِبُونَ','yakdhibūna','lie')],
    '2:11': [('وَإِذَا','wa-idhā','And when'),
             ('قِيلَ','qīla','it is said'),
             ('لَهُمْ','lahum','to them'),
             ('لَا','lā','Do not'),
             ('تُفْسِدُوا۟',"tuf'sidū",'cause corruption'),
             ('فِى','fī','in'),
             ('ٱلْأَرْضِ','l-arḍi','the earth'),
             ('قَالُوٓا۟','qālū','they say'),
             ('إِنَّمَا','innamā','We are only'),
             ('نَحْنُ','naḥnu','we'),
             ('مُصْلِحُونَ',"muṣ'liḥūna",'reformers')],
    '2:12': [('أَلَآ','alā','Beware'),
             ('إِنَّهُمْ','innahum','indeed they'),
             ('هُمُ','humu','themselves'),
             ('ٱلْمُفْسِدُونَ',"l-muf'sidūna",'are the corrupters'),
             ('وَلَـٰكِن','walākin','but'),
             ('لَّا','lā','not'),
             ('يَشْعُرُونَ',"yash'urūna",'they realize')],
    '2:13': [('وَإِذَا','wa-idhā','And when'),
             ('قِيلَ','qīla','it is said'),
             ('لَهُمْ','lahum','to them'),
             ('ءَامِنُوا۟','āminū','Believe'),
             ('كَمَآ','kamā','as'),('ءَامَنَ','āmana','believed'),
             ('ٱلنَّاسُ','l-nāsu','the people'),
             ('قَالُوٓا۟','qālū','they say'),
             ('أَنُؤْمِنُ',"anu'minu",'Should we believe'),
             ('كَمَآ','kamā','as'),('ءَامَنَ','āmana','believed'),
             ('ٱلسُّفَهَآءُ','l-sufahāu','the fools'),
             ('أَلَآ','alā','Beware'),
             ('إِنَّهُمْ','innahum','certainly they'),
             ('هُمُ','humu','themselves'),
             ('ٱلسُّفَهَآءُ','l-sufahāu','are the fools'),
             ('وَلَـٰكِن','walākin','but'),
             ('لَّا','lā','not'),
             ('يَعْلَمُونَ',"ya'lamūna",'they know')],
}

MEANINGS = {
    '1:1': 'In the name of Allah, the Most Gracious, the Most Merciful.',
    '1:2': 'All praise and thanks belong to Allah, Lord of all the worlds.',
    '1:3': 'The Most Gracious, the Most Merciful.',
    '1:4': 'Master of the Day of Judgment.',
    '1:5': 'You alone we worship, and You alone we ask for help.',
    '1:6': 'Guide us to the straight path —',
    '1:7': 'The path of those upon whom You have bestowed favour; not of those who earned anger, nor those who went astray.',
    '2:1': 'Alif, Lam, Meem. [Letters whose meaning is known only to Allah.]',
    '2:2': 'This is the Book in which there is no doubt — a guidance for those mindful of Allah.',
    '2:3': 'Who believe in the unseen, establish prayer, and spend out of what We have provided for them.',
    '2:4': 'And who believe in what was revealed to you and what was revealed before you, and of the Hereafter they are certain.',
    '2:5': 'Those are upon guidance from their Lord, and it is those who are the successful.',
    '2:6': 'Indeed, those who disbelieve — it is all the same whether you warn them or not — they will not believe.',
    '2:7': 'Allah has set a seal upon their hearts and upon their hearing, and over their vision is a veil. For them is a great punishment.',
    '2:8': 'And among the people are those who say, "We believe in Allah and the Last Day," but they are not believers.',
    '2:9': 'They seek to deceive Allah and those who believe, but they deceive none except themselves, and they perceive it not.',
    '2:10': 'In their hearts is a disease, and Allah has increased their disease. For them is a painful punishment because they used to lie.',
    '2:11': 'And when it is said to them, "Do not cause corruption on the earth," they say, "We are only reformers."',
    '2:12': 'Unquestionably, it is they who are the corrupters, but they perceive it not.',
    '2:13': 'And when it is said to them, "Believe as the people have believed," they say, "Should we believe as the fools have believed?" — Beware, it is they who are the fools, but they do not know.',
}


# ── PAGE DEFINITIONS ──────────────────────────────────────────────────────
# 'verses' lists verse keys in order for this page.
# Rows are computed automatically from word count.
PAGES = [
    {'num':1,'juz':1,
     'surah_en':'AL-FATIHA','surah_meaning':'The Opening',
     'surah_ar':'سُورَةُ الْفَاتِحَة','surah_no':1,
     'revealed':'Makkah','verses_total':7,
     'new_surah':True,'bismillah_separate':False,
     'verses':['1:1','1:2','1:3','1:4','1:5','1:6','1:7'],
     'wpr':5},
    {'num':2,'juz':1,
     'surah_en':'AL-BAQARAH','surah_meaning':'The Cow',
     'surah_ar':'سُورَةُ الْبَقَرَة','surah_no':2,
     'revealed':'Madinah','verses_total':286,
     'new_surah':True,'bismillah_separate':True,
     'verses':['2:1','2:2','2:3','2:4'],
     'wpr':5},
    {'num':3,'juz':1,
     'surah_en':'AL-BAQARAH','surah_meaning':'The Cow',
     'surah_ar':'سُورَةُ الْبَقَرَة','surah_no':2,
     'revealed':'Madinah','verses_total':286,
     'new_surah':False,'bismillah_separate':False,
     'verses':['2:5','2:6','2:7'],
     'wpr':5},
    {'num':4,'juz':1,
     'surah_en':'AL-BAQARAH','surah_meaning':'The Cow',
     'surah_ar':'سُورَةُ الْبَقَرَة','surah_no':2,
     'revealed':'Madinah','verses_total':286,
     'new_surah':False,'bismillah_separate':False,
     'verses':['2:8','2:9','2:10'],
     'wpr':5},
    {'num':5,'juz':1,
     'surah_en':'AL-BAQARAH','surah_meaning':'The Cow',
     'surah_ar':'سُورَةُ الْبَقَرَة','surah_no':2,
     'revealed':'Madinah','verses_total':286,
     'new_surah':False,'bismillah_separate':False,
     'verses':['2:11','2:12','2:13'],
     'wpr':5},
]

# ── ROW BUILDER ───────────────────────────────────────────────────────────
def verse_rows(vkey, wpr):
    """Split verse words into rows of wpr, placing ۝marker at end of last row."""
    words = WORDS[vkey]
    items = [('W', vkey, i) for i in range(len(words))]
    items.append(('M', vkey, -1))          # Ayah end marker
    return [items[i:i+wpr] for i in range(0, len(items), wpr)]

# ── HTML FRAGMENTS ────────────────────────────────────────────────────────
def word_cell(vkey, widx):
    a, t, e = WORDS[vkey][widx]
    return (f'<div class="wc">'
            f'<div class="tr">{t}</div>'
            f'<div class="hd"></div>'
            f'<div class="aw">{a}</div>'
            f'<div class="hd"></div>'
            f'<div class="mn">{e}</div>'
            f'</div>')

def marker_cell(vkey):
    n = int(vkey.split(':')[1])
    return (f'<div class="am">'
            f'<div class="as">۝{ar(n)}</div>'
            f'</div>')

def verse_section(vkey, wpr):
    rows = verse_rows(vkey, wpr)
    nrows = len(rows)
    vn = int(vkey.split(':')[1])
    rows_html = []
    for row in rows:
        cells = []
        for typ, vk, wi in row:
            cells.append(marker_cell(vk) if typ=='M' else word_cell(vk, wi))
        rows_html.append(f'<div class="wr">{"".join(cells)}</div>')
    return (f'<div class="vs" style="flex:{nrows}">'
            f'<div class="vm">'
            f'<div class="vn">{ar(vn)}</div>'
            f'<div class="vt">&#8220;{MEANINGS[vkey]}&#8221;</div>'
            f'</div>'
            f'<div class="vw">{"".join(rows_html)}</div>'
            f'</div>')

def page_header(p):
    h = (f'<div class="ph">'
         f'<div class="phb">'
         f'<span class="phl">JUZ {p["juz"]}</span>'
         f'<div class="phc"><span class="pho">&#10022;</span>'
         f'<span class="phn">{p["surah_en"]}</span>'
         f'<span class="pho">&#10022;</span></div>'
         f'<span class="php">PAGE {p["num"]}</span>'
         f'</div>')
    if p['new_surah']:
        h += (f'<div class="sb">'
              f'<div class="sbar">{p["surah_ar"]}</div>'
              f'<div class="sbi">Surah {p["surah_no"]} &nbsp;&#8226;&nbsp; '
              f'{p["surah_meaning"]} &nbsp;&#8226;&nbsp; '
              f'Revealed in {p["revealed"]} &nbsp;&#8226;&nbsp; '
              f'{p["verses_total"]} Verses</div>'
              f'</div>')
    h += '</div>'
    return h

def bismillah():
    return ('<div class="bm">'
            '<div class="bt">Bis-mil-lā-hir &nbsp; Raḥ-mā-nir &nbsp; Raḥīm</div>'
            '<div class="ba">بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ</div>'
            '</div>')

def page_footer(p):
    return (f'<div class="pf">'
            f'<span>Surah {p["surah_en"]} &mdash; {p["surah_meaning"]}</span>'
            f'<span>Page {p["num"]} &nbsp;|&nbsp; Juz {p["juz"]}</span>'
            f'</div>')

def render_page(p):
    wpr = p['wpr']
    bm = bismillah() if p['bismillah_separate'] else ''

    # LEFT — compact numbered meaning list (no height sync needed)
    me_parts = []
    for vk in p['verses']:
        vnum = ar(int(vk.split(':')[1]))
        me_parts.append(
            f'<div class="me">'
            f'<span class="vn">{vnum}</span>'
            f'<span class="vt">&#8220;{MEANINGS[vk]}&#8221;</span>'
            f'</div>'
        )
    left = f'<div class="mc">{"".join(me_parts)}</div>'

    # RIGHT — all verses flow continuously, no empty rows after short verses
    items = []
    for vk in p['verses']:
        for i in range(len(WORDS[vk])):
            items.append(('W', vk, i))
        items.append(('M', vk, -1))   # inline Ayah marker

    row_parts = []
    for chunk in [items[i:i+wpr] for i in range(0, len(items), wpr)]:
        cells = ''.join(
            marker_cell(vk) if t == 'M' else word_cell(vk, wi)
            for t, vk, wi in chunk
        )
        row_parts.append(f'<div class="wr">{cells}</div>')
    right = f'<div class="vw">{"".join(row_parts)}</div>'

    return (f'<div class="page">'
            f'{page_header(p)}{bm}'
            f'<div class="vb">{left}{right}</div>'
            f'{page_footer(p)}'
            f'</div>')


# ── CSS ───────────────────────────────────────────────────────────────────
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#9e8f72;display:flex;flex-direction:column;align-items:center;
     padding:35px 20px;gap:40px;font-family:'EB Garamond',serif}

/* PAGE — ivory parchment, double gold Mushaf frame */
.page{background:#fdf7ed;width:210mm;min-height:297mm;
      padding:11mm 10mm 9mm 10mm;
      border:1.5px solid #c9a84c;
      box-shadow:0 0 0 4px #fdf7ed,0 0 0 5.5px #c9a84c,0 10px 50px rgba(0,0,0,.32);
      display:flex;flex-direction:column;position:relative}
.page::before{content:'';position:absolute;inset:8px;
              border:0.5px solid rgba(201,168,76,.4);pointer-events:none;z-index:0}

/* HEADER — double gold rule */
.ph{margin-bottom:4px;position:relative;z-index:1}
.phb{display:flex;justify-content:space-between;align-items:center;
     background:#f8f0dc;border-top:2px solid #8b6c14;border-bottom:2px solid #8b6c14;
     box-shadow:inset 0 2px 0 #e8d49a,inset 0 -2px 0 #e8d49a;padding:5px 8px}
.phl{font-size:9px;color:#7a5810;letter-spacing:1.2px;font-weight:700;
     text-transform:uppercase;min-width:55px}
.phc{display:flex;align-items:center;gap:10px}
.pho{font-size:15px;color:#c9a84c;line-height:1}
.phn{font-size:13px;font-weight:700;letter-spacing:2.5px;color:#1a0e04;text-transform:uppercase}
.php{font-size:9px;color:#7a5810;text-align:right;min-width:55px;
     letter-spacing:.8px;font-weight:700}

/* SURAH START BAND */
.sb{background:linear-gradient(135deg,#f4e8c4 0%,#ede0aa 50%,#f4e8c4 100%);
    border-top:1px solid #c9a84c;border-bottom:1px solid #c9a84c;
    padding:8px 30px 7px;text-align:center;position:relative;margin-bottom:2px}
.sb::before,.sb::after{content:'❖';position:absolute;top:50%;
    transform:translateY(-50%);color:#c9a84c;font-size:11px}
.sb::before{left:9px}.sb::after{right:9px}
.sbar{font-family:'Amiri',serif;font-size:21px;direction:rtl;
      color:#1a0e04;margin-bottom:3px;letter-spacing:1px}
.sbi{font-size:10px;color:#7a5810;letter-spacing:.5px}

/* BISMILLAH — compact, ~50% shorter */
.bm{background:linear-gradient(to right,#fdf7ed,#f5ead0,#fdf7ed);
    border-top:0.5px solid #c9a84c;border-bottom:0.5px solid #c9a84c;
    padding:4px 12px 3px;text-align:center;margin-bottom:2px}
.bt{font-size:7px;font-style:italic;color:#a07830;margin-bottom:2px;letter-spacing:1.2px}
.ba{font-family:'Amiri',serif;font-size:34px;direction:rtl;
    color:rgba(0,0,0,.12);line-height:1.2}
"""


CSS += """
/* VERSE BODY — flex-ROW: left meaning list | right continuous word flow */
.vb{flex:1;display:flex;flex-direction:row;
    border:1px solid #d4b870;background:#fdf7ed;overflow:hidden}

/* LEFT — compact numbered meaning list, full page height */
.mc{width:21%;min-width:21%;border-right:1px solid #d4b870;
    background:#f6ead6;padding:4px 5px;
    display:flex;flex-direction:column;gap:0}
.me{display:flex;align-items:flex-start;gap:4px;
    padding:5px 2px;border-bottom:1px dashed #d4b870}
.me:last-child{border-bottom:none}
.vn{font-family:'Amiri',serif;font-size:10px;font-weight:700;color:#8b6c14;
    border:1px solid #c9a84c;border-radius:50%;width:15px;height:15px;
    display:inline-flex;align-items:center;justify-content:center;
    flex-shrink:0;background:#fdf7ed;direction:rtl;margin-top:1px}
.vt{font-family:'EB Garamond',serif;font-size:9.5px;font-style:italic;
    color:#2a1a06;line-height:1.5}

/* RIGHT — continuous word flow across all verses */
.vw{flex:1;display:flex;flex-direction:column;padding:1px 4px 0px}

/* WORD ROW — fills column height, words sit flush, no gap */
.wr{flex:1;display:flex;flex-direction:row-reverse;
    align-items:stretch;border-bottom:0.5px solid #e8d8b8;
    gap:0;justify-content:flex-start}
.wr:last-child{border-bottom:none}

/* WORD CELL — adaptive base width + grow to fill row width */
.wc{flex:1 1 auto;min-width:36px;display:flex;flex-direction:column}

/* AYAH END MARKER — compact */
.am{flex:0 0 22px;display:flex;align-items:center;justify-content:center}
.as{font-family:'Amiri',serif;font-size:16px;color:#c9a84c;
    direction:rtl;line-height:1;text-align:center}

/* ── 3-SECTION WORD CELL CONTENT ── */

/* Transliteration — top, minimum footprint */
.tr{font-family:'EB Garamond',serif;font-size:7.5px;font-style:italic;
    color:#a07830;text-align:center;padding:1px 2px 0px;
    min-height:10px;display:flex;align-items:center;justify-content:center;
    letter-spacing:.1px}

/* Horizontal hairline — minimal margin */
.hd{height:0.5px;background:#e4d0a8;margin:0 1px}

/* Arabic — visual king, minimum padding, font size preserved at 27px */
.aw{font-family:'Amiri',serif;font-size:27px;direction:rtl;text-align:center;
    padding:3px 3px 2px;flex:1;display:flex;align-items:center;
    justify-content:center;color:rgba(0,0,0,.13);line-height:1.45}

/* English meaning — bottom, minimal padding */
.mn{font-family:'EB Garamond',serif;font-size:8px;text-align:center;
    color:#1e1206;padding:0px 2px 2px;min-height:13px;
    display:flex;align-items:center;justify-content:center;line-height:1.25}

/* FOOTER — gold rule */
.pf{padding-top:5px;border-top:2px solid #8b6c14;display:flex;
    justify-content:space-between;font-size:9px;color:#7a5810;
    margin-top:7px;letter-spacing:.5px;font-weight:600}

@media print{
  body{background:#fdf7ed;padding:0;gap:0}
  .page{box-shadow:none;border-color:#8b6c14;page-break-after:always}
  .page::before{display:none}
}
"""


# ── BUILD & MAIN ──────────────────────────────────────────────────────────
def build_html():
    pages_html = '\n\n'.join(render_page(p) for p in PAGES)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Traceable Quran &#8212; 5 Page Preview</title>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet"/>
  <style>{CSS}</style>
</head>
<body>
{pages_html}
</body>
</html>"""

if __name__ == '__main__':
    html = build_html()
    with open('sample-page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    # Report per-page row counts for verification
    for p in PAGES:
        total_rows = sum(len(verse_rows(vk, p['wpr'])) for vk in p['verses'])
        print(f"Page {p['num']} ({p['surah_en']}): {len(p['verses'])} verses, "
              f"{total_rows} total rows, "
              f"verses: {', '.join(p['verses'])}")
    print(f"\nGenerated sample-page.html — {len(html):,} chars")
