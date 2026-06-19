#!/usr/bin/env python3
"""
Urdu (script) -> Roman Urdu transliterator.
Strategy: curated dictionary for the most frequent Quranic word-glosses
(perfect quality), plus a rule-based fallback for the long tail.
"""

# ── Curated dictionary: common Quranic Urdu glosses -> Roman Urdu ──
DICT = {
 'سے':'se','میں':'mein','نہیں':'nahin','بیشک':'beshak','جو':'jo','اور نہ':'aur na',
 'مگر':'magar','اللہ':'Allah','وہ':'woh','کہ':'ke','اور نہیں':'aur nahin','پر':'par',
 'نہ':'na','یا':'ya','اللہ کے':'Allah ke','جب':'jab','پھر':'phir','طرف':'taraf',
 'اللہ تعالیٰ':'Allah Ta\u2019ala','اس میں':'is mein','وہ لوگ':'woh log','اگر':'agar',
 'میں سے':'mein se','یہ':'ye','اللہ کی':'Allah ki','اور وہ':'aur woh','اللہ نے':'Allah ne',
 'ان کے لیے':'un ke liye','ساتھ اس کے':'saath us ke','بیشک وہ':'beshak woh','اور جب':'aur jab',
 'تمہارے لیے':'tumhare liye','ہر':'har','اور اگر':'aur agar','ان پر':'un par','اوپر':'upar',
 'اس سے':'is se','کہا':'kaha','اور جو':'aur jo','اور اللہ':'aur Allah','کوئی':'koi',
 'اس پر':'is par','ہے':'hai','کہہ دیجیے':'keh dijiye','کہہ دیجئے':'keh dijiye',
 'جنہوں نے کفر کیا':'jinhon ne kufr kiya','اس کے لیے':'is ke liye','وہ جو':'woh jo',
 'انہوں نے کہا':'unhon ne kaha','تم پر':'tum par','عذاب':'azaab','جو ایمان لائے':'jo iman laye',
 'اے':'ae','اور بیشک':'aur beshak','کے':'ke','زمین':'zameen','یہاں تک کہ':'yahan tak ke',
 'اور وہ لوگ':'aur woh log','اور البتہ تحقیق':'aur albatta tehqeeq','ان سے':'un se',
 'ساتھ اس کے جو':'saath us ke jo','بیشک میں':'beshak main','کتاب':'kitaab','بلکہ':'balke',
 'تحقیق':'tehqeeq','تھے وہ':'the woh','بعد':'baad','ان میں سے':'un mein se','بیشک ہم':'beshak hum',
 'پھر جب':'phir jab','اس کو':'us ko','پھر اگر':'phir agar','ان لوگوں کو':'un logon ko',
 'ہو تم':'ho tum','دن':'din','اللہ سے':'Allah se','تو بیشک':'to beshak','اللہ کا':'Allah ka',
 'اور جو کوئی':'aur jo koi','نام':'naam','کے ساتھ':'ke saath','ساتھ':'saath','نے':'ne',
 'کو':'ko','کی':'ki','کا':'ka','ان':'un','اس':'is','ہم':'hum','تم':'tum','میرے':'mere',
 'تمہیں':'tumhein','انہیں':'unhein','ایمان':'iman','رب':'Rabb','لوگ':'log','لوگوں':'logon',
 'اور':'aur','تو':'to','ہیں':'hain','ہو':'ho','تھا':'tha','تھے':'the','گا':'ga','گے':'ge',
 'دیا':'diya','کیا':'kiya','کرتے':'karte','کرنے':'karne','والے':'wale','والا':'wala',
 'والوں':'walon','رحم':'rahm','رحمان':'Rehman','رحیم':'Raheem','تعریف':'tareef',
 'جنت':'jannat','جہنم':'jahannam','آگ':'aag','نور':'noor','حق':'haq','دین':'deen',
 'نماز':'namaz','رزق':'rizq','غیب':'gaib','مومن':'momin','کافر':'kafir','کفر':'kufr',
 'نبی':'nabi','رسول':'rasool','کتابیں':'kitabein','آسمان':'aasman','آسمانوں':'aasmanon',
 'زمینوں':'zameenon','پانی':'paani','دل':'dil','دلوں':'dilon','آنکھیں':'aankhein',
 'ہاتھ':'haath','قوم':'qaum','بندے':'bande','بندوں':'bandon',
}

# ── Rule-based fallback ──
# digraphs first (longest match), then single letters.
_MAP = [
 ('ٹھ','Th'),('ڈھ','Dh'),('چھ','chh'),('کھ','kh'),('گھ','gh'),('پھ','ph'),('بھ','bh'),
 ('تھ','th'),('دھ','dh'),('جھ','jh'),('ڑھ','rh'),('شھ','sh'),
 ('آ','aa'),('اّ','a'),
 ('ا','a'),('ب','b'),('پ','p'),('ت','t'),('ٹ','t'),('ث','s'),('ج','j'),('چ','ch'),
 ('ح','h'),('خ','kh'),('د','d'),('ڈ','d'),('ذ','z'),('ر','r'),('ڑ','r'),('ز','z'),
 ('ژ','zh'),('س','s'),('ش','sh'),('ص','s'),('ض','z'),('ط','t'),('ظ','z'),('ع','a'),
 ('غ','gh'),('ف','f'),('ق','q'),('ک','k'),('گ','g'),('ل','l'),('م','m'),('ن','n'),
 ('ں','n'),('و','o'),('ہ','h'),('ھ','h'),('ۃ','h'),('ء',"'"),('ی','i'),('ے','e'),
 ('ئ','i'),('ؤ','o'),('آ','aa'),('ك','k'),('ي','i'),('ٰ','a'),('ۂ','h'),('ۓ','e'),
]
_DIAC = '\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670'
_VOWELS = set('aeiou')

def _map_char(w, i):
    for src,dst in _MAP:
        if w[i:i+len(src)]==src:
            return dst, len(src)
    return w[i], 1

def _translit_word(w):
    w = ''.join(c for c in w if c not in _DIAC)
    # positional: leading و -> w, leading ی -> y
    out=''
    i=0; first=True
    while i < len(w):
        ch=w[i]
        if first and ch=='و': dst,ln='w',1
        elif first and ch=='ی': dst,ln='y',1
        else: dst,ln=_map_char(w,i)
        # short-vowel insertion: consonant after consonant -> insert 'a'
        if out and dst and out[-1] not in _VOWELS and dst[0] not in _VOWELS \
           and out[-1] not in "'" and dst[0] not in "'":
            out+='a'
        out+=dst
        i+=ln; first=False
    # tidy doubled vowels / trailing artifacts
    out=out.replace('aa a','aa ').replace('iy','i').replace('uw','u')
    return out

def to_roman(urdu):
    urdu=(urdu or '').strip()
    if not urdu: return ''
    if urdu in DICT: return DICT[urdu]
    # transliterate token by token, applying dict to each token where possible
    toks=urdu.split()
    out=[]
    for t in toks:
        out.append(DICT.get(t, _translit_word(t)))
    return ' '.join(out)
