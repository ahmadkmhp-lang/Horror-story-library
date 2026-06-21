#!/usr/bin/env python3
"""Generate a horror-transcript PDF from preserved story_NN.txt source files.

- Full Devanagari text via fpdf2 + uharfbuzz HarfBuzz shaping (Noto fonts).
- Cover page, Table of Contents with real page numbers, PDF bookmarks, page-number footers.
- 100% of source text preserved (incl. timestamps); no summarizing.
"""
import sys, os
from fpdf import FPDF

SRC = os.path.join(os.path.dirname(__file__), "src")
FONTS = os.path.join(os.path.dirname(__file__), "fonts")

# id -> (English/Hindi title, optional note)
TITLES = {
    1:  "Bhakshini / भक्षिणी",
    2:  "This House Is Mine",
    3:  "The Yogini's Curse",
    4:  "The College Library Spirit",
    5:  "The Dark Well Ritual (Andhakup Kriya)",
    6:  "The River's Fish Ghost (Sugandha)",
    7:  "The Last Cab (Mahesh Patil)",
    8:  "मेरा बच्चा कहां है? (Anjali)",
    9:  "भूतों की बारात (The Ghost Procession)",
    10: "शाकचुन्नी (Shakchunni / Kalyani)",
    11: "कुएं वाली आत्मा / सती आसरा (Maya)",
    12: "आईना — The Mirror Surgeon (Sameer)",
    13: "आईना — The Mirror Surgeon (Sameer) [Duplicate of Story 12]",
    14: "मोलक देवता (Aghoram & Molak)",
    15: "लबूबू डॉल (The Labubu Doll)",
    16: "अंतिम अर्पण (Royal Crescent — Rupa)",
    17: "रूम 333 (Langham Hotel — Annie)",
    18: "काक तंत्र (The Crow Tantra — Ajitesh)",
    19: "ओकीकू डॉल (The Okiku Doll)",
    20: "रोहतांग की लोरी (Rohtang Lullaby — Sahil)",
    21: "कॉर्प्स ब्राइड (The Dead Bride — Mateo)",
    22: "काल त्रिगोरी (Kaal Trigodi)",
    23: "7 बजे का राज (Infrasound — Aryan)",
    24: "रूहानी कैद (The Cursed Book — Sameer & Tara)",
    25: "शांति निवास (Grief & Illusion — Mayank)",
    26: "माया की आत्मा (Kulkarni House — Vedika)",
    27: "शैतान की भेंट (Jayant & Neelima)",
    28: "मसान (The Massan — Anshika)",
    29: "आरे कॉलोनी का रिक्शा (Mohan & Reshma)",
    30: "एम्बुलेंस — दूल्हे की आत्मा (Raghu)",
    31: "कशेड़ी घाट का चकवा (Akash & Pankaj)",
    32: "सती घाटी (Kamlesh & the Truck)",
}


class TranscriptPDF(FPDF):
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
        self.cell(0, 8, f"{self.doc_title}    |    Page {self.page_no()}",
                  align="C")

    def cover(self, subtitle):
        self._on_cover = True
        self.set_text_shaping(False)  # cover text is Latin; avoids shaping+center bug
        self.add_page()
        self.set_fill_color(10, 10, 12)
        self.rect(0, 0, self.w, self.h, style="F")
        self.set_y(95)
        self.set_text_color(200, 30, 30)
        self.set_font("noto", "B", 30)
        self.cell(0, 16, "HORROR STORY", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 16, "TRANSCRIPTS", align="C", new_x="LMARGIN", new_y="NEXT")
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
        pdf.cell(16, 8, str(s.page_number), align="R",
                 new_x="LMARGIN", new_y="NEXT")


def build(story_ids, label, subtitle, out_path, toc_pages=1):
    pdf = TranscriptPDF(label)
    pdf.cover(subtitle)
    pdf.add_page()
    pdf.insert_toc_placeholder(render_toc, pages=toc_pages)

    for sid in story_ids:
        path = os.path.join(SRC, f"story_{sid:02d}.txt")
        with open(path, encoding="utf-8") as f:
            text = f.read().rstrip("\n")
        title = TITLES.get(sid, "")
        pdf.add_page()
        heading = f"Story {sid:02d}"
        pdf.start_section(f"{heading} — {title}")
        pdf.set_text_color(200, 30, 30)
        pdf.set_font("noto", "B", 22)
        pdf.multi_cell(0, 12, heading, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("noto", "B", 13)
        pdf.multi_cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        pdf.set_draw_color(200, 30, 30)
        pdf.set_line_width(0.4)
        y = pdf.get_y()
        pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
        pdf.ln(4)
        pdf.set_text_color(20, 20, 20)
        pdf.set_font("noto", "", 11.5)
        pdf.multi_cell(0, 7.2, text, new_x="LMARGIN", new_y="NEXT")

    pdf.output(out_path)
    print(f"WROTE {os.path.basename(out_path)} | {pdf.page_no()} pages | {os.path.getsize(out_path)} bytes")
    return pdf.page_no()


if __name__ == "__main__":
    DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(DOCS, exist_ok=True)
    VOLUMES = [
        (range(1, 8),   "Stories 01-07", "YouTube Horror Story Transcripts  |  Volume 1  |  Stories 01-07", "YOUTUBE TRANSCRIPT 1-7.pdf"),
        (range(8, 18),  "Stories 08-17", "YouTube Horror Story Transcripts  |  Volume 2  |  Stories 08-17", "YOUTUBE TRANSCRIPT 8-17.pdf"),
        (range(18, 28), "Stories 18-27", "YouTube Horror Story Transcripts  |  Volume 3  |  Stories 18-27", "YOUTUBE TRANSCRIPT 18-27.pdf"),
        (range(28, 33), "Stories 28-32", "YouTube Horror Story Transcripts  |  Volume 4  |  Stories 28-32", "YOUTUBE TRANSCRIPT 28-32.pdf"),
        (range(1, 33),  "Complete Library (01-32)", "YouTube Horror Story Transcripts  |  COMPLETE LIBRARY  |  All 32 Stories", "YOUTUBE TRANSCRIPT COMPLETE LIBRARY.pdf"),
    ]
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    total = {}
    for ids, label, subtitle, fname in VOLUMES:
        if target != "all" and target not in fname:
            continue
        pages = build(ids, label, subtitle, os.path.join(DOCS, fname),
                      toc_pages=2 if len(list(ids)) > 10 else 1)
        total[fname] = pages
    print("PAGE TOTALS:", total)
