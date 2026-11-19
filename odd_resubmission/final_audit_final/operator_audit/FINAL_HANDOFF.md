# Final handoff (operator audit)

## PRs
| PR | purpose | status | action |
|---|---|---|---|
| [#795](https://github.com/bougtoir/wip/pull/795) | ODD 2020/S1 rebuild, Ψ provenance | merged | none |
| [#801](https://github.com/bougtoir/wip/pull/801) | fast-forward-only mirror sync | merged | none |
| [#826](https://github.com/bougtoir/wip/pull/826) | inline figures, appendix removed | merged | none |
| [#829](https://github.com/bougtoir/wip/pull/829) | B0 correction, final package | merged | none |
| [#830](https://github.com/bougtoir/wip/pull/830) | mirror-guard docs only | open | merge optional (docs) |
| this PR | operator-level audit; Eq. 1 / §2.4 / Alg. 2 wording fixes; rebuilt final package | open | **merge before submission** |

Recommended order: this PR, then #830 (independent; either order works). No superseded PR must be merged; none is open.

## Post-merge checks
1. `make integrated` on master → 113/113 PASS, ZIP hash recorded in `SHA256SUMS.txt`.
2. Mirror sync fast-forwards `main` (no force); tag v3.3 still → 84f287403609.

## Conditions for submission
- Use `odd_resubmission/submission/final/` from the merged master (clean DOCX, tracked DOCX, PDF, cover letter, response, Figures 1–10).
- Author approval of submission in Editorial Manager (new submission, ref. ECOMOD-26-2231). Devin does not submit.
- Mirror ruleset (PR #830 steps) is recommended but does not block submission; the manuscript cites the immutable tag.
