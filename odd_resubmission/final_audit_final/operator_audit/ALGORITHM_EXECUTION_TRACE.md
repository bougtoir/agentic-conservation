# Algorithm execution trace (Algorithms 1–2 vs implementation)

Code: `src/agentic_conservation/simulation.py` (blob a04b6af60ff3, identical in wip master 8d83812d1409 and public tag `odd-2020-revision-v3.3-inline` → 84f2874036094595f4d7e515133e6c48e2d50c06). Entry point `run_simulation` (l. 494); annual loop l. 557.

## Algorithm 1 — one annual step

| MS step | code (l.) | executed behaviour | verdict |
|---|---|---|---|
| 1 funding shock | 565–568 | `funding_rng.random() < 0.015` → `budget *= 0.72`; skipped for S0 | PASS |
| 2 allocation | 569–576 | `spend_c = B_t·a_c / max(Σa, 1)`; all Σa = 1.00, so equal to MS `/Σa` | PASS |
| 3 environment | 577–586 (`_quality_update` 174–219) | trend (wild only) → climate (origin −, alternative +0.65) → restoration (wild only) → collapse (collapse scenario) → catastrophe (one wild node) → clip | PASS after Eq. 1 W_j fix (P1) |
| 4 observation | 587–602 | true suitability from q_t; counts = true × LogNormal(0, 0.18) for stage ≥ 2 else NaN; quality = q_(t−1) + N(0, 0.10) clipped [0, 1]; decision suitability = Eq. 2(observed) | PASS |
| 5 discovery | 603–616 (`_discover` 450–473) | latent, extant (before discovery), stage < 5; ≤ 1 stage | PASS |
| 6 action | 617–666 (`_move_agents` 312–447) | moves; then movement deaths (0.025, all moved), release deaths (0.08, released & still alive), transit infection 0.03·(1 − 0.65·min(1, rescue/(0.25·moved))) on surviving susceptible movers | PASS |
| 7 disease | 668–691 | per non-biobank node: prevalence before infections; infect p = clip(β_j·prev; 0, 0.65); recovery 0.32 for all infected incl. newly infected | PASS after wording (P2) |
| 8 survival | 693–723 | Eq. 6; one Bernoulli per alive individual; deaths applied together | PASS |
| 9 ageing/health | 725–731 | age +1; health += N(0, 0.015), clip [0.35, 1] | PASS |
| 10 reproduction | 732–819 | species × node (biobank excluded); mature = age ≥ 2 after ageing; Eq. 7; diversity-aware pairing if genetics spend > 0; cap 1200 truncation in species order | PASS |
| 11 biobank/EBD | 820–835 | coverage ×0.99, + spend_biobank/B_t·0.05 for extant visible species; EBD = latent, extinct, stage < 2 | PASS |
| 12 welfare | 836–887 | node welfare − captivity − 7 burdens; no demographic feedback | PASS |
| 13 engagement/budget | 888–906 | Eq. 4 (B_t = this year's post-shock budget) | PASS |
| 14 outputs | 908–1023 | year 50/100 snapshots; reproductive proxy (≥1 mature F and M co-located, non-biobank node) and wild persistence (any alive in node with wild flag: origin, alternative, reserve, semi-wild) at year 100 | PASS |

State boundaries: survival uses health after movement stress and infection state after recoveries; births use survivors after ageing; deaths before births. RNG: one keyed stream per process×year (`_keyed_rng`), so policy-independent draws (funding, catastrophe) are shared across paired policies; policy-dependent draws are not common random numbers (as stated in 2.4 Stochasticity).

Exception paths: S0 → budget 0, no spending, no shock; S6 → movement returns empty (l. 329–334); no visible species → no moves (l. 344–346); no living individuals → exposure 0, welfare means 0; empty biobank → coverage 0; rescue spend 0 → no moves.

## Algorithm 2 — action selection (lifted pseudocode)

```
rule = decision_rule_override or policy
if rule in {S0,S6} or movement_disabled or rescue <= 0: return none
C = max(1, floor(rescue/2.5)); moved = 0
V = species with stage >= 2; if V empty: return none
for sp in V sorted by (nan_to_num(1/(1+n_obs)) + 1 - s_obs[sp,origin], sp) descending:
    if moved >= C: break
    cand = alive individuals of sp
    S1: cand in managed-type nodes;  target = argmax s_obs over wild-type nodes
    S3: if s_obs[sp,origin] < 0.48: cand at origin, target = argmax{cons_zoo, breeding}
        elif year>=5 and s_obs[sp,origin] >= 0.62: cand not at origin and release_ready>=0.40, target = origin
        else: skip species
    S2/S4/S5/S7: cand with s_obs[sp,current node] < 0.58; target = argmax score (Eq.5);
        S2 -> conventional zoo
    cand = cand not already at target
    take = min(|cand|, C-moved, max(1, floor(0.2|cand|)), max(0, capacity_target - n_sp_at_target))
    choose take without replacement (movement RNG); update node, health stress,
    habituation (+0.08 managed / -0.05), wildness (+0.06 wild / -0.07), release_ready (+0.05 semi-wild / -0.01)
    released = chosen from managed-flag node to wild-flag target
```

Comparison with MS Algorithm 2: steps 1–7 match after clarifying step 4 (S3 candidate sets) and step 6 (species-specific free capacity; individuals at target excluded). Biobank: never a target (S1/S2/S3 choose non-biobank sets; argmax rules give it −1 + ≤0.0475 versus ≥ −0.015 for every other node). S6 rescue share: spent and counted in cost (l. 576), never converted to moves. S5 is a plain-score argmax; S7 a weighted-score argmax — no expected utility or rollout (P1 nomenclature, fixed in 2.4). Counts: `moved` = attempted moves, release events counted before release mortality (2.7.6 says so); wild persistence is a separate year-100 endpoint. Tie-breaking: equal risk → higher species index first; equal score → lowest node index (`np.argmax`) (P3, not disclosed, no scientific effect).
