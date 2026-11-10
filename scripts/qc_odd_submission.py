"""QC, manifest and ZIP for odd_resubmission/submission (no manuscript writes)."""

from __future__ import annotations

import hashlib
import subprocess
import zipfile
from pathlib import Path

import pandas as pd
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "odd_resubmission/submission"
BASELINES = {
    "manuscript/EM_MANUSCRIPT.docx": "8ff06f53e6bf0f49818795745f0d0b616bcc0d743aad5bbbc88ed1a8895b91de",  # noqa: E501
    "results/reversal/holdout_psi.csv": "57899cace7f3fd6cb1e662306df9f2bf1e49282ea9d688cb265f98361c93332c",  # noqa: E501
    "results/psi_confirmatory/designs.csv": "53096b7a4efe1a137d158bd91cf9d6bb534ec2a0f6e1aa21d1a81ec11b47b2e1",  # noqa: E501
    "results/psi_confirmatory/psi_predictions.csv": "b137f140cdf426ca2ea81526d09e672036ea7a8eab238353c0f6622c691fd85c",  # noqa: E501
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def text(p: Path) -> list[str]:
    return [x.text for x in Document(p).paragraphs]


def main() -> None:
    rows = []

    def check(item: str, ok: bool, detail: str) -> None:
        rows.append((item, "PASS" if ok else "FAIL", detail))

    clean = SUB / "EM_ODD_REVISED_MANUSCRIPT_CLEAN_FINAL.docx"
    tracked = SUB / "EM_ODD_REVISED_MANUSCRIPT_TRACKED_FINAL.docx"
    paras = text(clean)
    cells = [c.text for t in Document(clean).tables for r in t.rows for c in r.cells]
    body = "\n".join(paras + cells)
    for rel, h in BASELINES.items():
        check(f"baseline unchanged: {rel}", sha(ROOT / rel) == h, sha(ROOT / rel)[:16])
    diff = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", "results", "config", "manuscript"],
        cwd=ROOT,
    ).returncode
    check("no uncommitted changes to results/config/manuscript", diff == 0, f"git diff rc={diff}")
    a = paras.index("Abstract")
    aw = len(paras[a + 1].split())
    check("abstract <= 250 words", aw <= 250, f"{aw} words")
    h = paras.index("Highlights")
    hl = [len(x.lstrip("- ")) for x in paras[h + 1 : h + 6]]
    check("3-5 highlights <= 85 chars", max(hl) <= 85, str(hl))
    kw = next(x for x in paras if x.startswith("Keywords:"))
    nk = len(kw.split(":", 1)[1].split(";"))
    check("keywords <= 6", nk <= 6, f"{nk}")
    i, r = paras.index("1. Introduction"), paras.index("References")
    words = sum(len(x.split()) for x in paras[i:r] if not x.startswith(("Figure ", "Table ")))
    check("main text <= 7000 words (intro-declarations, excl. legends)", words <= 7000, f"{words}")
    odd = [
        "2.1 Purpose and patterns",
        "2.2 Entities, state variables, and scales",
        "2.3 Process overview and scheduling",
        "2.4 Design concepts",
        "2.5 Initialization",
        "2.6 Input data",
        "2.7 Submodels",
    ]
    check("all seven ODD elements in order", [p for p in paras if p in odd] == odd, "")
    dc = [
        "Basic principles",
        "Emergence",
        "Adaptation",
        "Objectives",
        "Learning",
        "Prediction",
        "Sensing",
        "Interaction",
        "Stochasticity",
        "Collectives",
        "Observation",
    ]
    check("11 design concepts", all(any(p.startswith(d + ":") for p in paras) for d in dc), "")
    labels = [
        "Process",
        "Form",
        "Alternatives",
        "Assumptions",
        "Effect on conclusions",
        "Evidence",
        "Missing evidence",
    ]
    blocks = sum(1 for p in paras if p.startswith("Missing evidence:"))
    check(
        "S1 rationale blocks (7 labels) for Eqs 1, 2, 6, 7 and Algorithm 2",
        blocks >= 5 and all(any(p.startswith(lb + ":") for p in paras) for lb in labels),
        f"{blocks} blocks",
    )
    xml = zipfile.ZipFile(clean).read("word/document.xml").decode()
    check("Word-native OMML equations", xml.count("<m:oMath>") >= 8, f"{xml.count('<m:oMath>')}")
    check("no embedded images in manuscript", "<pic:pic" not in xml, "figures separate")
    for n in range(1, 11):
        ok = f"Fig. {n}" in body and (SUB / f"figures/Figure_{n}.png").exists()
        check(f"Figure {n} cited and supplied", ok, "")
    tables = len(Document(clean).tables)
    check("all tables cited", all(f"Table {k}" in body for k in range(1, tables + 1)), f"{tables}")
    check(
        "withdrawal of original frozen-model claim stated",
        "withdraw the claim that the original held-out analysis" in body,
        "",
    )
    check("no 'independent validation' claim", "independent validation" not in body.lower(), "")
    check("MIN_BREEDING_POP = 4 stated", "MIN_BREEDING_POP = 4" in body, "")
    c = pd.read_csv(ROOT / "results/psi_confirmatory/metrics.csv")
    c = c[(c.endpoint == "survival_100") & (c.stratum == "all")].iloc[0]
    check("confirmatory accuracy matches registry", f"{c.acc_det:.3f}" in body, f"{c.acc_det:.3f}")
    q2 = pd.read_csv(ROOT / "results/odd_verification/q2_summary.csv")
    q2 = q2[q2.endpoint == "survival_100"]
    for row in q2.itertuples():
        check(
            f"Q2 {row.climate_form} contrast in text",
            f"{row.S7_minus_S6:+.3f}" in body or f"{row.S7_minus_S6:.3f}" in body,
            f"{row.S7_minus_S6:+.3f}",
        )
    s = pd.read_csv(ROOT / "results/policy_summary.csv")
    s = s[~s.oracle & (s.metric == "survival_100")].set_index("policy").estimate
    check("base S6/S7 survival in text", f"{s.S6:.3f}" in body and f"{s.S7:.3f}" in body, "")
    tx = zipfile.ZipFile(tracked).read("word/document.xml").decode()
    check(
        "tracked: red insertions and blue strikethrough deletions",
        "C00000" in tx and "0033CC" in tx and "<w:strike/>" in tx,
        "",
    )
    resp = "\n".join(text(SUB / "EDITOR_RESPONSE_ODD_FINAL.docx"))
    check("response cites ECOMOD-26-2231", "ECOMOD-26-2231" in resp, "")
    check("response first person singular", " we " not in resp.lower(), "")
    check(
        "decision letter verbatim inserted",
        "[Verbatim text" not in resp,
        "PENDING author: placeholder present" if "[Verbatim text" in resp else "",
    )
    cov = "\n".join(text(SUB / "EM_ODD_COVER_LETTER_FINAL.docx"))
    check(
        "cover letter cites ECOMOD-26-2231 and Grimm",
        "ECOMOD-26-2231" in cov and "Grimm" in cov,
        "",
    )
    check("cover letter first person singular", " we " not in cov.lower(), "")
    pdf = SUB / "EM_ODD_REVISED_MANUSCRIPT_FINAL.pdf"
    pages = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    ptxt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
    check(
        "PDF renders",
        "Pages:" in pages and "2.7 Submodels" in ptxt,
        [x for x in pages.splitlines() if x.startswith("Pages")][0],
    )
    check("PDF has no replacement glyphs", "\ufffd" not in ptxt, "")
    qc = pd.DataFrame(rows, columns=["check", "result", "detail"])
    md = [
        "# FINAL ODD QC MATRIX",
        "",
        "Generated by scripts/qc_odd_submission.py.",
        "",
        "| check | result | detail |",
        "|---|---|---|",
    ]
    md += [f"| {a} | {b} | {c} |" for a, b, c in rows]
    (ROOT / "odd_resubmission/FINAL_ODD_QC_MATRIX.md").write_text("\n".join(md) + "\n")
    files = sorted(
        p
        for p in SUB.rglob("*")
        if p.is_file() and p.suffix != ".zip" and p.name != "SHA256SUMS.txt"
    )
    (SUB / "SHA256SUMS.txt").write_text("".join(f"{sha(p)}  {p.relative_to(SUB)}\n" for p in files))
    package = SUB / "EM_ODD_SUBMISSION_PACKAGE_FINAL.zip"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files + [SUB / "SHA256SUMS.txt"]:
            z.write(p, p.relative_to(SUB))
    print(qc.to_string())


if __name__ == "__main__":
    main()
