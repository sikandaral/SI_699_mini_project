"""Render notebooks/mini_project_draft.ipynb as the submission PDF.

The report is the notebook itself with code removed: cells tagged ``remove_cell``
(setup and number checks) are dropped, and every other code cell shows only its
figure. So the PDF cannot disagree with the notebook.

Run from the repo root:  python tools_make_draft_report.py
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
NB = ROOT / "notebooks" / "mini_project_draft.ipynb"
OUT = ROOT / "report"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT.mkdir(exist_ok=True)

subprocess.run(["jupyter", "nbconvert", str(NB), "--to", "html", "--no-input", "--no-prompt",
                "--TagRemovePreprocessor.enabled=True",
                "--TagRemovePreprocessor.remove_cell_tags=remove_cell",
                "--output-dir", str(OUT), "--output", "mini_project_draft"], check=True)

PAPER_CSS = """<style>
@page { size: letter; margin: 0.7in 0.75in; }
html, body { background: #fff !important; margin: 0 !important; padding: 0 !important; }
main, .jp-Notebook { margin: 0 !important; padding: 0 !important; min-height: 0 !important; }
.jp-Cell:last-child, .jp-Cell:last-child p:last-child { margin-bottom: 0 !important; padding-bottom: 0 !important; }
body, .jp-Notebook, .jp-RenderedHTMLCommon {
  font-family: "Charter", "Georgia", "Times New Roman", serif !important;
  font-size: 10pt !important; line-height: 1.38 !important; color: #111 !important; }
.jp-Notebook { padding: 0 !important; }
.jp-Cell { padding: 0 !important; margin: 0 !important; }
.jp-RenderedHTMLCommon { padding-right: 0 !important; }
.jp-RenderedHTMLCommon p { margin: 0 0 6pt !important; text-align: justify; }
.jp-RenderedHTMLCommon h1 { font-size: 15pt !important; font-weight: 700 !important; line-height: 1.2; margin: 0 0 4pt !important; }
.jp-RenderedHTMLCommon h2 { font-size: 10pt !important; text-transform: uppercase; letter-spacing: .07em;
  color: #0d2f5c !important; border-bottom: .5pt solid #d8d6d0; padding-bottom: 2pt;
  margin: 12pt 0 5pt !important; }
.jp-RenderedHTMLCommon strong { font-weight: 700; }
.jp-RenderedHTMLCommon p:has(a) { text-align: left !important; word-break: break-word; }
.jp-OutputArea-output img { max-width: 80% !important; height: auto !important;
  display: block; margin: 4pt auto 2pt !important; }
.jp-Cell-outputWrapper, .jp-OutputArea-child { break-inside: avoid; }
.jp-InputPrompt, .jp-OutputPrompt, .jp-Collapser { display: none !important; }
a.anchor-link { display: none !important; }
</style>
"""
html_path = OUT / "mini_project_draft.html"
html = html_path.read_text(encoding="utf-8").replace("</head>", PAPER_CSS + "</head>", 1)
html_path.write_text(html, encoding="utf-8")

pdf_path = OUT / "mini_project_draft.pdf"
subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}", f"file://{html_path}"], capture_output=True)
pages = len(re.findall(rb"/Type\s*/Page[^s]", pdf_path.read_bytes()))
print(f"{pdf_path.relative_to(ROOT)}: {pages} pages")
