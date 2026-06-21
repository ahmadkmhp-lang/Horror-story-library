# Release Notes — v1.0.0

**Horror Story Library — YouTube Transcript Library Complete Collection**

## Overview
First public release. Contains 32 horror story transcripts preserved verbatim (Hindi & English) and compiled into 5 print-ready PDF volumes with full Devanagari typography.

## What's Included
- **32 transcripts** — `transcripts/Story_01.md` … `Story_32.md`
- **5 PDF volumes** — `docs/`
  | Volume | Stories | Pages |
  |--------|---------|-------|
  | YOUTUBE TRANSCRIPT 1-7.pdf | 01–07 | 40 |
  | YOUTUBE TRANSCRIPT 8-17.pdf | 08–17 | 46 |
  | YOUTUBE TRANSCRIPT 18-27.pdf | 18–27 | 47 |
  | YOUTUBE TRANSCRIPT 28-32.pdf | 28–32 | 29 |
  | YOUTUBE TRANSCRIPT COMPLETE LIBRARY.pdf | 01–32 | 154 |
- **2 reports** — `reports/validation_report.md`, `reports/completion_report.md`
- **Reproducible build tooling** — `build/generate_pdf.py`, bundled Noto fonts, raw sources

## Features
- Verbatim preservation (~74,275 words; original timestamps retained)
- Cover page, Table of Contents (real page numbers), PDF bookmarks, page-number footers in every volume
- Correct Devanagari shaping via HarfBuzz (uharfbuzz) + Noto Sans Devanagari

## Notes
- Story 13 is an exact duplicate of Story 12 in the source batch — preserved and clearly flagged.

## Verification
All five PDFs validated (open, page count, bookmarks, TOC, page numbering, Unicode-extractable Hindi). See `REPOSITORY_AUDIT.md`.

**License:** MIT
