"""QC, audit tables, manifest and ZIP for the integrated ODD submission.

Reads the generated documents in odd_resubmission/submission/integrated and the
preserved registries; writes audit Markdown to odd_resubmission/final_audit_integrated.
It never writes manuscript text or numerical outputs.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pandas as pd
from docx import Document
from docx.oxml.ns import qn
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from agentic_conservation.documents_em_odd import (  # noqa: E402
    ADDRESS,
    AFFILIATION,
    AUTHOR,
    EMAIL,
    FIGURES,
    ORCID,
    OUT_DIR,
    OUTPUTS,
    _historical_baselines,
    _lhs_frame,
    _robustness_frame,
)

SUB = ROOT / OUT_DIR
AUD = ROOT / "odd_resubmission/final_audit_integrated"
PROTECTED = [
    "src/agentic_conservation/simulation.py",
    "src/agentic_conservation/minimal_model.py",
    "src/agentic_conservation/analysis.py",
    "config",
    "results",
    "tables",
    "data",
    "manuscript",
    "submission",
    "frozen_cb_rejection_2026-10-26",
    "figures",
    "odd_resubmission/psi_forensics",
    "odd_resubmission/submission",
    "odd_resubmission/editorial",
]
BANNED = [
    "Appendix",
    "Table A1",
    "Table A2",
    "Table A3",
    "Table A4",
    "Table A5",
    "Table A6",
    "Table A7",
    "Supplementary table",
    "supplied as a separate file",
    "Independent researcher",
]
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def doc_text(p: Path) -> str:
    d = Document(p)
    cells = [c.text for t in d.tables for r in t.rows for c in r.cells]
    return "\n".join([x.text for x in d.paragraphs] + cells)


def main() -> None:
    AUD.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, str, str, str]] = []

    def check(group: str, item: str, ok: bool, detail: str = "") -> None:
        rows.append((group, item, "PASS" if ok else "FAIL", str(detail)))

    base = git("merge-base", "HEAD", "origin/master").strip()
    changed = [
        ln.split("\t")
        for ln in git("diff", "--relative", "--name-status", base, "--", *PROTECTED).splitlines()
        if ln
    ]
    bad = [c for c in changed if c[0] != "A"]
    added = [c[1] for c in changed if c[0] == "A"]
    check("baseline", f"no modified/deleted file in protected paths vs {base[:12]}", not bad, bad)
    allowed = ("figures/odd/fig1_network_living_nodes.png", "figures/odd/fig_psi_historical_v0.png")
    extra = [
        a
        for a in added
        if not (a in allowed or a.startswith("odd_resubmission/submission/integrated/"))
    ]
    check("baseline", "only expected additions in protected paths", not extra, extra or added)
    for f in ["EM_ODD_APPENDIX_A_FINAL.docx", "EM_ODD_REVISED_MANUSCRIPT_CLEAN_FINAL.docx"]:
        check(
            "baseline",
            f"historical {f} retained",
            (ROOT / "odd_resubmission/submission" / f).exists(),
        )

    clean, tracked = SUB / OUTPUTS["clean"], SUB / OUTPUTS["tracked"]
    resp, cover, pdf = SUB / OUTPUTS["response"], SUB / OUTPUTS["cover"], SUB / OUTPUTS["pdf"]
    for k, p in OUTPUTS.items():
        check("files", f"{k}: {p} exists", (SUB / p).exists())
    check("files", "no Appendix A document in package", not list(SUB.glob("*APPENDIX*")))

    # ---------------------------------------------------------- text checks
    texts = {p.name: doc_text(p) for p in (clean, resp, cover)}
    for name, t in texts.items():
        hits = [b for b in BANNED if b.lower() in t.lower()]
        check(
            "appendix", f"{name}: no appendix/placeholder/obsolete-affiliation text", not hits, hits
        )
        for v in (AUTHOR, AFFILIATION, ADDRESS, EMAIL, ORCID):
            check("author", f"{name}: contains '{v[:40]}'", v in t)
        check("author", f"{name}: old name order absent", "Tatsuki Onishi" not in t)
    for name in (resp.name, cover.name):
        check("letters", f"{name}: first person singular", " we " not in texts[name].lower())
        check("letters", f"{name}: cites ECOMOD-26-2231", "ECOMOD-26-2231" in texts[name])

    d = Document(clean)
    body = "\n".join(p.text for p in d.paragraphs)
    alltext = texts[clean.name]

    # ---------------------------------------------------------- figures
    xml = zipfile.ZipFile(clean).read("word/document.xml").decode()
    n_inline, n_anchor = xml.count("<wp:inline"), xml.count("<wp:anchor")
    check(
        "figures",
        "exactly ten inline drawings, no floating anchors",
        n_inline == 10 and n_anchor == 0,
        f"inline {n_inline}, anchor {n_anchor}",
    )
    rels = {r.rId: r for r in d.part.rels.values()}
    paras = d.paragraphs
    fig_rows = []
    caption_re = re.compile(r"^Figure (\d+)\. ")
    order = []
    for i, p in enumerate(paras):
        blips = p._p.findall(".//" + qn("a:blip"))
        if not blips:
            continue
        rid = blips[0].get(qn("r:embed"))
        blob = rels[rid].target_part.blob
        ext = p._p.find(".//" + qn("wp:extent"))
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        cap = paras[i + 1].text
        m = caption_re.match(cap)
        num = int(m.group(1)) if m else None
        key = list(FIGURES)[0]
        src = None
        for k, (rel, _c) in FIGURES.items():
            if (
                hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
                == hashlib.sha256(blob).hexdigest()
            ):
                key, src = k, rel
        im = Image.open(ROOT / src) if src else None
        ratio_ok = im is not None and abs(cx / cy - im.width / im.height) < 0.01
        first = body.find(f"Fig. {num}") if num else -1
        cite_before = 0 <= first < body.find(cap) if num else False
        inline = p._p.find(".//" + qn("wp:inline")) is not None
        order.append(num)
        fig_rows.append(
            (
                num,
                key,
                src,
                im.size if im else None,
                f"{cx / 914400:.2f} × {cy / 914400:.2f} in",
                ratio_ok,
                inline,
                bool(m),
                cite_before,
            )
        )
        check("figures", f"Figure {num}: embedded bytes identical to {src}", src is not None)
        check("figures", f"Figure {num}: inline, aspect ratio preserved", inline and ratio_ok)
        check("figures", f"Figure {num}: caption is the next editable paragraph", bool(m))
        check("figures", f"Figure {num}: first citation precedes the figure", cite_before)
    check("figures", "figures appear in numerical order 1–10", order == list(range(1, 11)), order)
    cited = [int(x) for x in re.findall(r"Fig\. (\d+)", body)]
    first_seq = list(dict.fromkeys(cited))
    check(
        "figures", "figures first cited in order 1–10", first_seq == list(range(1, 11)), first_seq
    )
    check(
        "figures",
        "Figure 1 biobank: genetic material, no animals",
        "never holds or receives animals" in body,
    )
    check(
        "figures",
        "historical Ψ figure labelled historical, not confirmatory",
        "Historical, not confirmatory" in body,
    )

    # ---------------------------------------------------------- tables
    caps = [p.text for p in paras if re.match(r"^Table \d+\. ", p.text)]
    nums = [int(re.match(r"^Table (\d+)\.", c).group(1)) for c in caps]
    check("tables", "table captions sequential", nums == list(range(1, len(d.tables) + 1)), nums)
    refs = []
    for m in re.finditer(r"Tables? (\d+)(?:–(\d+))?", body):
        if m.start() == 0 or body[m.start() - 1] == "\n":
            continue
        a_, b_ = int(m.group(1)), int(m.group(2) or m.group(1))
        refs.append((m.start(), list(range(a_, b_ + 1))))
    tcited = list(dict.fromkeys(k for _s, ks in refs for k in ks))
    check("tables", "tables first cited in numerical order", tcited == nums, tcited)
    positions = {n_: min(s_ for s_, ks in refs if n_ in ks) for n_ in nums}
    capos = {n_: body.find(c) for n_, c in zip(nums, caps)}
    check(
        "tables", "each table cited before its caption", all(positions[k] < capos[k] for k in nums)
    )
    check(
        "tables", "all tables are editable Word tables", len(d.tables) == len(caps), len(d.tables)
    )
    table_rows = [
        (n_, c[len(f"Table {n_}. ") :], len(d.tables[n_ - 1].rows)) for n_, c in zip(nums, caps)
    ]

    def cells(t):
        return [[c.text for c in r.cells] for r in t.rows]

    rob = _robustness_frame(ROOT)
    t10 = cells(d.tables[nums[[c.startswith("Table 10.") for c in caps].index(True)] - 1])[2:]
    check(
        "numbers",
        "ablation/adverse table: all 15 designs × 13 values match canonical",
        t10 == rob.astype(str).values.tolist(),
        f"{len(t10)} rows",
    )
    canon = pd.read_csv(ROOT / "tables/table7_robustness.csv")
    vals = {
        f"{x:.3f}"
        for x in canon[["survival_100", "fraction_ebd", "mean_individual_welfare"]]
        .to_numpy()
        .ravel()
    }
    shown = {v for r in t10 for v in r[3:6] + r[7:]}
    check(
        "numbers",
        "every table7 value appears (45 × 3)",
        vals <= shown and len(canon) == 45,
        len(vals),
    )
    lhs = _lhs_frame(ROOT)
    t9 = cells(d.tables[8])[1:]
    check(
        "numbers",
        "LHS profile table matches tables/table4_sensitivity.csv",
        t9 == lhs.values.tolist(),
    )
    psi_t = cells(d.tables[10])[1:]
    base_rows = [list(map(str, r)) for r in _historical_baselines(ROOT)]
    check(
        "numbers", "historical baselines B0–B2 rows match per-cell record", psi_t[-3:] == base_rows
    )
    c = pd.read_csv(ROOT / "results/psi_confirmatory/metrics.csv")
    c = c[(c.endpoint == "survival_100") & (c.stratum == "all")].iloc[0]
    for lbl, val in [
        ("acc_det", f"{c.acc_det:.3f}"),
        ("wilson_lo", f"{c.acc_det_wilson_lo:.3f}"),
        ("regret", f"{c.regret_psi:.4f}"),
        ("acc_all", f"{c.acc_all:.3f}"),
    ]:
        check("numbers", f"prospective {lbl} {val} in text/table", val in alltext)
    check(
        "numbers",
        "33/34 determinate",
        int(round(c.acc_det * c.det_cells)) == 33 and int(c.det_cells) == 34,
    )
    for v in ["0.846", "0.393", "0.0450"]:
        check("numbers", f"historical V0 value {v} present", v in alltext)
    q2 = pd.read_csv(ROOT / "results/odd_verification/q2_summary.csv")
    for r in q2[q2.endpoint == "survival_100"].itertuples():
        check(
            "numbers",
            f"Q2 {r.climate_form} contrast {r.S7_minus_S6:+.3f}",
            f"{r.S7_minus_S6:+.3f}" in alltext or f"{r.S7_minus_S6:.3f}" in alltext,
        )

    # ---------------------------------------------------------- format
    om = xml.count("<m:oMath>")
    check("format", "Word-native OMML equations present", om >= 8, om)
    styles = zipfile.ZipFile(clean).read("word/styles.xml").decode()
    normal = re.search(r'<w:style [^>]*w:styleId="Normal".*?</w:style>', styles, re.S).group(0)
    check(
        "format",
        "Normal style Times New Roman 12 pt",
        "Times New Roman" in normal and 'w:val="24"' in normal,
    )
    fonts = set(re.findall(r'w:ascii="([^"]+)"', xml))
    check("format", "all runs Times New Roman", fonts <= {"Times New Roman", "Cambria Math"}, fonts)
    colours = set(re.findall(r'<w:color w:val="([0-9A-Fa-f]{6})"', xml)) - {"000000"}
    check("format", "no non-black text colour in clean manuscript", not colours, colours)
    check("format", "no stray Markdown asterisks", "**" not in alltext)
    check("format", "no artificial character spacing", "<w:spacing w:val" not in xml)
    capsz = [
        r.font.size.pt
        for p in paras
        if p.text.startswith("Figure ") and re.match(r"^Figure \d+\. ", p.text)
        for r in p.runs
        if r.font.size
    ]
    check("format", "figure captions 10 pt", capsz and set(capsz) == {10.0}, set(capsz))
    secs = [(s.orientation, round(s.page_width.inches, 1)) for s in d.sections]
    check(
        "format",
        "one landscape section only (Table 10)",
        sum(1 for o, _w in secs if int(o) == 1) == 1,
        secs,
    )
    tx = zipfile.ZipFile(tracked).read("word/document.xml").decode()
    check(
        "format",
        "tracked: red insertions and blue strikethrough deletions",
        "C00000" in tx and "0033CC" in tx and "<w:strike/>" in tx,
    )

    # ---------------------------------------------------------- PDF
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    imgs = subprocess.run(["pdfimages", "-list", str(pdf)], capture_output=True, text=True).stdout
    img_pages = [int(ln.split()[0]) for ln in imgs.splitlines()[2:] if ln.split()[2] == "image"]
    check("pdf", "PDF contains ten raster figures", len(img_pages) == 10, img_pages)
    fig_pages, tab_pages = {}, {}
    for pg in range(1, pages + 1):
        t = subprocess.run(
            ["pdftotext", "-f", str(pg), "-l", str(pg), str(pdf), "-"],
            capture_output=True,
            text=True,
        ).stdout
        for m in re.finditer(r"^(Figure|Table) (\d+)\. ", t, re.M):
            (fig_pages if m.group(1) == "Figure" else tab_pages).setdefault(int(m.group(2)), pg)
        check(
            "pdf", f"page {pg}: no replacement glyph", "\ufffd" not in t
        ) if "\ufffd" in t else None
    bbox = subprocess.run(
        ["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, text=True
    ).stdout
    overflow = []
    for pg, page in enumerate(bbox.split("<page ")[1:], 1):
        width = float(re.search(r'width="([\d.]+)"', page).group(1))
        right = width - 54
        overflow += [
            (pg, w_)
            for x_, w_ in re.findall(r'xMax="([\d.]+)" yMax="[\d.]+">([^<]*)<', page)
            if float(x_) > right
        ]
    check(
        "pdf", "no text beyond the right margin (equations and tables)", not overflow, overflow[:8]
    )
    ptxt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    check(
        "pdf",
        "PDF: no placeholder or appendix reference",
        not any(b.lower() in ptxt.lower() for b in BANNED[:-1]),
    )
    check(
        "pdf",
        "PDF figure captions found for 1–10",
        sorted(fig_pages) == list(range(1, 11)),
        fig_pages,
    )

    # ---------------------------------------------------------- write reports
    def md_table(head, data):
        out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        out += ["| " + " | ".join(str(x) for x in r) + " |" for r in data]
        return "\n".join(out)

    fig_md = [
        "# FINAL INLINE FIGURE QC",
        "",
        "Generated by scripts/qc_integrated_submission.py from the clean DOCX and PDF.",
        "",
        md_table(
            [
                "Fig.",
                "key",
                "source file (bytes embedded unchanged)",
                "pixels",
                "size in DOCX",
                "aspect kept",
                "inline",
                "editable caption next",
                "cited before",
                "PDF page",
                "PDF raster page",
            ],
            [
                (
                    *r,
                    fig_pages.get(r[0]),
                    img_pages[r[0] - 1] if r[0] and r[0] <= len(img_pages) else None,
                )
                for r in fig_rows
            ],
        ),
        "",
        f"Inline drawings: {n_inline}; floating anchors: {n_anchor}. The PDF is a "
        "LibreOffice rendering of the clean DOCX; it re-encodes images at about "
        "300 ppi, while the DOCX keeps the original 300–320 dpi PNG bytes.",
        "",
        "Scientific content of each figure against its caption: "
        "FINAL_INLINE_FIGURE_CONTENT_REVIEW.md.",
    ]
    (AUD / "FINAL_INLINE_FIGURE_QC.md").write_text("\n".join(fig_md) + "\n")
    tab_md = [
        "# FINAL TABLE ORDER AND NUMERICAL AUDIT",
        "",
        "Generated by scripts/qc_integrated_submission.py.",
        "",
        md_table(
            ["Table", "caption", "rows incl. header", "PDF page"],
            [(*r, tab_pages.get(r[0])) for r in table_rows],
        ),
        "",
        md_table(
            ["group", "check", "result", "detail"],
            [r for r in rows if r[0] in ("tables", "numbers")],
        ),
    ]
    (AUD / "FINAL_TABLE_ORDER_AND_NUMERICAL_AUDIT.md").write_text("\n".join(tab_md) + "\n")
    fmt_md = [
        "# FINAL OMML AND FORMAT QC",
        "",
        "Generated by scripts/qc_integrated_submission.py.",
        "",
        f"PDF pages: {pages}. OMML equation objects: {om}. Sections: {secs}.",
        "",
        md_table(
            ["group", "check", "result", "detail"], [r for r in rows if r[0] in ("format", "pdf")]
        ),
    ]
    (AUD / "FINAL_OMML_AND_FORMAT_QC.md").write_text("\n".join(fmt_md) + "\n")
    qc_md = [
        "# FINAL QC MATRIX (automated part)",
        "",
        "Generated by scripts/qc_integrated_submission.py.",
        "",
        md_table(["group", "check", "result", "detail"], rows),
    ]
    (AUD / "FINAL_QC_MATRIX_AUTOMATED.md").write_text("\n".join(qc_md) + "\n")

    # ---------------------------------------------------------- package
    fig_dir = SUB / "figures"
    files = [clean, tracked, pdf, resp, cover] + sorted(
        fig_dir.glob("Figure_*.png"), key=lambda p: int(p.stem.split("_")[1])
    )
    (SUB / "SHA256SUMS.txt").write_text("".join(f"{sha(p)}  {p.relative_to(SUB)}\n" for p in files))
    pkg = SUB / "EM_ODD_SUBMISSION_PACKAGE_INTEGRATED.zip"
    with zipfile.ZipFile(pkg, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files + [SUB / "SHA256SUMS.txt"]:
            z.write(p, p.relative_to(SUB))
    fails = [r for r in rows if r[2] == "FAIL"]
    print(f"{len(rows) - len(fails)}/{len(rows)} PASS; package {pkg.name} {sha(pkg)[:16]}")
    for r in fails:
        print("FAIL", r)


if __name__ == "__main__":
    main()
