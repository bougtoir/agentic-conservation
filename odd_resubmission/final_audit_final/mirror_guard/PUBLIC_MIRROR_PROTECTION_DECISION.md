# PUBLIC MIRROR PROTECTION DECISION

Status: **CONDITIONAL** (guard requested, not yet configured).

| Item | Evidence (read 2026-11-18) |
|---|---|
| Mirror main | 84f2874036094595f4d7e515133e6c48e2d50c06, descends from the v3.3 tag commit; contains tables/table9_reversal_predictors_corrected_v1.csv and manuscript/, submission/, frozen_cb_rejection_2026-10-26/ |
| Release tag | odd-2020-revision-v3.3-inline: annotated tag object f35216f19c6881380361b251c5be2e6e8a4b2c68 → commit 84f2874036094595f4d7e515133e6c48e2d50c06 |
| Server-side protection on main | none: `GET /repos/bougtoir/agentic-conservation/branches/main` → `protected: false`; `GET …/rulesets` → []; `GET …/rules/branches/main` → [] |
| Who writes main | wip workflow `sync-to-repos.yml` with secret SYNC_PAT; the workflow checks that the PAT belongs to `bougtoir`, the repository owner (admin of a personal repo). Legacy and canonical runs use the same credential |
| Canonical writer | master YAML (after #801; master now 8d83812d1409): agentic mapped only from devin/agentic-conservation-public-sync, overlay on current main, parent = current main, push without --force |
| Legacy writer | 305 wip branches keep the pre-#801 YAML (git push --force of a parentless commit); 39 run it on their own push; any can run it by workflow_dispatch; schedule uses master only. Regression observed 2026-11-10 |
| Devin permissions on the mirror | none (repo permissions all false; branch-protection API HTTP 403), so the rule cannot be set from this session |

Decision: a ruleset (or classic branch protection) on `main` only, with
"Block force pushes" and "Restrict deletions", **no bypass actors**, enforced
for administrators. Because legacy and canonical runs both authenticate as the
owner, an owner bypass would also exempt the legacy writer, so bypass must be
empty. The canonical writer only makes fast-forward pushes and needs no
bypass. No other rule (PR, reviews, checks, signatures) is required.

Fallback (not authorised; needs separate approval): archive-tag and delete the
five retired source branches. Every legacy YAML found skips a missing source
branch ("SKIP: Branch … not found in wip"), but the ruleset is preferred
because it does not depend on that.
