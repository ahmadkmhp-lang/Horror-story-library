#!/usr/bin/env python3
"""Build the File 9 (Films 81-90) combined PDF."""
from build_combined import build_combined

src = "/projects/sandbox/pdfbuild/src9"
films = [f"{src}/FILM_{n}_full.md" for n in range(81, 91)]
build_combined(
    films,
    "/projects/sandbox/pdfbuild/WO_GALI_FILE_09_Films_81_to_90.pdf",
    "वो गली",
    "FILE 9  -  THE FORGOTTEN TRADES EDITION  -  Films 81 to 90  -  combined",
)
