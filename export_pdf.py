#!/usr/bin/env python3
"""
Generate a print-ready PDF of the Traceable Quran Para 1.

Strategy:
  - Use local font files (avoid slow Google Fonts CDN).
  - Override @font-face declarations to point at local TTFs.
  - WeasyPrint renders 18-page A4 PDF.
"""
import sys, time
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

BASE      = Path(__file__).parent
HTML_FILE = BASE / 'sample-page.html'
PDF_FILE  = BASE / 'Traceable-Quran-Para1.pdf'
FONT_DIR  = BASE / 'fonts'

PDF_OVERRIDES = f"""
@font-face {{
  font-family: 'Amiri';
  font-weight: 400;
  src: url('file://{FONT_DIR}/Amiri-Regular.ttf') format('truetype');
}}
@font-face {{
  font-family: 'Amiri';
  font-weight: 700;
  src: url('file://{FONT_DIR}/Amiri-Bold.ttf') format('truetype');
}}
@font-face {{
  font-family: 'EB Garamond';
  font-weight: 400;
  font-style: normal;
  src: url('file://{FONT_DIR}/EBGaramond-Regular.ttf') format('truetype');
}}
@font-face {{
  font-family: 'EB Garamond';
  font-weight: 400;
  font-style: italic;
  src: url('file://{FONT_DIR}/EBGaramond-Italic.ttf') format('truetype');
}}
@font-face {{
  font-family: 'EB Garamond';
  font-weight: 600;
  src: url('file://{FONT_DIR}/EBGaramond-SemiBold.ttf') format('truetype');
}}

@page {{ size: A4; margin: 0; }}
body  {{ background: #fdf7ed !important; padding: 0 !important; gap: 0 !important; }}
.page {{
  box-shadow: none !important;
  margin: 0 !important;
  page-break-after: always;
  border: 1.5px solid #c9a84c !important;
}}
.page:last-of-type {{ page-break-after: auto; }}
.page::before {{ display: none !important; }}
"""

def main():
    if not HTML_FILE.exists():
        sys.exit(f"Missing {HTML_FILE} — run generate.py first.")

    print(f"Rendering {HTML_FILE.name} -> {PDF_FILE.name}...")
    t0 = time.time()

    fc = FontConfiguration()
    HTML(filename=str(HTML_FILE)).write_pdf(
        target=str(PDF_FILE),
        stylesheets=[CSS(string=PDF_OVERRIDES, font_config=fc)],
        font_config=fc,
    )

    dt = time.time() - t0
    size = PDF_FILE.stat().st_size
    print(f"Done in {dt:.0f}s.  Wrote {PDF_FILE.name}  ({size:,} bytes / {size/1024:.0f} KB)")

if __name__ == '__main__':
    main()
