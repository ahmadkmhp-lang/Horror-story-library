#!/usr/bin/env python3
"""Convert WO GALI markdown story files to PDF with proper Devanagari shaping."""
import sys
import unicodedata
from fpdf import FPDF
from fpdf.errors import FPDFException


def safe_multi_cell(pdf, h, text, align="L"):
    """Render text top-to-bottom, hard-wrapping any token too wide for the line."""
    from fpdf.enums import XPos, YPos
    try:
        pdf.multi_cell(0, h, text, align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        return
    except FPDFException:
        pass
    epw = pdf.w - pdf.l_margin - pdf.r_margin
    words = text.split(" ")
    safe_words = []
    for w in words:
        if not w:
            safe_words.append(w)
            continue
        while pdf.get_string_width(w) > epw and len(w) > 1:
            cut = len(w)
            while cut > 1 and pdf.get_string_width(w[:cut]) > epw:
                cut -= 1
            safe_words.append(w[:cut])
            w = w[cut:]
        safe_words.append(w)
    rebuilt = " ".join(safe_words)
    try:
        pdf.multi_cell(0, h, rebuilt, align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    except FPDFException:
        for ch in rebuilt:
            try:
                pdf.multi_cell(0, h, ch, align=align, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except FPDFException:
                continue

FONT_DIR = "/projects/sandbox/Horror-story-library/wo-gali-library/fonts"
DEV = f"{FONT_DIR}/NotoSansDevanagari-Static.ttf"

def strip_unsupported(text: str) -> str:
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        # drop emoji / symbols (So) and other pictographs, keep letters/marks/punct/space
        if cat in ("So", "Cs"):
            continue
        if ord(ch) >= 0x1F000:
            continue
        out.append(ch)
    return "".join(out)

class StoryPDF(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-12)
        self.set_font("noto", size=8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"वो गली  -  {self.page_no()}", align="C")

def build(md_path: str, pdf_path: str, title: str):
    pdf = StoryPDF(orientation="P", unit="mm", format="A4")
    pdf.add_font("noto", "", DEV)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(16, 16, 16)
    pdf.add_page()
    pdf.set_text_shaping(True)

    # Title block
    pdf.set_font("noto", size=20)
    pdf.set_text_color(150, 20, 20)
    safe_multi_cell(pdf, 11, strip_unsupported(title), align="C")
    pdf.ln(4)

    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()

    for raw in lines:
        line = strip_unsupported(raw.rstrip("\n"))
        stripped = line.strip()
        if not stripped:
            pdf.ln(3)
            continue
        if set(stripped) <= set("="):
            pdf.ln(1)
            continue
        if set(stripped) <= set("-"):
            pdf.ln(1)
            continue
        if stripped.startswith("STORY ") or stripped.startswith("WO GALI") or stripped.startswith("FILE ") or stripped.startswith("FILM "):
            pdf.ln(2)
            pdf.set_font("noto", size=15)
            pdf.set_text_color(150, 20, 20)
            safe_multi_cell(pdf, 8, stripped, align="L")
            pdf.ln(1)
        elif stripped.startswith("PART ") or stripped.startswith("SEQUENCE "):
            pdf.ln(1)
            pdf.set_font("noto", size=12)
            pdf.set_text_color(20, 60, 130)
            safe_multi_cell(pdf, 7, stripped, align="L")
        elif stripped.startswith("* ") or stripped.startswith("[CHARACTER ANCHOR]") or stripped.startswith("[TARGET RUNTIME]") or stripped.startswith("[VARIETY LOG]") or stripped.startswith("VIRAL SEO") or stripped.startswith("[DNA]"):
            pdf.set_font("noto", size=9)
            pdf.set_text_color(70, 70, 70)
            safe_multi_cell(pdf, 5.2, stripped, align="L")
        elif stripped.startswith("[VO Tone"):
            pdf.set_font("noto", size=10)
            pdf.set_text_color(120, 60, 20)
            safe_multi_cell(pdf, 6, stripped, align="L")
        else:
            pdf.set_font("noto", size=11)
            pdf.set_text_color(15, 15, 15)
            safe_multi_cell(pdf, 6.4, stripped, align="L")

    pdf.output(pdf_path)
    print(f"OK -> {pdf_path}")

if __name__ == "__main__":
    base = "/projects/sandbox/Horror-story-library/wo-gali-library"
    jobs = [
        (f"{base}/WO_GALI_FILE_01.md", f"{base}/pdf/WO_GALI_FILE_01.pdf", "वो गली — FILE 1 (Stories 01-10)"),
        (f"{base}/WO_GALI_FILE_02.md", f"{base}/pdf/WO_GALI_FILE_02.pdf", "वो गली — FILE 2 (Stories 11-20)"),
        (f"{base}/WO_GALI_FILE_03.md", f"{base}/pdf/WO_GALI_FILE_03.pdf", "वो गली — FILE 3 (Stories 21-30)"),
        (f"{base}/WO_GALI_FILE_04.md", f"{base}/pdf/WO_GALI_FILE_04.pdf", "वो गली — FILE 4 (Stories 31-40)"),
        (f"{base}/WO_GALI_FILM_41.md", f"{base}/pdf/WO_GALI_FILM_41.pdf", "वो गली — FILM 41 (Cinematic, 12-15 min)"),
        (f"{base}/WO_GALI_FILM_42.md", f"{base}/pdf/WO_GALI_FILM_42.pdf", "वो गली — FILM 42 : आख़िरी परदा"),
        (f"{base}/WO_GALI_FILM_43.md", f"{base}/pdf/WO_GALI_FILM_43.pdf", "वो गली — FILM 43 : ग्रहण की तेरहवीं घड़ी"),
        (f"{base}/WO_GALI_FILM_44.md", f"{base}/pdf/WO_GALI_FILM_44.pdf", "वो गली — FILM 44 : सफ़ेद रण का घड़ा"),
        (f"{base}/WO_GALI_FILM_45.md", f"{base}/pdf/WO_GALI_FILM_45.pdf", "वो गली — FILM 45 : गिनती की स्लेट"),
        (f"{base}/WO_GALI_FILM_46.md", f"{base}/pdf/WO_GALI_FILM_46.pdf", "वो गली — FILM 46 : पार उतारन"),
        (f"{base}/WO_GALI_FILM_47.md", f"{base}/pdf/WO_GALI_FILM_47.pdf", "वो गली — FILM 47 : मोम के चेहरे"),
        (f"{base}/WO_GALI_FILM_48.md", f"{base}/pdf/WO_GALI_FILM_48.pdf", "वो गली — FILM 48 : आख़िरी कॉल"),
        (f"{base}/WO_GALI_FILM_49.md", f"{base}/pdf/WO_GALI_FILM_49.pdf", "वो गली — FILM 49 : गन्ने का कोल्हू"),
    ]
    for md, pdf, title in jobs:
        build(md, pdf, title)
