#!/usr/bin/env python3
"""Combine multiple WO GALI markdown film files into ONE PDF with Devanagari shaping."""
import sys, unicodedata
from fpdf import FPDF
from fpdf.errors import FPDFException
from fpdf.enums import XPos, YPos

FONT = "/projects/sandbox/pdfbuild/fonts/NotoSansDevanagari-Static.ttf"


def strip_unsupported(text: str) -> str:
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat in ("So", "Cs"):
            continue
        if ord(ch) >= 0x1F000:
            continue
        out.append(ch)
    return "".join(out)


def safe_multi_cell(pdf, h, text, align="L"):
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
            safe_words.append(w); continue
        while pdf.get_string_width(w) > epw and len(w) > 1:
            cut = len(w)
            while cut > 1 and pdf.get_string_width(w[:cut]) > epw:
                cut -= 1
            safe_words.append(w[:cut]); w = w[cut:]
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


class StoryPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("noto", size=8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"वो गली  -  {self.page_no()}", align="C")


def render_md(pdf, md_path):
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()
    for raw in lines:
        line = strip_unsupported(raw.rstrip("\n"))
        stripped = line.strip()
        if not stripped:
            pdf.ln(3); continue
        if set(stripped) <= set("=") or set(stripped) <= set("-") or set(stripped) <= set("\u2550") or set(stripped) <= set("\u2014"):
            pdf.ln(1); continue
        s = stripped.lstrip("#* ").strip()
        if s.startswith("WO GALI") or s.startswith("FILM ") or s.startswith("FILE ") or s.startswith("STORY "):
            pdf.ln(2); pdf.set_font("noto", size=15); pdf.set_text_color(150, 20, 20)
            safe_multi_cell(pdf, 8, s, align="L"); pdf.ln(1)
        elif s.startswith("SEQUENCE") or s.startswith("PART "):
            pdf.ln(1); pdf.set_font("noto", size=12); pdf.set_text_color(20, 60, 130)
            safe_multi_cell(pdf, 7, s, align="L")
        elif stripped.startswith("* ") or s.startswith("[") or s.startswith("VIRAL SEO") or s.startswith("SCENE BREAKDOWN") or s.startswith("IMAGINATION") or s.startswith("2D ANIMATION") or s.startswith("AUDIO"):
            pdf.set_font("noto", size=9); pdf.set_text_color(70, 70, 70)
            safe_multi_cell(pdf, 5.2, stripped.lstrip("*# ").strip(), align="L")
        elif s.startswith("[VO Tone") or stripped.startswith("*[VO"):
            pdf.set_font("noto", size=10); pdf.set_text_color(120, 60, 20)
            safe_multi_cell(pdf, 6, s, align="L")
        else:
            pdf.set_font("noto", size=11); pdf.set_text_color(15, 15, 15)
            safe_multi_cell(pdf, 6.4, stripped, align="L")


def build_combined(md_paths, out_path, cover_title, cover_sub):
    pdf = StoryPDF(orientation="P", unit="mm", format="A4")
    pdf.add_font("noto", "", FONT)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(16, 16, 16)
    pdf.set_text_shaping(True)
    # Cover
    pdf.add_page()
    pdf.ln(60)
    pdf.set_font("noto", size=26); pdf.set_text_color(150, 20, 20)
    safe_multi_cell(pdf, 14, strip_unsupported(cover_title), align="C")
    pdf.ln(4)
    pdf.set_font("noto", size=13); pdf.set_text_color(60, 60, 60)
    safe_multi_cell(pdf, 8, strip_unsupported(cover_sub), align="C")
    # Films
    for mp in md_paths:
        pdf.add_page()
        render_md(pdf, mp)
    pdf.output(out_path)
    print(f"OK -> {out_path} ({len(md_paths)} films)")


if __name__ == "__main__":
    src = "/projects/sandbox/pdfbuild/src"
    films = [f"{src}/WO_GALI_FILM_{n}.md" for n in range(41, 51)]
    build_combined(
        films,
        "/projects/sandbox/pdfbuild/WO_GALI_FILE_05_Films_41_to_50.pdf",
        "वो गली",
        "FILE 5  -  Films 41 to 50  (cinematic)  -  combined",
    )
