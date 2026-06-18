#!/usr/bin/env python3
"""Generate 5-page Traceable Quran HTML preview."""

# ── ALL WORD DATA (arabic, transliteration, english meaning) ──────────────
WORDS = {
    # Al-Fatiha
    '1:1': [('بِسْمِ','bis\'mi','In the name'),('ٱللَّهِ','l-lahi','of Allah'),('ٱلرَّحْمَـٰنِ','l-raḥmāni','the Most Gracious'),('ٱلرَّحِيمِ','l-raḥīmi','the Most Merciful')],
    '1:2': [('ٱلْحَمْدُ','al-ḥamdu','All praise'),('لِلَّهِ','lillahi','be to Allah'),('رَبِّ','rabbi','the Lord'),('ٱلْعَـٰلَمِينَ','l-ʿālamīna','of all the worlds')],
    '1:3': [('ٱلرَّحْمَـٰنِ','al-raḥmāni','The Most Gracious'),('ٱلرَّحِيمِ','l-raḥīmi','the Most Merciful')],
    '1:4': [('مَـٰلِكِ','māliki','Master'),('يَوْمِ','yawmi','of the Day'),('ٱلدِّينِ','l-dīni','of Judgment')],
    '1:5': [('إِيَّاكَ','iyyāka','You alone'),('نَعْبُدُ','naʿbudu','we worship'),('وَإِيَّاكَ','wa-iyyāka','and You alone'),('نَسْتَعِينُ','nastaʿīnu','we ask for help')],
    '1:6': [('ٱهْدِنَا','ih\'dinā','Guide us'),('ٱلصِّرَٰطَ','l-ṣirāṭa','to the path'),('ٱلْمُسْتَقِيمَ','l-mus\'taqīma','the straight')],
    '1:7': [('صِرَٰطَ','ṣirāṭa','The path'),('ٱلَّذِينَ','alladhīna','of those'),('أَنْعَمْتَ','anʿamta','You bestowed favour'),('عَلَيْهِمْ','ʿalayhim','on them'),('غَيْرِ','ghayri','not of'),('ٱلْمَغْضُوبِ','l-maghḍūbi','who earned wrath'),('عَلَيْهِمْ','ʿalayhim','upon themselves'),('وَلَا','walā','and not'),('ٱلضَّآلِّينَ','l-ḍālīna','those who go astray')],
    # Al-Baqarah
    '2:1': [('الٓمٓ','alif-lām-meem','Alif • Lam • Meem')],
    '2:2': [('ذَٰلِكَ','dhālika','That'),('ٱلْكِتَـٰبُ','l-kitābu','is the Book'),('لَا','lā','no'),('رَيْبَ','rayba','doubt'),('فِيهِ','fīhi','in it'),('هُدًى','hudan','a Guidance'),('لِّلْمُتَّقِينَ','lil\'muttaqīna','for the God-conscious')],
    '2:3': [('ٱلَّذِينَ','alladhīna','Those who'),('يُؤْمِنُونَ','yu\'minūna','believe'),('بِٱلْغَيْبِ','bil-ghaybi','in the unseen'),('وَيُقِيمُونَ','wayuqīmūna','and establish'),('ٱلصَّلَوٰةَ','l-ṣalata','the prayer'),('وَمِمَّا','wamimmā','and out of what'),('رَزَقْنَـٰهُمْ','razaqnāhum','We provided them'),('يُنفِقُونَ','yunfiqūna','they spend')],
    '2:4': [('وَٱلَّذِينَ','wa-alladhīna','And those who'),('يُؤْمِنُونَ','yu\'minūna','believe'),('بِمَآ','bimā','in what'),('أُنزِلَ','unzila','was revealed'),('إِلَيْكَ','ilayka','to you'),('وَمَآ','wamā','and what'),('أُنزِلَ','unzila','was revealed'),('مِن','min','from'),('قَبْلِكَ','qablika','before you'),('وَبِٱلْـَٔاخِرَةِ','wabil-ākhirati','and in the Hereafter'),('هُمْ','hum','they'),('يُوقِنُونَ','yūqinūna','firmly believe')],
    '2:5': [('أُو۟لَـٰٓئِكَ','ulāika','Those'),('عَلَىٰ','ʿalā','are on'),('هُدًى','hudan','Guidance'),('مِّن','min','from'),('رَّبِّهِمْ','rabbihim','their Lord'),('وَأُو۟لَـٰٓئِكَ','wa-ulāika','and those'),('هُمُ','humu','they are'),('ٱلْمُفْلِحُونَ','l-muf\'liḥūna','the successful ones')],
    '2:6': [('إِنَّ','inna','Indeed'),('ٱلَّذِينَ','alladhīna','those who'),('كَفَرُوا۟','kafarū','disbelieved'),('سَوَآءٌ','sawāon','it is the same'),('عَلَيْهِمْ','ʿalayhim','to them'),('ءَأَنذَرْتَهُمْ','a-andhartahum','whether you warn them'),('أَمْ','am','or'),('لَمْ','lam','not'),('تُنذِرْهُمْ','tundhir\'hum','you warn them'),('لَا','lā','not'),('يُؤْمِنُونَ','yu\'minūna','they will believe')],
    '2:7': [('خَتَمَ','khatama','Has set a seal'),('ٱللَّهُ','l-lahu','Allah'),('عَلَىٰ','ʿalā','on'),('قُلُوبِهِمْ','qulūbihim','their hearts'),('وَعَلَىٰ','waʿalā','and on'),('سَمْعِهِمْ','samʿihim','their hearing'),('وَعَلَىٰٓ','waʿalā','and on'),('أَبْصَـٰرِهِمْ','abṣārihim','their vision'),('غِشَـٰوَةٌ','ghishāwatun','is a veil'),('وَلَهُمْ','walahum','and for them'),('عَذَابٌ','ʿadhābun','is a punishment'),('عَظِيمٌ','ʿaẓīmun','great')],
    '2:8': [('وَمِنَ','wamina','And of'),('ٱلنَّاسِ','l-nāsi','the people'),('مَن','man','(are some) who'),('يَقُولُ','yaqūlu','say'),('ءَامَنَّا','āmannā','We believe'),('بِٱللَّهِ','bil-lahi','in Allah'),('وَبِٱلْيَوْمِ','wabil-yawmi','and in the Day'),('ٱلْـَٔاخِرِ','l-ākhiri','the Last'),('وَمَا','wamā','but not'),('هُم','hum','they'),('بِمُؤْمِنِينَ','bimu\'minīna','are believers')],
    '2:9': [('يُخَـٰدِعُونَ','yukhādiʿūna','They seek to deceive'),('ٱللَّهَ','l-laha','Allah'),('وَٱلَّذِينَ','wa-alladhīna','and those who'),('ءَامَنُوا۟','āmanū','believed'),('وَمَا','wamā','and not'),('يَخْدَعُونَ','yakhdaʿūna','they deceive'),('إِلَّآ','illā','except'),('أَنفُسَهُمْ','anfusahum','themselves'),('وَمَا','wamā','and not'),('يَشْعُرُونَ','yashʿurūna','they realize')],
    '2:10': [('فِى','fī','In'),('قُلُوبِهِم','qulūbihim','their hearts'),('مَّرَضٌ','maraḍun','is a disease'),('فَزَادَهُمُ','fazādahumu','so increased them'),('ٱللَّهُ','l-lahu','Allah'),('مَرَضًا','maraḍan','in disease'),('وَلَهُمْ','walahum','and for them'),('عَذَابٌ','ʿadhābun','is a punishment'),('أَلِيمٌ','alīmun','painful'),('بِمَا','bimā','because'),('كَانُوا۟','kānū','they used to'),('يَكْذِبُونَ','yakdhibūna','lie')],
    '2:11': [('وَإِذَا','wa-idhā','And when'),('قِيلَ','qīla','it is said'),('لَهُمْ','lahum','to them'),('لَا','lā','Do not'),('تُفْسِدُوا۟','tuf\'sidū','spread corruption'),('فِى','fī','in'),('ٱلْأَرْضِ','l-arḍi','the earth'),('قَالُوٓا۟','qālū','they say'),('إِنَّمَا','innamā','Only'),('نَحْنُ','naḥnu','we'),('مُصْلِحُونَ','muṣ\'liḥūna','are reformers')],
    '2:12': [('أَلَآ','alā','Beware'),('إِنَّهُمْ','innahum','indeed they'),('هُمُ','humu','themselves'),('ٱلْمُفْسِدُونَ','l-muf\'sidūna','are the corrupters'),('وَلَـٰكِن','walākin','but'),('لَّا','lā','not'),('يَشْعُرُونَ','yashʿurūna','they realize')],
    '2:13': [('وَإِذَا','wa-idhā','And when'),('قِيلَ','qīla','it is said'),('لَهُمْ','lahum','to them'),('ءَامِنُوا۟','āminū','Believe'),('كَمَآ','kamā','as'),('ءَامَنَ','āmana','believed'),('ٱلنَّاسُ','l-nāsu','the people'),('قَالُوٓا۟','qālū','they say'),('أَنُؤْمِنُ','anu\'minu','Should we believe'),('كَمَآ','kamā','as'),('ءَامَنَ','āmana','believed'),('ٱلسُّفَهَآءُ','l-sufahāu','the fools'),('أَلَآ','alā','Beware'),('إِنَّهُمْ','innahum','certainly they'),('هُمُ','humu','themselves'),('ٱلسُّفَهَآءُ','l-sufahāu','are the fools'),('وَلَـٰكِن','walākin','but'),('لَّا','lā','not'),('يَعْلَمُونَ','yaʿlamūna','they know')],
}

MEANINGS = {
    '1:1': 'In the name of Allah, the Most Gracious, the Most Merciful.',
    '1:2': 'All praise and thanks belong to Allah, Lord of all the worlds.',
    '1:3': 'The Most Gracious, the Most Merciful.',
    '1:4': 'Master of the Day of Judgment.',
    '1:5': 'You alone we worship, and You alone we ask for help.',
    '1:6': 'Guide us to the straight path —',
    '1:7': 'The path of those upon whom You have bestowed favour, not of those who earned anger, nor those who went astray.',
    '2:1': 'Alif, Lam, Meem. [These are letters of the Arabic alphabet whose precise meaning is known only to Allah.]',
    '2:2': 'This is the Book in which there is no doubt, a guidance for those mindful of Allah.',
    '2:3': 'Who believe in the unseen, establish prayer, and spend out of what We have provided for them.',
    '2:4': 'And who believe in what was revealed to you and what was revealed before you, and of the Hereafter they are certain.',
    '2:5': 'Those are upon guidance from their Lord, and those are the successful ones.',
    '2:6': 'Indeed, those who disbelieve — it is all the same whether you warn them or not — they will not believe.',
    '2:7': 'Allah has set a seal upon their hearts and upon their hearing, and over their vision is a veil. For them is a great punishment.',
    '2:8': 'And among people are those who say "We believe in Allah and the Last Day," but they are not believers.',
    '2:9': 'They seek to deceive Allah and those who believe, but they deceive none except themselves, and they do not realize it.',
    '2:10': 'In their hearts is a disease, and Allah has increased their disease. For them is a painful punishment because they used to lie.',
    '2:11': 'And when it is said to them, "Do not cause corruption on the earth," they say, "We are only reformers."',
    '2:12': 'Unquestionably, it is they who are the corrupters, but they do not realize it.',
    '2:13': 'And when it is said to them, "Believe as the people have believed," they say, "Should we believe as the fools believed?" — Beware, it is they who are the fools, but they do not know.',
}

# ── PAGE DEFINITIONS ──────────────────────────────────────────────────────
# Each row: list of (verse_key, word_index_0based, is_verse_start)
PAGES = [
    {
        'num': 1, 'juz': 1, 'hizb': '1', 'para': 'Juz 1 — Para 1',
        'surah_ar': 'سُورَةُ الْفَاتِحَة', 'surah_en': 'AL-FATIHA', 'surah_meaning': 'The Opening',
        'surah_no': 1, 'revealed': 'Makkah', 'verses_total': 7,
        'new_surah': True, 'bismillah_separate': False,
        'verse_meanings': ['1:1','1:2','1:3','1:4','1:5','1:6','1:7'],
        'rows': [
            [('1:1',0,True),('1:1',1,False),('1:1',2,False),('1:1',3,False),('1:2',0,True),('1:2',1,False)],
            [('1:2',2,False),('1:2',3,False),('1:3',0,True),('1:3',1,False),('1:4',0,True),('1:4',1,False)],
            [('1:4',2,False),('1:5',0,True),('1:5',1,False),('1:5',2,False),('1:5',3,False)],
            [('1:6',0,True),('1:6',1,False),('1:6',2,False),('1:7',0,True),('1:7',1,False),('1:7',2,False)],
            [('1:7',3,False),('1:7',4,False),('1:7',5,False),('1:7',6,False),('1:7',7,False),('1:7',8,False)],
        ]
    },
    {
        'num': 2, 'juz': 1, 'hizb': '1', 'para': 'Juz 1 — Para 1',
        'surah_ar': 'سُورَةُ الْبَقَرَة', 'surah_en': 'AL-BAQARAH', 'surah_meaning': 'The Cow',
        'surah_no': 2, 'revealed': 'Madinah', 'verses_total': 286,
        'new_surah': True, 'bismillah_separate': True,
        'verse_meanings': ['2:1','2:2','2:3','2:4'],
        'rows': [
            [('2:1',0,True)],
            [('2:2',0,True),('2:2',1,False),('2:2',2,False),('2:2',3,False),('2:2',4,False),('2:2',5,False)],
            [('2:2',6,False),('2:3',0,True),('2:3',1,False),('2:3',2,False),('2:3',3,False),('2:3',4,False)],
            [('2:3',5,False),('2:3',6,False),('2:3',7,False),('2:4',0,True),('2:4',1,False),('2:4',2,False)],
            [('2:4',3,False),('2:4',4,False),('2:4',5,False),('2:4',6,False),('2:4',7,False),('2:4',8,False)],
            [('2:4',9,False),('2:4',10,False),('2:4',11,False)],
        ]
    },
    {
        'num': 3, 'juz': 1, 'hizb': '1', 'para': 'Juz 1 — Para 1',
        'surah_ar': 'سُورَةُ الْبَقَرَة', 'surah_en': 'AL-BAQARAH', 'surah_meaning': 'The Cow',
        'surah_no': 2, 'revealed': 'Madinah', 'verses_total': 286,
        'new_surah': False, 'bismillah_separate': False,
        'verse_meanings': ['2:5','2:6','2:7'],
        'rows': [
            [('2:5',0,True),('2:5',1,False),('2:5',2,False),('2:5',3,False),('2:5',4,False),('2:5',5,False)],
            [('2:5',6,False),('2:5',7,False),('2:6',0,True),('2:6',1,False),('2:6',2,False),('2:6',3,False)],
            [('2:6',4,False),('2:6',5,False),('2:6',6,False),('2:6',7,False),('2:6',8,False),('2:6',9,False)],
            [('2:6',10,False),('2:7',0,True),('2:7',1,False),('2:7',2,False),('2:7',3,False),('2:7',4,False)],
            [('2:7',5,False),('2:7',6,False),('2:7',7,False),('2:7',8,False),('2:7',9,False),('2:7',10,False)],
            [('2:7',11,False)],
        ]
    },
    {
        'num': 4, 'juz': 1, 'hizb': '1', 'para': 'Juz 1 — Para 1',
        'surah_ar': 'سُورَةُ الْبَقَرَة', 'surah_en': 'AL-BAQARAH', 'surah_meaning': 'The Cow',
        'surah_no': 2, 'revealed': 'Madinah', 'verses_total': 286,
        'new_surah': False, 'bismillah_separate': False,
        'verse_meanings': ['2:8','2:9','2:10'],
        'rows': [
            [('2:8',0,True),('2:8',1,False),('2:8',2,False),('2:8',3,False),('2:8',4,False),('2:8',5,False)],
            [('2:8',6,False),('2:8',7,False),('2:8',8,False),('2:8',9,False),('2:8',10,False),('2:9',0,True)],
            [('2:9',1,False),('2:9',2,False),('2:9',3,False),('2:9',4,False),('2:9',5,False),('2:9',6,False)],
            [('2:9',7,False),('2:9',8,False),('2:9',9,False),('2:10',0,True),('2:10',1,False),('2:10',2,False)],
            [('2:10',3,False),('2:10',4,False),('2:10',5,False),('2:10',6,False),('2:10',7,False),('2:10',8,False)],
            [('2:10',9,False),('2:10',10,False),('2:10',11,False)],
        ]
    },
    {
        'num': 5, 'juz': 1, 'hizb': '1', 'para': 'Juz 1 — Para 1',
        'surah_ar': 'سُورَةُ الْبَقَرَة', 'surah_en': 'AL-BAQARAH', 'surah_meaning': 'The Cow',
        'surah_no': 2, 'revealed': 'Madinah', 'verses_total': 286,
        'new_surah': False, 'bismillah_separate': False,
        'verse_meanings': ['2:11','2:12','2:13'],
        'rows': [
            [('2:11',0,True),('2:11',1,False),('2:11',2,False),('2:11',3,False),('2:11',4,False),('2:11',5,False)],
            [('2:11',6,False),('2:11',7,False),('2:11',8,False),('2:11',9,False),('2:11',10,False),('2:12',0,True)],
            [('2:12',1,False),('2:12',2,False),('2:12',3,False),('2:12',4,False),('2:12',5,False),('2:12',6,False)],
            [('2:13',0,True),('2:13',1,False),('2:13',2,False),('2:13',3,False),('2:13',4,False),('2:13',5,False)],
            [('2:13',6,False),('2:13',7,False),('2:13',8,False),('2:13',9,False),('2:13',10,False),('2:13',11,False)],
            [('2:13',12,False),('2:13',13,False),('2:13',14,False),('2:13',15,False),('2:13',16,False),('2:13',17,False)],
            [('2:13',18,False)],
        ]
    },
]


# ── HTML GENERATOR ────────────────────────────────────────────────────────

def word_cell(vkey, widx, is_start, verse_num_map):
    ar, tr, en = WORDS[vkey][widx]
    vnum = vkey.split(':')[1]
    if is_start:
        cls = 'word-cell verse-start'
        extra = f' data-verse="{vnum}"'
    else:
        cls = 'word-cell'
        extra = ''
    return (
        f'        <div class="{cls}"{extra}>\n'
        f'          <div class="translit">{tr}</div>\n'
        f'          <div class="cdiv"></div>\n'
        f'          <div class="arabic">{ar}</div>\n'
        f'          <div class="cdiv"></div>\n'
        f'          <div class="meaning">{en}</div>\n'
        f'        </div>'
    )

def render_row(row_words):
    cells = '\n'.join(word_cell(vk, wi, vs, {}) for vk, wi, vs in row_words)
    return f'      <div class="word-row">\n{cells}\n      </div>'

def render_meanings(verse_keys):
    items = []
    for vk in verse_keys:
        num = vk.split(':')[1]
        text = MEANINGS[vk]
        items.append(f'''      <div class="me">
        <span class="vb">{num}</span>
        <span class="mp">&#8220;{text}&#8221;</span>
      </div>''')
    return '\n'.join(items)

def render_header(p):
    surah_block = f'''  <div class="ph">
    <div class="ph-bar">
      <span class="ph-juz">JUZ {p['juz']}</span>
      <div class="ph-center">
        <span class="ph-orn">&#10022;</span>
        <span class="ph-name">{p['surah_en']}</span>
        <span class="ph-orn">&#10022;</span>
      </div>
      <span class="ph-pg">PAGE {p['num']}</span>
    </div>'''
    if p['new_surah']:
        surah_block += f'''
    <div class="surah-band">
      <div class="surah-band-ar">{p['surah_ar']}</div>
      <div class="surah-band-info">
        Surah {p['surah_no']} &nbsp;&#8226;&nbsp; {p['surah_meaning']} &nbsp;&#8226;&nbsp;
        Revealed in {p['revealed']} &nbsp;&#8226;&nbsp; {p['verses_total']} Verses
      </div>
    </div>'''
    surah_block += '\n  </div>'
    return surah_block

def render_bismillah():
    return '''  <div class="bism-row">
    <div class="bism-tr">Bis-mil-lā-hir &nbsp; Raḥ-mā-nir &nbsp; Raḥīm</div>
    <div class="bism-ar">بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ</div>
  </div>'''

def render_page(p):
    header = render_header(p)
    bismillah = render_bismillah() if p['bismillah_separate'] else ''
    meanings = render_meanings(p['verse_meanings'])
    rows = '\n'.join(render_row(r) for r in p['rows'])
    footer = f'''  <div class="pf">
    <span>Surah {p['surah_en']} &mdash; {p['surah_meaning']}</span>
    <span>Page {p['num']} &nbsp;|&nbsp; {p['para']}</span>
  </div>'''
    return f'''<div class="page">
{header}
{bismillah}
  <div class="body">
    <div class="mc">
{meanings}
    </div>
    <div class="wc">
{rows}
    </div>
  </div>
{footer}
</div>'''


# ── CSS ───────────────────────────────────────────────────────────────────
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#a89870;display:flex;flex-direction:column;align-items:center;padding:35px 20px;gap:40px;font-family:'EB Garamond',serif}

/* PAGE — warm ivory, double gold frame like a Mushaf */
.page{
  background:#fdf7ed;
  width:210mm;min-height:297mm;
  padding:11mm 10mm 9mm 10mm;
  /* Double-border: gold border, cream gap, gold outline */
  border:1.5px solid #c9a84c;
  box-shadow:0 0 0 4px #fdf7ed, 0 0 0 5.5px #c9a84c, 0 10px 50px rgba(0,0,0,.32);
  display:flex;flex-direction:column;position:relative;
}
/* Inner frame hairline */
.page::before{content:'';position:absolute;inset:8px;border:0.5px solid rgba(201,168,76,.45);pointer-events:none;z-index:0}

/* HEADER — double gold rule, Mushaf-style */
.ph{margin-bottom:4px;position:relative;z-index:1}
.ph-bar{
  display:flex;justify-content:space-between;align-items:center;
  background:#f8f0dc;
  border-top:2px solid #8b6c14;border-bottom:2px solid #8b6c14;
  box-shadow:inset 0 2px 0 #e8d49a,inset 0 -2px 0 #e8d49a;
  padding:5px 8px;
}
.ph-juz{font-size:9px;color:#7a5810;letter-spacing:1.2px;font-weight:700;text-transform:uppercase;min-width:58px}
.ph-center{display:flex;align-items:center;gap:10px}
.ph-orn{font-size:15px;color:#c9a84c;line-height:1}
.ph-name{font-size:13px;font-weight:700;letter-spacing:2.5px;color:#1a0e04;text-transform:uppercase}
.ph-pg{font-size:9px;color:#7a5810;text-align:right;min-width:58px;letter-spacing:.8px;font-weight:700}

/* SURAH BAND — warm gold gradient, ornamental corners */
.surah-band{
  background:linear-gradient(135deg,#f4e8c4 0%,#ede0aa 50%,#f4e8c4 100%);
  border-top:1px solid #c9a84c;border-bottom:1px solid #c9a84c;
  padding:8px 30px 7px;text-align:center;position:relative;margin-bottom:2px;
}
.surah-band::before,.surah-band::after{content:'❖';position:absolute;top:50%;transform:translateY(-50%);color:#c9a84c;font-size:11px}
.surah-band::before{left:9px}.surah-band::after{right:9px}
.surah-band-ar{font-family:'Amiri',serif;font-size:21px;direction:rtl;color:#1a0e04;margin-bottom:3px;letter-spacing:1px}
.surah-band-info{font-size:10px;color:#7a5810;letter-spacing:.5px}

/* BISMILLAH — prominent, sacred */
.bism-row{
  background:linear-gradient(to right,#fdf7ed,#f5ead0,#fdf7ed);
  border-top:0.5px solid #c9a84c;border-bottom:0.5px solid #c9a84c;
  padding:9px 14px 7px;text-align:center;margin-bottom:3px;
}
.bism-tr{font-size:8.5px;font-style:italic;color:#a07830;margin-bottom:4px;letter-spacing:1.5px}
.bism-ar{font-family:'Amiri',serif;font-size:34px;direction:rtl;color:rgba(0,0,0,.12);line-height:1.6}

/* BODY */
.body{display:flex;flex:1;border:1px solid #d4b870;background:#fdf7ed}

/* LEFT — parchment margin notes */
.mc{width:24%;min-width:24%;border-right:1px solid #d4b870;background:#f7edd8;padding:7px 6px;display:flex;flex-direction:column}
.me{display:flex;flex-direction:column;align-items:center;padding:6px 2px 8px;border-bottom:1px dashed #d4b870}
.me:last-child{border-bottom:none}
.vb{font-size:8px;font-weight:700;color:#8b6c14;border:1px solid #c9a84c;border-radius:50%;width:15px;height:15px;display:inline-flex;align-items:center;justify-content:center;margin-bottom:4px;flex-shrink:0;background:#fdf7ed}
.mp{font-size:10px;font-style:italic;color:#2a1a06;text-align:center;line-height:1.6}

/* RIGHT — word rows, NO heavy box borders — Mushaf line feel */
.wc{flex:1;display:flex;flex-direction:column;padding:5px 8px 3px;gap:0}

/* Each row = one Mushaf line — bottom hairline only */
.word-row{display:flex;flex-direction:row-reverse;border-bottom:0.5px solid #e4d4b0;padding:1px 0;background:transparent}
.word-row:last-child{border-bottom:none}

/* Word cell */
.word-cell{flex:1;display:flex;flex-direction:column;position:relative;padding:0 3px}

/* Gold verse boundary — between last word of verse N and first word of verse N+1 */
.verse-start{border-right:1.5px solid #c9a84c}

/* Verse number medallion — Mushaf gold style */
.verse-start::before{
  content:attr(data-verse);
  position:absolute;top:3px;right:-1px;
  font-family:'EB Garamond',serif;font-size:6.5px;font-weight:700;
  color:#fff;
  background:radial-gradient(circle at 38% 32%,#e8c050,#8b6000);
  border-radius:50%;width:13px;height:13px;
  display:flex;align-items:center;justify-content:center;
  z-index:2;box-shadow:0 1px 3px rgba(0,0,0,.28);
  border:0.5px solid #c9a84c;
}

/* TRANSLITERATION — top, warm amber */
.translit{font-family:'EB Garamond',serif;font-size:7.5px;font-style:italic;color:#a07830;text-align:center;padding:3px 2px 1px;min-height:14px;display:flex;align-items:center;justify-content:center;letter-spacing:.1px}

/* Horizontal hairline dividers */
.cdiv{height:0.5px;background:#e4d0a8;margin:0 4px}

/* ARABIC — visual king, largest element */
.arabic{font-family:'Amiri',serif;font-size:27px;direction:rtl;text-align:center;padding:7px 4px 4px;flex:1;display:flex;align-items:center;justify-content:center;color:rgba(0,0,0,.13);line-height:1.5}

/* MEANING — bottom, warm dark */
.meaning{font-family:'EB Garamond',serif;font-size:8px;text-align:center;color:#1e1206;padding:2px 2px 4px;min-height:18px;display:flex;align-items:center;justify-content:center;line-height:1.25}

/* FOOTER — gold rule matching header */
.pf{padding-top:5px;border-top:2px solid #8b6c14;display:flex;justify-content:space-between;font-size:9px;color:#7a5810;margin-top:7px;letter-spacing:.6px;font-weight:600}

@media print{body{background:#fdf7ed;padding:0;gap:0}.page{box-shadow:none;border-color:#8b6c14;page-break-after:always}.page::before{display:none}}
"""

# ── FULL HTML ─────────────────────────────────────────────────────────────
def build_html():
    pages_html = '\n\n'.join(render_page(p) for p in PAGES)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1.0"/>
  <title>Traceable Quran — 5 Page Preview</title>
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
    print(f"Generated sample-page.html ({len(html):,} chars, ~{len(html)//1000}KB)")
