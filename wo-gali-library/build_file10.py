#!/usr/bin/env python3
"""Build the File 10 (Films 91-100) combined PDF."""
from build_combined import build_combined

src = "/projects/sandbox/pdfbuild/src10"
films = [f"{src}/FILM_{n}_full.md" for n in range(91, 101)]
build_combined(
    films,
    "/projects/sandbox/pdfbuild/WO_GALI_FILE_10_Films_91_to_100.pdf",
    "वो गली",
    "FILE 10  -  THE LAST THRESHOLD EDITION (GRAND FINALE)  -  Films 91 to 100  -  combined",
)
