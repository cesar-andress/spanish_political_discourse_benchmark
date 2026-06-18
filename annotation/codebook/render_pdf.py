#!/usr/bin/env python3
"""Render SPDB_Codebook_v1.md to PDF via WeasyPrint."""

from __future__ import annotations

import sys
from pathlib import Path

import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
MD = HERE / "SPDB_Codebook_v1.md"
PDF = HERE / "SPDB_Codebook_v1.pdf"

CSS = """
@page { size: A4; margin: 2cm 2.2cm; }
body { font-family: "DejaVu Sans", sans-serif; font-size: 10pt; line-height: 1.45; color: #1a1a1a; }
h1 { font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 0.3em; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 13pt; margin-top: 1.2em; color: #222; }
h3 { font-size: 11pt; margin-top: 1em; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; }
pre { background: #f5f5f5; padding: 0.6em; border-left: 3px solid #ccc; white-space: pre-wrap; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 9pt; }
th, td { border: 1px solid #bbb; padding: 0.35em 0.5em; text-align: left; vertical-align: top; }
th { background: #eee; }
blockquote { margin: 0.6em 0; padding-left: 0.8em; border-left: 3px solid #888; color: #333; font-style: italic; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }
ul, ol { margin: 0.4em 0 0.4em 1.2em; }
.label-id { font-family: monospace; font-weight: bold; }
"""


def main() -> int:
    if not MD.exists():
        print(f"Missing {MD}", file=sys.stderr)
        return 1
    body = markdown.markdown(
        MD.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
    <title>SPDB Annotation Codebook v1</title>
    <style>{CSS}</style></head><body>{body}</body></html>"""
    HTML(string=html, base_url=str(HERE)).write_pdf(PDF)
    print(f"Wrote {PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
