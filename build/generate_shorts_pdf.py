#!/usr/bin/env python3
"""Generate combined PDFs for the Wo Gali SHORT_NN markdown packages.

- Full Devanagari + Latin via fpdf2 + uharfbuzz HarfBuzz shaping (Noto fonts).
- One PDF per batch of 10 Shorts (01-10, 11-20, 21-30).
- Cover page, Table of Contents with page numbers, PDF bookmarks, footers.
- 100% of each markdown package preserved (all 10 departments); markdown
  markers (#, *, **) are cleaned for readability but NO text is removed.
"""
import sys, os, glob, re

from fpdf import FPDF

ROOT = os.path.dirname(os.path.dirname(__file__))
LIB = os.path.join(ROOT, "wo-gali-library")
FONTS = os.path.join(os.path.dirname(__file__), "fonts")
DOCS = os.path.join(ROOT, "docs")


def find_short(n):
    hits = glob.glob(os.path.join(LIB, f"SHORT_{n:02d}_*.md"))
    if not hits:
        hits = glob.glob(os.path.join(LIB, f"SHORT_{n}_*.md"))
    return hits[0] if hits else None


def clean(text):
    """Strip markdown emphasis/markers but keep all words."""
    text = text.replace("**", "").replace("`", "")
    return text.strip()


class ShortsPDF(FPDF):
    def __init__(self, doc_title):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.doc_title = doc_title
        self.set_margins(15, 18, 15)
        self.set_auto_page_break(True, margin=18)
        self.add_font("noto", "", os.path.join(FONTS, "NotoSansDevanagari.ttf"))
        self.add_font("noto", "B", os.path.join(FONTS, "NotoSansDevanagari-Bold.ttf"))
        self.add_font("notol", "", os.path.join(FONTS, "NotoSans.ttf"))
        self.add_font("notol", "B", os.path.join(FONTS, "NotoSans-Bold.ttf"))
        self.set_fallback_fonts(["notol"])
        self.set_text_shaping(True)
        self._on_cover = False

    def footer(self):
        if self._on_cover:
            return
        self.set_y(-14)
        self.set_font("notol", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"{self.doc_title}    |    Page {self.page_no()}", align="C")

    def cover(self, subtitle):
        self._on_cover = True
        self.set_text_shaping(False)
        self.add_page()
        self.set_fill_color(10, 10, 12)
        self.rect(0, 0, self.w, self.h, style="F")
        self.set_y(90)
        self.set_text_color(200, 30, 30)
        self.set_font("noto", "B", 30)
        self.cell(0, 16, "WO GALI", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 16, "VIRAL SHORTS", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)
        self.set_text_color(235, 235, 235)
        self.set_font("noto", "B", 20)
        self.cell(0, 12, self.doc_title, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_text_color(150, 150, 150)
        self.set_font("notol", "", 12)
        self.multi_cell(0, 8, subtitle, align="C")
        self._on_cover = False
        self.set_text_shaping(True)

    def render_line(self, raw):
        line = raw.rstrip()
        if not line.strip():
            self.ln(3)
            return
        avail_reset = lambda: self.set_x(self.l_margin)
        if line.startswith("# "):
            # Short title header
            self.ln(2)
            self.set_text_color(200, 30, 30)
            self.set_font("noto", "B", 17)
            self.multi_cell(0, 9, clean(line[2:]), new_x="LMARGIN", new_y="NEXT")
            self.ln(1)
        elif line.startswith("## "):
            self.ln(2)
            self.set_text_color(180, 25, 25)
            self.set_font("noto", "B", 13)
            self.multi_cell(0, 7.5, clean(line[3:]), new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(200, 30, 30)
            self.set_line_width(0.3)
            y = self.get_y()
            self.line(self.l_margin, y, self.w - self.r_margin, y)
            self.ln(2)
        elif line.startswith("### "):
            self.ln(1)
            self.set_text_color(40, 40, 90)
            self.set_font("noto", "B", 11.5)
            self.multi_cell(0, 6.5, clean(line[4:]), new_x="LMARGIN", new_y="NEXT")
        elif line.startswith("**[") or line.startswith("[") and "ANCHOR" in line:
            self.set_text_color(90, 40, 10)
            self.set_font("noto", "B", 10.5)
            self.multi_cell(0, 6, clean(line), new_x="LMARGIN", new_y="NEXT")
        elif line.lstrip().startswith("* "):
            self.set_text_color(20, 20, 20)
            self.set_font("noto", "", 10.5)
            self.multi_cell(0, 6, "•  " + clean(line.lstrip()[2:]), new_x="LMARGIN", new_y="NEXT")
        else:
            self.set_text_color(20, 20, 20)
            self.set_font("noto", "", 10.5)
            self.multi_cell(0, 6, clean(line), new_x="LMARGIN", new_y="NEXT")


def render_toc(pdf, outline):
    pdf.set_xy(pdf.l_margin, pdf.t_margin)
    pdf.set_text_color(200, 30, 30)
    pdf.set_font("noto", "B", 20)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("noto", "", 11)
    avail = pdf.w - pdf.l_margin - pdf.r_margin
    for s in outline:
        if s.level != 0:
            continue
        pdf.set_text_color(30, 30, 30)
        pdf.cell(avail - 16, 8, s.name, new_x="RIGHT", new_y="TOP")
        pdf.cell(16, 8, str(s.page_number), align="R", new_x="LMARGIN", new_y="NEXT")


def build(nums, label, subtitle, out_path):
    pdf = ShortsPDF(label)
    pdf.cover(subtitle)
    pdf.add_page()
    pdf.insert_toc_placeholder(render_toc, pages=1)
    for n in nums:
        path = find_short(n)
        if not path:
            print(f"  WARNING: SHORT {n} not found")
            continue
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        # bookmark name from the "# NN - Title" line
        sec = f"Short {n:02d}"
        for ln in lines:
            if ln.startswith("# "):
                sec = clean(ln[2:])
                break
        pdf.add_page()
        pdf.start_section(sec)
        for ln in lines:
            pdf.render_line(ln)
    pdf.output(out_path)
    print(f"WROTE {os.path.basename(out_path)} | {pdf.page_no()} pages | {os.path.getsize(out_path)} bytes")


if __name__ == "__main__":
    os.makedirs(DOCS, exist_ok=True)
    BATCHES = [
        (range(1, 11),  "Shorts 01-10", "वो गली — Viral Shorts Production Packages  |  Shorts 01-10  |  full A-to-Z 10-department", "WO GALI SHORTS 01-10.pdf"),
        (range(11, 21), "Shorts 11-20", "वो गली — Viral Shorts Production Packages  |  Shorts 11-20  |  full A-to-Z 10-department", "WO GALI SHORTS 11-20.pdf"),
        (range(21, 31), "Shorts 21-30", "वो गली — Viral Shorts Production Packages  |  Shorts 21-30  |  full A-to-Z 10-department", "WO GALI SHORTS 21-30.pdf"),
    ]
    for nums, label, subtitle, fname in BATCHES:
        build(nums, label, subtitle, os.path.join(DOCS, fname))
