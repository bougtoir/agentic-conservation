# Final operation-level equation / algorithm ↔ implementation audit

## 1. Locked artifacts (before any edit)

| item | identifier |
|---|---|
| wip master | 8d83812d14091c1aa12d49d59682e00c72f13091 (merge of #829) |
| public tag `odd-2020-revision-v3.3-inline` | tag object f35216f19c6881380361b251c5be2e6e8a4b2c68 → commit 84f2874036094595f4d7e515133e6c48e2d50c06 |
| public `main` at audit | 0f6eb558f5cbbd809745c66cd5f1704417dc23f0 (fast-forward descendant of v3.3; sync of wip 8d83812d) |
| audited clean DOCX (master) | sha256 a44041e4fbd21698bccba73bccbcca91dfb974c842a8f61ce6388d5c1bab9bb8 |
| audited PDF (master) | sha256 a8d94770ea67e3da79975a723ede9aec924f0839300c825cecd4d775e654f108 |
| builder `documents_em_odd.py` (master) | sha256 0e269ab372e66e2c984ec016b60078bbac1bb24a9acfbd87b130ce41888c750b |
| `simulation.py` | sha256 ebf1c70efa8882dfcd5ff645430db321860549865736a29e21a113b923e7a564 (git blob a04b6af60ff3) |
| `minimal_model.py` | sha256 eee300a23f7599b5aab6ff4162fefd0016a661b53490c1dc67583a2443b5a4a2 (blob 79155afcfde5) |
| `config/base.json`, `nodes.json`, `species.json` | ed1dfe75…, 6cb67882…, fc6b78e9… |

Model identity: `simulation.py`, `minimal_model.py`, the three configs, `holdout_psi.csv`, `table9_reversal_predictors.csv` and `table9_reversal_predictors_corrected_v1.csv` have identical git blobs in wip master and the cited v3.3 tag. The manuscript cites the same scientific model version.

Equations were read from the OMML (`m:oMath`, 20 objects for Eqs. 1–8, including the `z` helper lines of Eqs. 1, 2, 6) and the ex-situ factor of Eq. 7 was checked in XML (`m:sSup` with exponent M_j). Rendered PDF pages were inspected.

## 2. Equation crosswalk
Full term-by-term table: `EQUATION_IMPLEMENTATION_CROSSWALK.csv` (34 rows). Summary:

| Eq. | result | issue |
|---|---|---|
| 1 habitat | **P1 fixed** | code applies background trend δ and restoration only to the four wild nodes; managed-only nodes keep base quality. Eq. 1 showed both terms for every node. Now `− W_j·δ … + W_j·(spend_hab/B_0)·e·r_j`, where-clause defines W_j, scenario scaling of δ, catastrophe on one wild node. Climate t-indexing (year 1…100), 0.65 gain, clip order, cumulative 0.606 verified. |
| 2 suitability | PASS | all five literals, M_j(1−W_j) indicator, clip [0.02, 0.99]. |
| 3 discovery | PASS | caps, coefficients, d_x stage 0 only, +spend_hab/1000 inside min, ≤1 stage/yr. |
| 4 engagement/budget | PASS | x̄ individual-weighted; B_t = post-shock budget; one-year shock. |
| 5 target score | P2 fixed; P1 fixed | b_π,j and φ were undefined; where-clause added. S5/S7 labels "greedy expected utility"/"forward-rollout proxy" overstated the implementation (plain and weighted score argmax); §2.4 Objectives and Prediction rewritten. Table 4 labels come from the frozen registry `tables/table2_policies.csv` and were left unchanged; the text now says they are legacy labels. |
| 6 survival | PASS | every additive term, flags from node columns, clip [0.05, 0.995], synchronous deaths. |
| 7 reproduction | PASS | n_F, density per species, ex-situ exponent M_j, infection/inbreeding floors, cap order (disclosed in §2.3). |
| 8 Ψ | PASS | three arms, ε = 0.02, exact H + C telescoping, MIN_BREEDING_POP = 4, V1 cohort discovery, equal quota; bundled-contrast caveat present. |

## 3–4. Algorithms
See `ALGORITHM_EXECUTION_TRACE.md`. Algorithm 1 order matches code exactly (14 steps). Algorithm 2 matches after two wording clarifications (S3 candidate sets; species-specific free target capacity, individuals at target excluded).

## 5. Unnumbered submodels and endpoints
- Observation: LogNormal(0, 0.18) counts for stage ≥ 2; q(t−1) + N(0, 0.10) clipped [0, 1]. PASS.
- Disease: prevalence fixed before infections; newly infected can recover the same year (P2, wording added to §2.7.7).
- Biobank: decay 1 %, growth for extant visible species, no individuals (P2: Fig. 1 caption now says the protected reserve, like the semi-wild station, is both wild and managed, as in `nodes.json`).
- Welfare: normative, no feedback. EBD: latent, extinct, stage < 2. Genetics: F = mean + 0.08 same founder, ×0.82 diversity-aware. PASS.
- Initialisation: all 364 individuals start at the origin node (P2: was "wild nodes").
- Endpoints: individual, reproductive proxy (mature F+M co-located in non-biobank node), wild (any node with wild flag; now listed in §2.1). Paired S7 − S6, 2×paired SE, replicate as unit (`analysis.py`, unchanged). PASS.
- Ψ historical V0 vs V1 and prospective evaluation unchanged; Table 11 B0/B1/B2 read from `tables/table9_reversal_predictors_corrected_v1.csv` (builder l. 2407), not hard-coded. PASS.
- Perfect-current-state comparator: `oracle=True` returns true counts and current quality (l. 249–250). PASS.

## 6. Probes
`tests/test_operator_audit_probes.py` (11 tests, all pass; no result file touched, no sweep): Eq. 1 wild-only trend/restoration and managed-node constancy; climate t = 1 vs 100 and Σ = 0.606 for all four forms; Eq. 1/2 clip bounds; biobank never selected; take quota floor/minimum 1; S0/S6 never move; Eq. 3 single-stage advance and no advance when extinct; cap truncation order; Eq. 7 exponent; H + C identity. Everything else was settled by source inspection (line references in the CSV).

## 7. Issues and resolution
| id | severity | issue | resolution |
|---|---|---|---|
| I1 | P1 | Eq. 1 applied δ and restoration to all nodes | OMML + where-clause fixed |
| I2 | P1 | S5 "greedy expected utility", S7 "forward-rollout proxy" claimed computations not implemented | §2.4 rewritten; Table 4 registry labels kept, explained |
| I3 | P2 | b_π,j, φ undefined in Eq. 5 | where-clause added |
| I4 | P2 | Alg. 2 step 4 S3 candidate sets, step 6 capacity semantics | wording clarified |
| I5 | P2 | disease timing (same-year recovery) | wording added |
| I6 | P2 | Fig. 1 caption omitted that reserve is managed | caption fixed (image unchanged) |
| I7 | P2 | initialisation "wild nodes" → origin node; wild endpoint node list | wording fixed |
| I8 | P3 | tie-breaking (higher species index; lowest node index); NaN count → risk term 0 for newly visible species; B_0 symbol shared with baseline B0 | reported only |

No P0. No model code, parameter, registry, figure image, table value or numerical result changed.

## 8. Post-fix verification
- `make integrated`: 113/113 PASS; PDF 45 pages; 21 OMML objects (Eq. 1 wraps to three lines); tables identical to before; cover letter and response text identical.
- pytest 59 passed; ruff clean; `scripts/final_numeric_audit.py` 157/157.
- New hashes: clean DOCX 07400f26…, tracked 162cb469…, PDF 73076566…, ZIP 406e4987… (full list in `odd_resubmission/submission/final/SHA256SUMS.txt`).
