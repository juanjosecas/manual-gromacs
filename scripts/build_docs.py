#!/usr/bin/env python3
"""Generate modular MkDocs pages from canonical manual.md without editing it."""
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CHAPTERS = DOCS / "capitulos"
TICK = chr(96)
SECTIONS = [
    ("Instalación de GROMACS", "instalacion", "Instalación y Docker"),
    ("Caso: 1 proteína - 1 ligando", "proteina-ligando", "Proteína y ligando"),
    ("Simulación de una caja de agua", "sistemas", "Sistemas y simulaciones"),
    ("Interacción energética lineal (Linear Interaction Energy, LIE)", "lie", "LIE"),
    ("Múltiples moléculas de ligandos y de proteínas", "multimoleculares", "Sistemas multimoleculares"),
    ("Dinámica de una proteína en agua", "proteina-agua", "Proteína en agua"),
    ("Sistema bifásico", "sistema-bifasico", "Sistema bifásico"),
    ("Proteína de membrana: construcción de una bicapa e inserción de una acuaporina", "membranas", "Membranas y acuaporinas"),
    ("Energía libre de perturbación: energía libre de solvatación", "fep", "FEP y solvatación"),
    ("Energía de unión mediante " + TICK + "gmx_MMPBSA" + TICK, "mmpbsa", "MM/PBSA"),
]

def slugify(title):
    title = re.sub(r"[\x60*_]", "", title).lower()
    title = "".join(c for c in unicodedata.normalize("NFKD", title)
                    if not unicodedata.combining(c))
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9 -]", "", title).strip().replace(" ", "-"))

def headings(lines):
    result = []
    fence = None
    for i, line in enumerate(lines):
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if m:
            marker = m.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        match = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
        if match:
            result.append((i, len(match.group(1)), match.group(2)))
    if fence is not None:
        raise ValueError("Unclosed Markdown code fence")
    return result

def main():
    lines = (ROOT / "manual.md").read_text(encoding="utf-8").splitlines()
    hs = headings(lines)
    starts = []
    for title, name, label in SECTIONS:
        found = [i for i, level, t in hs if t == title]
        if len(found) != 1:
            raise ValueError(f"Expected one heading {title!r}, found {len(found)}")
        starts.append((found[0], name, label))
    starts.sort()
    CHAPTERS.mkdir(parents=True, exist_ok=True)
    pages = {}
    for idx, (start, name, label) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        pages[name] = (start, end, label)
    (DOCS / "introduccion.md").write_text("\n".join(lines[:starts[0][0]]) + "\n", encoding="utf-8")
    anchors = {}
    for i, level, title in hs:
        page = next((name for name, (a, b, _) in pages.items() if a <= i < b), None)
        if page:
            anchors.setdefault(slugify(title), page)
    for name, (start, end, _) in pages.items():
        indexed = {i: (level, title) for i, level, title in hs if start <= i < end}
        rendered = []
        for pos in range(start, end):
            line = lines[pos]
            if pos in indexed:
                level, title = indexed[pos]
                new_level = 1 if pos == start else min(level + (1 if level <= 2 else 0), 4)
                line = "#" * new_level + " " + title + " {#" + slugify(title) + "}"
            rendered.append(line)
        (CHAPTERS / f"{name}.md").write_text("\n".join(rendered).rstrip() + "\n", encoding="utf-8")
    guide = (ROOT / "guia.md").read_text(encoding="utf-8")
    guide = re.sub(r"\A---\n.*?\n---\n", "", guide, flags=re.S)
    def fix_link(match):
        anchor = match.group(1)
        page = anchors.get(anchor)
        if page is None:
            raise ValueError(f"Unknown guide link: #{anchor}")
        return f"capitulos/{page}.md#{anchor}"
    guide = re.sub(r"\{\{\s*'/'\s*\|\s*relative_url\s*\}\}#([a-zA-Z0-9_-]+)", fix_link, guide)
    guide = re.sub(r"\{\{\s*'/'\s*\|\s*relative_url\s*\}\}", "introduccion.md", guide)
    (DOCS / "guia.md").write_text(guide, encoding="utf-8")
    index = ["# Manual de GROMACS", "", "Documentación de dinámica molecular con GROMACS 2026.3.", "",
             "Contenido científico conservado en el archivo original del repositorio.", "",
             "## Comenzar", "", "- [Guía práctica](guia.md)", "- [Introducción](introduccion.md)", "",
             "## Capítulos", ""]
    for _, name, label in starts:
        index.append(f"- [{label}](capitulos/{name}.md)")
    (DOCS / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"Generated {len(pages)} chapters and guide")

if __name__ == "__main__":
    main()
