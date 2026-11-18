"""Rebuild the integrated (inline-figure, appendix-free) ODD submission.

Steps: corrected figure variants -> manuscript generator -> PDF render with
LibreOffice. No simulation is run; every number is read from preserved outputs.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    subprocess.run([sys.executable, "scripts/make_odd_figures.py"], cwd=ROOT, env=env, check=True)
    subprocess.run(
        [sys.executable, "src/agentic_conservation/documents_em_odd.py"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    sys.path.insert(0, str(ROOT / "src"))
    from agentic_conservation.documents_em_odd import OUT_DIR, OUTPUTS

    out = ROOT / OUT_DIR
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        raise SystemExit("LibreOffice (soffice) is required to render the PDF")
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out), OUTPUTS["clean"]],
        cwd=out,
        check=True,
        capture_output=True,
    )
    (out / OUTPUTS["clean"].replace(".docx", ".pdf")).replace(out / OUTPUTS["pdf"])
    print(out / OUTPUTS["pdf"])


if __name__ == "__main__":
    main()
