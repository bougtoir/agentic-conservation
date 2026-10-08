PYTHON ?= python3
export PYTHONPATH := src

.PHONY: quick full fetch empirical figures package test lint clean

quick:
	$(PYTHON) scripts/run_pipeline.py --mode quick

full:
	$(PYTHON) scripts/run_pipeline.py --mode full

fetch:
	$(PYTHON) scripts/fetch_empirical.py

empirical:
	$(PYTHON) scripts/analyze_empirical.py
	$(PYTHON) scripts/build_literature_audit.py

figures:
	$(PYTHON) scripts/build_outputs.py

package:
	$(PYTHON) scripts/build_submission.py

audit:
	PYTHONPATH=src $(PYTHON) scripts/run_structural_audits.py --mode full

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src scripts tests

clean:
	rm -rf data/processed figures results submission tables
	rm -f data/source_inventory.csv FINAL_REPORT.md
	rm -f FINAL_SUBMISSION_READINESS.md
	rm -f docs/double_blind_audit.md docs/integrity_audit.md
	rm -f docs/model_bias_audit.md docs/reproducibility_audit.md
	rm -f docs/reviewer_audit.md provenance/hard_code_audit.md
	rm -f provenance/run_manifest.json
	rm -f manuscript/ARTICLE_IMPACT_STATEMENT_OPTIONS.md
	rm -f manuscript/CONSERVATION_BIOLOGY_SUBMISSION_CHECKLIST.md
	rm -f manuscript/COVER_PAGE_TEMPLATE.md
	rm -f manuscript/DATA_CODE_AVAILABILITY.md
	rm -f manuscript/HUMAN_AUTHORING_PACKET.md
	rm -f manuscript/SUPPORTING_INFORMATION.md
	rm -f manuscript/INLINE_MANUSCRIPT_HUMAN_REVIEW_DRAFT.docx
	rm -f manuscript/SUPPORTING_INFORMATION_INLINE.docx
	rm -f manuscript/EDITABLE_TABLES.docx
	rm -f manuscript/EDITABLE_FIGURES.pptx
	rm -f manuscript/FIGURE_DECK.pptx
	rm -f manuscript/FIGURE_REGENERATION.md
	rm -f manuscript/COVER_PAGE_TEMPLATE.docx
	rm -f manuscript/DOCUMENT_VALIDATION.txt
