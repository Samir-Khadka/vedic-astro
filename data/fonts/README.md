# Fonts vendored for the PDF fallback

- NotoSansDevanagari-Regular.ttf, NotoSansDevanagari-Bold.ttf
  Source: Google Noto fonts, SIL Open Font License 1.1.
- DejaVuSans.ttf, DejaVuSans-Bold.ttf
  Source: DejaVu fonts, free license (see DejaVu LICENSE).
- Purpose: the PDF fallback in astro/pdf.py uses fpdf2 + uharfbuzz
  so Nepali text shapes correctly even when WeasyPrint's system
  libraries (Pango) are absent. Noto Sans Devanagari covers Devanagari
  but not full Latin, so words are set in DejaVu Sans when they contain
  no Devanagari characters. System copies are used if these files are
  ever removed; the fallback then degrades to the English-only
  reportlab path.
