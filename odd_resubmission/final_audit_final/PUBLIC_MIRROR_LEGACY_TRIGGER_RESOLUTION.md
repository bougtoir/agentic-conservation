# PUBLIC MIRROR LEGACY TRIGGER RESOLUTION

Status: **CONDITIONAL** — the cited release tag is valid and reproducible;
public `main` is not protected against future regressions until the author
takes one of the actions in §4.

## 1. How the workflow runs (GitHub Actions semantics)

| Event | Which YAML runs | Can reach the legacy code? |
|---|---|---|
| `schedule` (cron) | default branch (master) only | No. Master's YAML (after #801) maps this mirror only from `devin/agentic-conservation-public-sync`, fast-forward, no `--force`. |
| `push` | the YAML in the pushed commit, if that branch is in that YAML's `on.push.branches` | **Yes**, when the pushed branch carries the pre-#801 YAML. |
| `workflow_dispatch` | the YAML of the chosen ref | **Yes**, if someone dispatches on a legacy branch. |

## 2. Evidence

- Scan of all 903 wip remote branches: 305 carry a pre-#801 workflow that maps
  at least one source branch to `agentic-conservation` and force-pushes; 39 of
  them list themselves in their own `on.push.branches`, so a push to any of
  them runs the legacy sync (e.g. devin/1790254872-functional-geometry-revision,
  devin/1792230689-jog-final-audit, devin/1793160780-fossil-mortality-final-qc).
- Demonstrated regression: on 2026-11-10 a push to
  devin/1790254872-functional-geometry-revision ran the legacy YAML and
  force-pushed an obsolete tree over the mirror `main` (Actions log, recorded in
  ../final_audit/PUBLIC_MIRROR_SYNC_STABILITY_AUDIT.md).
- The legacy loop reads source branches named in its BRANCH_MAP. The mapped
  sources that still exist are the five retired branches:
  devin/1790233047-agentic-conservation, devin/1793050713-ecological-modelling-retarget,
  devin/1793300000-reversal-theory, devin/1793300000-em-reversal-integration,
  devin/1793164552-em-final-qc. When a source branch is missing, the legacy
  loop prints "SKIP: Branch … not found in wip" and does not push.
- Recent runs (2026-11-17/18) were on master and on two pointer branches whose
  head equals master; mirror `main` advanced by fast-forward only:
  3e512fd2 (post-#826 canonical sync) → 84f28740 (this release).
- Mirror-side protection could not be set from this session: the GitHub
  integration has no admin permission on bougtoir/agentic-conservation
  (branch-protection API: HTTP 403).

## 3. Tests (local mock, `tests/test_mirror_guard_mock.py`)

- A bare repository with a force-push restriction (`receive.denyNonFastForwards`)
  rejects the legacy push (parentless commit + `--force`) and keeps `main`;
  the canonical overlay commit (parent = current head) is accepted and keeps
  every existing file.
- The legacy YAML contains the missing-source SKIP guard and `git push --force`.

## 4. Author actions (either one closes the risk; neither was done)

A. **Preferred, nothing deleted:** in bougtoir/agentic-conservation → Settings →
   Rules (or Branches), add a rule for `main` that blocks force pushes and
   deletions and applies to administrators/bypass actors too. The canonical
   sync uses plain fast-forward pushes and keeps working; every legacy push is
   rejected. Tags are not affected.
B. Delete the five retired source branches listed in §2 after archiving them as
   tags (`archive/<branch>` at their current heads). The legacy loop then skips
   this mirror. This needs separate approval.

No branch, tag or workflow on other projects was changed. Existing tags
v2, v3-inline, v3.1-inline, v3.2-inline were left as they are; the final
release is v3.3-inline (84f287403609).
