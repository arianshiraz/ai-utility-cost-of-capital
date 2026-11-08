"""Build the paper as Word and PDF from docs/paper.md.
Word file: python-docx (display equations rendered with matplotlib mathtext); PDF: Word itself, through COM
(Windows with Microsoft Word installed). Outputs: paper/ai_utility_cost_of_capital.docx and .pdf
(only the PDF is committed). Run from the repository root: py -3 code/21_build_paper.py
"""
import re
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "stix"  # Times-like, to match the text
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "paper.md"
OUT = ROOT / "paper"
NAME = "ai_utility_cost_of_capital"
REPO = "https://github.com/arianshiraz/ai-utility-cost-of-capital"
FONT = "Times New Roman"
SYM = {r"\perp": "⊥", r"\Delta": "Δ", r"\alpha": "α", r"\theta": "θ", r"\gamma": "γ", r"\varepsilon": "ε",
       r"\beta": "β", r"\,": " ", r"\times": "×", r"\mathrm": ""}


def math_runs(p, tex, size):
    """Inline TeX as runs: _{..} subscript, ^{..} superscript, a few symbols."""
    for k, v in SYM.items():
        tex = tex.replace(k, v)
    for tok in re.findall(r"[_^]\{[^}]*\}|[_^].|[^_^]+", tex):
        if tok[0] in "_^":
            body = tok[2:-1] if tok[1] == "{" else tok[1:]
            r = p.add_run(body.replace("{", "").replace("}", ""))
            r.font.subscript, r.font.superscript = tok[0] == "_", tok[0] == "^"
        else:
            r = p.add_run(tok.replace("{", "").replace("}", ""))
        r.italic, r.font.size, r.font.name = True, size, FONT


def add_inline(p, text, size=Pt(11), bold=False, italic=False):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)  # links: keep the text
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\$[^$]+\$)", text):
        if not part:
            continue
        if part.startswith("$"):
            math_runs(p, part[1:-1], size)
            continue
        b, i, t = bold, italic, part
        if part.startswith("**"):
            b, t = True, part[2:-2]
        elif part.startswith("*"):
            i, t = True, part[1:-1]
        elif part.startswith("`"):
            t = part[1:-1]
        r = p.add_run(t)
        r.bold, r.italic, r.font.size, r.font.name = b, i, size, FONT


def render_eq(tex, path):
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${tex}$", fontsize=13)
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=False, facecolor="white")
    plt.close(fig)


def style(doc):
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15
    for lvl, sz in ((1, 14), (2, 12), (3, 11)):
        h = doc.styles[f"Heading {lvl}"]
        h.font.name, h.font.size, h.font.bold = FONT, Pt(sz), True
        h.font.color.rgb = RGBColor(0, 0, 0)
        rf = h.element.rPr.rFonts
        for att in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            rf.attrib.pop(qn(att), None)
        rf.set(qn("w:ascii"), FONT)
        rf.set(qn("w:hAnsi"), FONT)
    for s in doc.sections:
        s.left_margin = s.right_margin = Inches(1)
        s.top_margin = s.bottom_margin = Inches(1)


def add_table(doc, rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for r in cells if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]
    t = doc.add_table(rows=len(cells), cols=len(cells[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, r in enumerate(cells):
        for j, c in enumerate(r):
            cell = t.cell(i, j)
            cell.paragraphs[0].paragraph_format.space_after = Pt(0)
            add_inline(cell.paragraphs[0], c, size=Pt(8.5), bold=(i == 0))
    doc.add_paragraph()


def build():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    doc = Document()
    style(doc)
    tmp = Path(tempfile.mkdtemp())
    i, neq = 0, 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("# "):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(ln[2:].strip())
            r.bold, r.font.size, r.font.name = True, Pt(16), FONT
        elif ln.startswith("### "):
            doc.add_heading(ln[4:].strip(), level=2)
        elif ln.startswith("## "):
            doc.add_heading(ln[3:].strip(), level=1)
        elif ln.strip().startswith("$$"):
            if ln.strip() != "$$" and ln.strip().endswith("$$"):  # one-line display equation
                j, tex = i, ln.strip()[2:-2]
            else:
                j = i + 1
                while lines[j].strip() != "$$":
                    j += 1
                tex = " ".join(x.strip() for x in lines[i + 1:j])
            tex = tex.rstrip(",. ")
            neq += 1
            png = tmp / f"eq{neq}.png"
            render_eq(tex, png)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(png), height=Inches(0.42))
            i = j
        elif ln.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            add_table(doc, lines[i:j])
            i = j - 1
        elif ln.startswith("!["):
            path = re.search(r"\(([^)]+)\)", ln).group(1)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str((SRC.parent / path).resolve()), width=Inches(6.0))
        elif ln.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            add_inline(p, ln[2:])
        else:
            p = doc.add_paragraph()
            is_caption = ln.startswith("*") and not ln.startswith("**") and ln.rstrip().endswith("*")
            add_inline(p, ln, size=Pt(9.5) if is_caption else Pt(11))
            if lines[i - 1].startswith("Arian") or ln.startswith("Arian"):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        i += 1
    p = doc.add_paragraph()
    add_inline(p, f"Code, data documentation and pre-specification: {REPO}", size=Pt(9))
    OUT.mkdir(exist_ok=True)
    docx = OUT / f"{NAME}.docx"
    doc.save(docx)
    return docx


def to_pdf(docx):
    import win32com.client
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    try:
        d = word.Documents.Open(str(docx.resolve()), ReadOnly=True)
        d.SaveAs2(str(docx.with_suffix(".pdf").resolve()), FileFormat=17)
        d.Close(False)
    finally:
        word.Quit()


if __name__ == "__main__":
    f = build()
    to_pdf(f)
    print("written", f, f.with_suffix(".pdf"))
