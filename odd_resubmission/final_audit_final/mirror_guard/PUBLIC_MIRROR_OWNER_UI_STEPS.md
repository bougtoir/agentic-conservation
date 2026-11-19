# PUBLIC MIRROR OWNER UI STEPS (bougtoir/agentic-conservation)

Ruleset (recommended):
1. Open https://github.com/bougtoir/agentic-conservation/settings/rules → **New ruleset** → **New branch ruleset**.
2. Ruleset name: `protect-main`. Enforcement status: **Active**.
3. Bypass list: leave **empty** (do not add Repository admin).
4. Target branches → **Add target** → **Include by pattern** → `main`.
5. Branch rules: keep **Restrict deletions** and **Block force pushes** checked; leave all other rules unchecked (no pull request, status checks, signed commits, linear history).
6. **Create**.

Alternative (classic): Settings → Branches → **Add classic branch protection rule** → pattern `main`; leave every "Require …" box unchecked; check **Do not allow bypassing the above settings**; leave **Allow force pushes** and **Allow deletions** unchecked → **Create**.

Checklist after saving (Devin can verify the first two without admin rights):
- [ ] `GET /repos/bougtoir/agentic-conservation/rules/branches/main` lists `non_fast_forward` and `deletion` (ruleset), or `branches/main` shows `protected: true` (classic).
- [ ] Next canonical sync run on master ends with main fast-forwarded (or unchanged when nothing changed), with no rejection message for agentic-conservation.
- [ ] Tag odd-2020-revision-v3.3-inline still → 84f287403609.
