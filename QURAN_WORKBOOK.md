# Traceable Quran Workbook — Complete Project Documentation

> **This file is your master reference for everything built, how it works, how to update it, and how to request new editions.**

---

## Table of Contents

1. [Project Summary](#1-project-summary)
2. [What Was Built](#2-what-was-built)
3. [File Structure](#3-file-structure)
4. [Data Sources](#4-data-sources)
5. [Typography & Design](#5-typography--design)
6. [Page Layout System](#6-page-layout-system)
7. [How to Regenerate Any File](#7-how-to-regenerate-any-file)
8. [How to Make Changes](#8-how-to-make-changes)
9. [In-Browser Editing Guide](#9-in-browser-editing-guide)
10. [How to Add a New Language/Edition](#10-how-to-add-a-new-languageedition)
11. [Front & Back Matter](#11-front--back-matter)
12. [Known Limitations & Future Work](#12-known-limitations--future-work)
13. [Complete Change Log](#13-complete-change-log)

---

## 1. Project Summary

**The Traceable Quran** is a complete, print-ready word-by-word Quran tracing and learning workbook.

| Spec | Value |
|---|---|
| Surahs | All 114 |
| Juz (Paras) | All 30 |
| Verses | 6,236 |
| Arabic words | 77,429 (each individually traceable) |
| Pages (English edition) | 1,647 (complete single book) |
| Pages (Roman Urdu edition) | 1,898 across all 30 Juz files |
| Format | A4, print-ready HTML with embedded fonts |
| Arabic script | Uthmani, Hafs ʿan ʿAsim narration |
| Arabic font | Amiri (Khaled Hosny, SIL OFL) |
| English translation | Saheeh International |
| Roman Urdu translation | Mawdudi (Abul Ala Maududi), id 831 |
| Offline capable | Yes — all fonts embedded in every file |

---

## 2. What Was Built

### English Edition
- **30 individual Juz files** → `juz/Juz-01.html` … `juz/Juz-30.html`
- **Front Matter** (18 pages) → `juz/Front-Matter.html`
- **Back Matter** (5 pages) → `juz/Back-Matter.html`
- **Complete single-file book** (1,647 pages) → `Traceable-Quran-Complete.html`

### Roman Urdu Edition
- **30 individual Juz files** → `juz/Juz-01-Urdu.html` … `juz/Juz-30-Urdu.html`

### Master Index
- `juz/index.html` — interactive, editable index with language toggle (English ↔ Roman Urdu)

### In every file
- **Edit Mode toolbar** — click any text to edit it live
- **Color tool** — 5 theme presets + custom color pickers for every element
- **Export button** — download your edited version permanently

---

## 3. File Structure

```
Traceable-Quran-Shareef/
│
│  ── CORE DATA ──────────────────────────────────────────
├── quran_data.json          Arabic text + transliteration + English meanings
│                            + verse meanings (Saheeh Int'l) + ruku numbers
├── quran_urdu.json          Urdu-script word meanings + Roman Urdu verse
│                            meanings (Maududi) for all 6,236 verses
│
│  ── BUILD SCRIPTS ──────────────────────────────────────
├── fetch_all.py             Fetches quran_data.json from quran.com API
├── fetch_urdu.py            Fetches quran_urdu.json (Roman Urdu Maududi + Urdu words)
├── build_all.py             Generates all 30 English Juz files
├── build_urdu.py            Generates all 30 Roman Urdu Juz files
├── build_front_back.py      Generates Front-Matter.html + Back-Matter.html
├── compile_book.py          Compiles all parts into Traceable-Quran-Complete.html
├── urdu_roman.py            Urdu-script → Roman Urdu transliterator
│
│  ── OUTPUT FILES ───────────────────────────────────────
├── Traceable-Quran-Complete.html     ← SINGLE COMPLETE BOOK (English, 1,647 pp)
│
├── juz/
│   ├── index.html           Master index (editable, language toggle)
│   ├── Front-Matter.html    18-page front matter
│   ├── Back-Matter.html     5-page back matter
│   ├── Juz-01.html … Juz-30.html     English edition (30 files)
│   └── Juz-01-Urdu.html … Juz-30-Urdu.html  Roman Urdu edition (30 files)
│
│  ── FONTS (embedded in every HTML file) ────────────────
├── fonts/
│   ├── Amiri-Regular.woff2       Arabic text
│   ├── Amiri-Bold.woff2
│   ├── EBGaramond-Regular.woff2  Latin text (transliteration, meanings)
│   ├── EBGaramond-Italic.woff2
│   └── EBGaramond-SemiBold.woff2
```

---

## 4. Data Sources

### Arabic Text
| Property | Detail |
|---|---|
| Script | Uthmani (Rasm Uthmani) |
| Narration | Hafs ʿan ʿAsim |
| Harakat | Full diacritics included |
| Source | quran.com word-by-word API |
| API endpoint | `api.quran.com/api/v4/verses/by_chapter/{ch}?words=true&word_fields=text_uthmani,transliteration,translation&translations=20` |

### English Verse Meanings
- **Translation**: Saheeh International
- **API translation ID**: `20`
- **Publisher**: Abul Qasim Publishing House, Jeddah (1997, rev. 2004)

### Roman Urdu Verse Meanings
- **Translation**: Mawdudi (Abul Ala Maududi) — Roman Urdu
- **API translation ID**: `831`

### Word-by-Word English Meanings
- Source: quran.com word-by-word database
- Root lexicons: *Lisan al-Arab* (Ibn Manzur), *Al-Mufradat* (Al-Isfahani)

### Word-by-Word Roman Urdu Meanings
- Source: quran.com Urdu-script word glosses (`language=ur`)
- Converted to Roman Urdu via `urdu_roman.py`
- Common words (top ~200) use a curated hand-mapped dictionary (perfect quality)
- Remaining words use rule-based transliteration (readable, approximate)

### Ruku Numbers
- Source: quran.com API `fields=ruku_number`
- Used to place the traditional Ruku-end marker (green ع + number)

---

## 5. Typography & Design

### Fonts
| Font | Use | License |
|---|---|---|
| Amiri (Khaled Hosny) | Arabic text | SIL Open Font License |
| EB Garamond (Georg Duffner) | All Latin text | SIL Open Font License |

### Color Palette
```
Page background:   #fdf7ed  (ivory parchment)
Panel background:  #f6ead6  (warm cream)
Header background: #f8f0dc
Gold / accent:     #c9a84c
Arabic trace:      rgba(0,0,0,0.18) — light gray for tracing
Transliteration:   #a07830  (amber)
Word meaning:      #1e1206  (dark brown)
Verse meaning:     #2a1a06
Ruku marker:       #1a7a4a  (green)
```

### Three-Layer Word Cell
```
┌─────────────────────┐
│   bis'mi            │  ← Transliteration (10pt italic amber)
│                     │
│   بِسْمِ             │  ← Arabic trace (20pt Amiri, 0.18 opacity)
│                     │
│   In the name       │  ← Meaning (10pt EB Garamond)
└─────────────────────┘
```

### Page Dimensions
```
Page:         A4 (210 × 297 mm)
Padding:      12mm all sides
Border:       0.5mm solid gold (#c9a84c) — double frame
Header:       14mm
Footer:       10mm
Body:         248mm  (= page − padding − border − header − footer)
Left panel:   22% of body width (verse meanings)
Word area:    78% of body width
```

### Adaptive Cell Widths
Cell width is proportional to the Arabic word's base character count:
```python
cell_width = max(12mm, min(word_area_width,
  max(arabic_chars × 3.3mm, translit_longest_token × 1.7mm,
      meaning_longest_token × 1.7mm) + 3mm_padding))
```
Short words (في, لا) get less space. Long words (ٱلْمُسْتَقِيمَ) get more.

---

## 6. Page Layout System

### Three Page Types

**Type A — Juz Opening Page**
Full-page decorative spread. Large Juz number, Arabic label, introduction text, key themes.

**Type B — Surah Opening Page**
Full-page Surah card. Arabic name (40pt), English name, Makki/Madani, verse count, overview, Bismillah.
*(Surah 9 At-Tawbah: Bismillah is correctly absent.)*

**Type C — Standard Workbook Page**
- Left column (22%): Verse meanings (panel)
- Right column (78%): Word rows (tracing area)

### Pagination Logic
1. Words flow continuously across verse boundaries (dense rows)
2. Rows are packed until `BODY_H - 2mm` is filled
3. `break-inside: avoid` on every row — no row ever splits across pages
4. Verses longer than one full page (2:61, 2:85, 2:102) span pages — Mushaf-style
5. Panel meanings flow across pages when a verse is too long for one panel column

### Ruku Markers
The end of every Ruku is marked with:
- ع in green (#1a7a4a)
- The sequential ruku number within that Juz (in small text)

Juz 1 has 17 Rukus. Other Juz have their own counts computed automatically.

---

## 7. How to Regenerate Any File

All scripts are in the root of the repository.

### Re-fetch all Quran data (if API changes)
```bash
python3 fetch_all.py        # regenerates quran_data.json
python3 fetch_urdu.py       # regenerates quran_urdu.json
```

### Regenerate English Juz files
```bash
python3 build_all.py                  # all 30 Juz
python3 build_all.py 1 2 3            # specific Juz numbers
python3 build_all.py 15               # single Juz
```

### Regenerate Roman Urdu Juz files
```bash
python3 build_urdu.py                 # all 30 Juz → Juz-NN-Urdu.html
python3 build_urdu.py 1 5 10          # specific Juz
```

### Regenerate Front & Back Matter
```bash
python3 build_front_back.py
# outputs: juz/Front-Matter.html, juz/Back-Matter.html
```

### Compile complete single-file book (English)
```bash
python3 compile_book.py
# outputs: Traceable-Quran-Complete.html (1,647 pages)
```

### Full rebuild from scratch
```bash
python3 fetch_all.py
python3 fetch_urdu.py
python3 build_all.py
python3 build_urdu.py
python3 build_front_back.py
python3 compile_book.py
```

---

## 8. How to Make Changes

### Change font sizes
In `build_all.py`, near the top:
```python
AR_PT  = 20   # Arabic tracing text
TR_PT  = 10   # Transliteration
MN_PT  = 10   # Word meaning
PANEL_TXT_PT = 11   # Verse meaning in left panel
```
Change any value, then regenerate.

### Change Arabic trace opacity
In `build_all.py` CSS:
```css
--c-arabic: rgba(0,0,0,0.18)
```
Increase for darker trace (easier to see). Decrease for lighter (easier to trace over).

### Change number of words per row
In `build_all.py`:
```python
# In build_juz():
rows_pages = B.paginate(B.pack(B.make_items(vks, rmap)))
```
The packing is controlled by `WORD_W` (word-area width in mm). To force narrower rows, reduce this. To force more words per row, either increase `WORD_W` or reduce `AR_CHAR_MM`.

### Change left panel width
```python
PANEL_PCT = 22   # change to 25, 30, etc.
```

### Add or edit a Front/Back Matter page
All front/back matter page functions are in `build_front_back.py`:
- `p_cover()` — cover page
- `p_title()` — title page
- `p_copyright()` — copyright
- `p_preface()` — preface
- `p_how_to_use()` — how to use
- `p_methodology()` — methodology
- `p_transliteration_guide()` — transliteration
- `p_symbols()` — symbols guide
- `p_learning_roadmap()` — roadmap
- `p_quran_structure()` — Quran overview
- `p_about_arabic_text()` — Arabic text details *(NEW)*
- `p_about_translation()` — translation details *(NEW)*
- `p_juz_index()` — Juz index
- `p_surah_index_1()`, `p_surah_index_2()` — Surah index
- `p_introduction()` — introduction
- `p_virtues()` — virtues of learning
- `p_etiquettes()` — etiquettes
- `p_khatm()` — Khatm page
- `p_dua_khatm()` — Dua after Khatm
- `p_reflection()` — reflection page
- `p_about_workbook()` — technical specs
- `p_final_message()` — closing message

To add a new page: write a new `p_yourpage()` function using the same helpers (`section()`, `para()`, `ul()`, `hadith()`, etc.) and add it to the `front` or `back` list in `main()`.

### Change the verse translation (English)
To use a different English translation, find its ID at `api.quran.com/api/v4/resources/translations` and change in `fetch_all.py`:
```python
f'&translations=20'   # 20 = Saheeh International
```
Re-run `fetch_all.py` then rebuild.

### Change the Roman Urdu verse translation
The current translation is Mawdudi (id 831). To switch:
```python
# In fetch_urdu.py:
f'&translations=831'
```
Other Urdu options:
- 97 — Tafheem e Quran, Mawdudi (Urdu script)
- 54 — Maulana Junagarhi
- 234 — Jalandhari
- 819 — Wahiduddin Khan

---

## 9. In-Browser Editing Guide

Every HTML file includes a built-in **Edit toolbar** at the top.

### How to use Edit Mode
1. Download any file and open in Chrome (local file, not online preview)
2. Click **✎ Edit Mode** — turns green
3. Click any text to edit it directly:
   - Arabic words (gray trace text)
   - Transliterations
   - Word meanings
   - Verse meanings (left panel)
   - Surah names, Juz titles, headers
4. Changes **auto-save** to browser storage as you type
5. Reopen the file later — edits are still there (per file, per browser)

### Buttons
| Button | Action |
|---|---|
| ✎ Edit Mode | Toggle editing on/off |
| 🎨 Colors | Open live color customization panel |
| ↺ Reset | Clear all edits, restore original |
| ⤓ Save / Export | Download a standalone HTML with edits baked in |

### Color Tool
Click **🎨 Colors** to open the color panel:
- **5 preset themes**: Ivory (default), White, Sepia, Night, Mint
- **Custom pickers** for: sheet background, word area, panel, header, accent/gold, Arabic trace, transliteration, word meaning, verse meaning
- **Arabic darkness slider**: control how light/dark the traceable Arabic appears

---

## 10. How to Add a New Language/Edition

To generate a new edition (e.g., Turkish, French, Indonesian):

**Step 1 — Find translation IDs at quran.com:**
```
GET api.quran.com/api/v4/resources/translations
GET api.quran.com/api/v4/resources/translations?language=tr   (Turkish example)
```

**Step 2 — Create a fetch script** (copy `fetch_urdu.py`, change translation ID and language code)

**Step 3 — Create a build script** (copy `build_urdu.py`, change:)
```python
ur = json.loads((BASE/'quran_NEWLANG.json').read_text(encoding='utf-8'))
B.VARIANT = '-Turkish'           # output suffix
B.TITLE_SUFFIX = ' (Turkish)'   # page title
```

**Step 4 — If the language uses a non-Latin script**, create a transliterator (like `urdu_roman.py`) or use Latin-script API data directly.

**Step 5 — Regenerate:**
```bash
python3 fetch_NEWLANG.py
python3 build_NEWLANG.py
```

**Step 6 — Add to the index** in `juz/index.html` — add a third language state to `toggleLang()`.

---

## 11. Front & Back Matter

### Front Matter (18 pages — `juz/Front-Matter.html`)
| Page | Title |
|---|---|
| i | Cover |
| ii | Title Page |
| iii | Copyright |
| iv | Preface |
| v | How to Use This Workbook |
| vi | Workbook Methodology |
| vii | Transliteration Guide |
| viii | Symbols & Conventions |
| ix | Learning Roadmap |
| x | Qur'an Structure Overview |
| xi | About the Arabic Text *(script, narration, Amiri font)* |
| xii | About the Translation & Meanings *(Saheeh Int'l, Mawdudi, lexicons)* |
| xiii | Juz Index |
| xiv | Surah Index (1–57) |
| xv | Surah Index (58–114) |
| xvi | Introduction to the Qur'an |
| xvii | Virtues of Learning the Qur'an |
| xviii | Etiquettes of Qur'an Study |

### Back Matter (5 pages — `juz/Back-Matter.html`)
| Page | Title |
|---|---|
| 1630 | Khatm ul-Qur'an (with date/witness fields) |
| 1631 | Du'a After Completing the Qur'an |
| 1632 | Reflection Page |
| 1633 | About This Workbook |
| 1634 | Final Closing Message |

### Complete Book
`Traceable-Quran-Complete.html` — all 1,647 pages in one file.
- Front matter: roman numerals (i … xviii)
- Body: arabic numerals (1 … 1624)
- Back matter: arabic continues (1625 … 1647)
- Juz Index and Surah Index show real page numbers
- No file names, no links, no digital references — pure printed book

---

## 12. Known Limitations & Future Work

### Current limitations

| Issue | Detail | How to fix |
|---|---|---|
| Word-by-word Roman Urdu quality | Rule-based transliteration is approximate for uncommon words | Expand the `DICT` in `urdu_roman.py` |
| Transliteration style | Uses quran.com convention (not ISO 233 or ALA-LC) | Would require re-mapping all 77,429 words |
| Tajweed rules | Cannot be represented in transliteration — oral instruction required | Outside scope |
| Gap pages | ~11 pages per 30-Juz set where a Juz ends with < 40% fill | Structural — unavoidable with verse-complete pagination |
| Juz 30 page count | 102 pages due to 37 surahs each getting a surah opener | Could combine opener + first content page for short surahs |
| Roman Urdu complete book | Not yet compiled as a single file | Run: `python3 build_urdu.py` then adapt `compile_book.py` |
| PDF export | Requires Chrome print-to-PDF (no server-side PDF tool available) | Use Playwright/Puppeteer if server-side PDF is needed |

### Suggested future editions
- [ ] Complete Roman Urdu single-book compilation
- [ ] Urdu-script edition (replace meanings with Urdu script)
- [ ] Turkish, Indonesian, French, Spanish editions
- [ ] Juz-by-Juz audio integration (word-by-word audio via quran.com)
- [ ] Larger print edition (26pt+ Arabic for elderly readers)
- [ ] Children's edition (fewer words per row, larger font)
- [ ] Tajweed-color edition (color-coded Tajweed rules on Arabic)

---

## 13. Complete Change Log

### Phase 1 — Foundation
- Built the HTML/CSS page template from scratch (A4, gold Mushaf border)
- Developed 3 page types: Juz opener, Surah opener, Standard workbook
- Established CSS variable system for live color theming

### Phase 2 — Content Engine
- Fetched complete Quran data (6,236 verses, 77,429 words) from quran.com
- Built greedy RTL row-packing algorithm (words fill rows across ayah boundaries)
- Built adaptive cell-width system (Arabic char count drives width)
- Built pre-computed pagination (no row ever splits across a page)

### Phase 3 — Features
- Added inline Ayah markers (۝ + Arabic-Indic numerals) at verse ends
- Added Ruku-end markers (green ع + ruku number per Juz)
- Built panel carry-over system — long verse meanings flow across pages (0 truncations)
- Fixed Surah 9 (At-Tawbah) Bismillah correctly absent

### Phase 4 — Quality Assurance
- Full programmatic audit: 0 missing verses, 0 encoding errors, 0 truncations, 0 overflow
- Fixed HTML footnote codes (`<sup foot_note=...>`) — stripped from all 6,236 verses
- Verified word alignment between English and Urdu datasets: 0 mismatches

### Phase 5 — Complete Book
- Built 18-page Front Matter (cover, preface, indexes, introduction, virtues, etiquettes)
- Built 5-page Back Matter (Khatm, Du'a, reflection, about, closing)
- Compiled single-file complete book (1,647 pages, roman+arabic page numbers, real indexes)
- No file names, no digital references in the compiled book

### Phase 6 — Interactive Features
- Added Edit Mode to every file (click any text to edit, auto-save, export)
- Added Color Tool (5 presets + 9 custom color pickers, Arabic darkness slider)
- Built editable Master Index with language toggle
- Added per-file localStorage persistence for edits and themes

### Phase 7 — Roman Urdu Edition
- Fetched Mawdudi Roman Urdu translation (id 831) for all 6,236 verses
- Fetched Urdu-script word glosses for all 77,429 words
- Built `urdu_roman.py` — curated dictionary + rule-based transliterator
- Generated all 30 Roman Urdu Juz files (1,898 pages) — English unchanged
- Added language toggle to Master Index

---

## Quick Reference Card

```
TO PRINT A JUZ:
  1. Download juz/Juz-NN.html (or Juz-NN-Urdu.html)
  2. Open in Chrome
  3. Ctrl+P → Save as PDF
     • Paper: A4
     • Margins: None
     • ☑ Background graphics

TO EDIT TEXT IN A JUZ:
  1. Download and open in Chrome
  2. Click ✎ Edit Mode
  3. Click any text → type
  4. Click ⤓ Save/Export when done

TO CHANGE COLORS:
  1. Click 🎨 Colors
  2. Pick a preset or adjust custom pickers
  3. Click ⤓ Save/Export to keep changes

TO REGENERATE ALL FILES:
  python3 build_all.py          # English, all 30
  python3 build_urdu.py         # Roman Urdu, all 30
  python3 build_front_back.py   # front + back matter
  python3 compile_book.py       # complete single book

TO ADD A NEW TRANSLATION:
  → See Section 10 of this document
```

---

*This document was last updated as of the current session.*
*All 30 English Juz, all 30 Roman Urdu Juz, Front Matter, Back Matter, and the complete single-file book are on GitHub in the `juz/` folder and root of the repository.*
