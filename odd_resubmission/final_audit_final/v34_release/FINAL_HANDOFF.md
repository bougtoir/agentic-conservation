# FINAL HANDOFF — v3.4 release (ECOMOD-26-2231 new submission)

Verdict now: **STAGE A READY — AWAITING AUTHOR MERGE** (tag v3.4 not created; release not frozen → overall CONDITIONAL GO — RELEASE NOT FROZEN).

Devin did NOT merge any PR, create any tag, push to public `main`, delete branches/tags, force-push, submit, or contact the journal.

## PR MERGE HANDOFF

Must be merged for this release:

| PR | Purpose | State | Head | Depends on | Ready |
|---|---|---|---|---|---|
| https://github.com/bougtoir/wip/pull/839 (branch `devin/1795095138-agentic-v34-release-ref`; current head shown on the PR) | generator cites `odd-2020-revision-v3.4-inline` by name; regenerated package; release plan/audit | open | see PR | master `cab9beae` | yes, if CI passes |

Only this PR remains. Merge order: this PR alone.

Already merged, no action:

| PR | Merge commit |
|---|---|
| https://github.com/bougtoir/wip/pull/795 | `83587d5876da967f35f29d4c155eebab6758785c` |
| https://github.com/bougtoir/wip/pull/801 | `75a2f2d91830fac42a26e16f34e53664bd5936b6` |
| https://github.com/bougtoir/wip/pull/826 | `eac36d92b762f474543829e96b12de64ca8db3ed` |
| https://github.com/bougtoir/wip/pull/829 | `8d83812d14091c1aa12d49d59682e00c72f13091` |
| https://github.com/bougtoir/wip/pull/835 | `4963584aeab3720b563b2ea5f5aefe614d842963` |
| https://github.com/bougtoir/wip/pull/830 | `cab9beaecfd9e2e985456e651d6ff9b1298a6b73` |

Closed/unmerged/superseded: none open for this project. Branch `devin/1794454843-agentic-mirror-audit-post801` (commit a1e5679) was pushed without a PR; its content is superseded by #829/#830 and should not be merged.

## AUTHOR ACTION CHECKLIST

1. Merge the Stage A PR.
2. Verify the public mirror sync: new `wip-sync` fast-forward on `main` naming the merged wip commit (Devin can check; `V34_TAG_RELEASE_PLAN.md` B2–B3).
3. Authorise creation of the immutable annotated tag `odd-2020-revision-v3.4-inline` at that verified public commit only (B4). Never move v3.3 or older tags.
4. Validate a clean clone of the tag (B5–B6); Devin writes `V34_TAG_PUBLICATION_AUDIT.md`.
5. Submit in Editorial Manager as a new submission referring to ECOMOD-26-2231, using `odd_resubmission/submission/final/` (clean DOCX, tracked DOCX, PDF, cover letter, editorial response, Figures 1–10) whose hashes match `SHA256SUMS.txt`.

Separate owner item (does not block the tag): public `main` protection NOT VERIFIED / UNRESOLVED (no ruleset; protection API 403). Steps: `../mirror_guard/PUBLIC_MIRROR_OWNER_UI_STEPS.md`.
