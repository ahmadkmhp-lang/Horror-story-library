#!/usr/bin/env python3
"""Build the MASTER combined PDF of the entire WO GALI cinematic library (Films 41-100)."""
from build_combined import build_combined

src = "/projects/sandbox/pdfbuild/master"
films = [f"{src}/FILM_{n:03d}.md" for n in range(41, 101)]
build_combined(
    films,
    "/projects/sandbox/pdfbuild/WO_GALI_MASTER_LIBRARY_Films_41_to_100.pdf",
    "वो गली",
    "MASTER LIBRARY  -  Cinematic Films 41 to 100  -  Files 5 to 10  -  complete combined edition",
)
