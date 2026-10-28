# Model specification (reverse-engineered from the executable code)

Every statement below is derived from `src/agentic_conservation/simulation.py`
and `src/agentic_conservation/analysis.py` (implementation source of truth),
not from prior manuscript text. Equation identifiers (E1–E18) are used in
`EQUATION_ALGORITHM_CODE_MATRIX.csv`, which maps each equation to the exact
function, config parameter, test, and output metric.

## Method identity (what this model is and is not)

- This is a **discrete-time, individual-based Monte Carlo simulation**: each
  simulated year applies stochastic transition rules to a fixed array of
  individual agents using pseudo-random draws keyed by (replicate seed,
  process, year).
- It is **not** Markov chain Monte Carlo: no posterior sampling or Bayesian
  inference is performed; "Monte Carlo" here means repeated stochastic
  simulation replicates.
- It is **not** a solved partially observable Markov decision process
  (POMDP): policies are fixed decision rules (heuristics), not policies
  optimized over a belief state. A state-dependent rule that reads current
  observations is not the same as solving a POMDP.
- "Perfect-current-state-information comparator" (formerly labelled
  "oracle" in code and prose) means: the same S7 decision rule is rerun with
  true current abundance and true current habitat quality substituted for
  its noisy delayed observations. It still uses the same decision heuristic,
  sees no future environmental draws, and performs no hindsight action
  selection. The paired difference between comparator and feasible runs is
  an information effect in model units — it is not EVPI and not the value
  of solving a POMDP.

## Entities and state

- 8 synthetic species; 5 initially known, 3 latent. Traits per species
  (synthetic, unitless unless stated): growth, mortality (annual
  probability), niche_breadth, habitat_specificity, climate_sensitivity,
  anthropogenic_sensitivity, dispersal, detectability, fertility,
  social_dependence, migration_need, captivity_tolerance; initial_n
  individuals; known flag.
- 9 nodes (index 0–8): origin wild habitat (0), alternative wild habitat
  (1), protected reserve (2), conventional zoo (3), conservation zoo (4),
  breeding center (5), semi-wild pre-release (6), rehabilitation facility
  (7), biobank (8, non-living store; no individuals ever occupy it — all
  demography and movement loops exclude index 8). Node attributes: type,
  wild, managed, base_quality, capacity, disease, predation, anthropogenic,
  welfare, cost, connectivity, research, visitor_exposure, restoration.
- Individual state vector i: species, sex, age, origin node, current node,
  founder id, inbreeding, health ∈ [0.35, 1], infection ∈ {0 susceptible,
  1 infected, 2 recovered}, wildness, habituation, stress_tolerance,
  foraging, release_ready, alive.
- Species knowledge stage k_s ∈ {0..5}: initially 5 for known, 0 for
  latent. Stage ≥ 2 makes a species visible to observation and
  decision-making. Stage semantics: 0 exists, 1 detected, 2 described,
  3 monitored, 4 threat recognized, 5 protected.
- Time: annual steps t = 1..100. Horizon is a modelling choice, not an
  empirical forecast window.

## Annual update order (Algorithm 1, implemented order)

Each year t, in exactly this order:

1. Funding: with probability p_fund = 0.015 the budget is multiplied by
   0.72 (skipped for S0).
2. Budget split: spending_k = budget · a_{π,k} / Σ a_π over the seven
   allocation channels {habitat, survey, rescue, ex_situ, genetics,
   biobank, engagement}; cumulative spend recorded.
3. Environment (E2): wild-node quality updated by scenario trend,
   directional climate displacement, habitat investment, scheduled
   collapse and stochastic catastrophe; clipped to [0.05, 0.98].
4. Observation (E3–E4): observed species counts (true counts × lognormal
   noise, only for stage ≥ 2) and observed node quality (quality delayed
   by 1 year + Gaussian noise). True suitability is computed from true
   quality for ecological transitions; decision suitability is recomputed
   from observed quality for policy use (E1 applied to q_obs).
5. Discovery (E5): latent species may advance one stage.
6. Movement/action (E6–E9, Algorithm 2): eligible individuals relocated
   under the policy's rule; relocation stress applied to health,
   habituation, wildness, release readiness; movement and release
   mortality drawn; transit infection with quarantine coverage.
7. Within-node disease (E10): prevalence-scaled infection and recovery.
8. Survival (E11): individual Bernoulli survival; deaths applied.
9. Ageing and health drift; reproduction (E12–E14): per species–node,
   Poisson births with optional diversity-aware paternity; capped by
   max_individuals = 1200.
10. Biobank and EBD bookkeeping (E15–E16).
11. Welfare (E17) accumulation and welfare-burden decomposition.
12. Human feedback (E18): engagement update; next year's budget reset as
    budget_{t+1} = B0 · (0.82 + 0.24 · engagement) for nonzero policies.
13. Year-50 snapshot and trajectory recording.

## Equations

Indices: s species, j node, i individual, t year. All probabilities per
year. clip(x; a, b) bounds x to [a, b].

**E1 Suitability.** From `_species_node_suitability`:

suit_{s,j} = clip( q_j·(0.72 + 0.28·breadth_s) − spec_s·(1 − q_j)·0.32
             + M_j·(1 − W_j)·(tol_s − 0.5)·0.25
             − M_j·(1 − W_j)·mig_s·0.24 ; 0.02, 0.99 )

with q_j node quality, spec_s habitat_specificity, tol_s
captivity_tolerance, mig_s migration_need, M_j managed flag, W_j wild
flag. The managed-non-wild terms apply to zoo/conservation
zoo/breeding/rehabilitation only — not to reserve or semi-wild (both are
wild∧managed).

**E2 Habitat quality** (`_quality_update`):

- Scenario trend subtracted from wild q_j: directional_change d = 0.006;
  slow_deterioration 0.5d; rapid_deterioration 2d; restoration −0.6d;
  stationary and abrupt_collapse 0.
- Directional climate shift: q_0 -= climate_velocity · t/100;
  q_1 += 0.65 · climate_velocity · t/100.
- Habitat investment: q_wild += (spend_habitat / B0) · 0.025 · restoration_j.
- abrupt_collapse scenario: at t = max(2, ⌊100/3⌋) = 33, q_0 -= 0.70.
- Catastrophe: with p = 0.035, one random wild node loses U(0.16, 0.38).
- q_j clipped to [0.05, 0.98].

**E3 Observation** (`_observed_state`): n_obs_s = n_s · LogNormal(0, 0.18)
if stage_s ≥ 2 else NaN (unavailable). q_obs_j = clip(q_{j,t−1} + N(0,
0.10), 0, 1) — one-year delay, not current truth. Comparator runs
substitute n_s and q_{j,t} directly.

**E4 Discovery** (`_discover`): with scale = spend_survey / 10, a latent
species at stage k advances one stage per year with probability

p_0 = min(0.95, 0.005 + 0.16·scale·detect_s)
p_1 = min(0.85, 0.005 + 0.12·scale)
p_2 = min(0.75, 0.005 + 0.10·scale)
p_3 = min(0.65, 0.005 + 0.09·scale)
p_4 = min(0.60, 0.005 + 0.06·scale + spend_habitat/1000)

At most one stage per year; background detection p = 0.005.

**E5 Policy budgets**: spend_k = B_t·a_{π,k}/Σa_π; Σa_π ≤ 1 enforced.
S0 has B_t = 0.

**E6 Movement eligibility & risk ranking** (`_move_agents`): skipped for
S0 and S6 and when spend_rescue = 0. Move capacity C_move =
⌊spend_rescue/2.5⌋ individuals per year. Species ranked by decreasing
risk r_s = 1/(1 + n_obs_s) + (1 − suit_obs[s,0]); latent species excluded
until stage ≥ 2.

**E7 Per-policy eligibility & target**:

- S1: candidates in managed nodes → best wild node by decision
  suitability.
- S2: all visible species → node "zoo" (conventional zoo), unconditionally.
- S3: refuge mode if suit_obs[s,0] < 0.48 → origin individuals → best of
  {conservation_zoo, breeding} by suitability; return mode if t ≥ 5 and
  suit_obs[s,0] ≥ 0.62 → non-origin individuals with release_ready ≥ 0.40
  → origin. Otherwise no move.
- S4/S5/S7: individuals with current decision suitability < 0.58.
  Target = argmax_j score_j with score_j = suit_obs[s,j] − 0.04·cost_j +
  0.03·research_j, score_8 = −1; S4 adds 0.10 for nodes of type
  {protected_reserve, conservation_zoo, breeding_center,
  semi_wild_pre_release}; S7 adds 0.08·restoration_j + 0.05·research_j;
  S4 and S7 add origin_fidelity = 0.20 to score_0.
- Per species take = min(#candidates, C_move − moved,
  max(1, ⌊#candidates/5⌋), remaining target capacity) — at most ~20% of
  a species' candidates per year.

**E8 Relocation effects**: health_i ×= (1 − 0.1·(1 − stress_tol_i));
habituation_i += 0.08 if target managed else −0.05; wildness_i += 0.06
if target wild else −0.07; release_ready_i += 0.05 if target semi-wild
else −0.01. Moved individuals die with p = 0.025; managed→wild releases
additionally die with p = 0.08.

**E9 Transit disease**: each susceptible moved individual is infected with
p = 0.03·(1 − cov·0.65), where quarantine coverage cov = min(1,
spend_rescue/(0.25·moved)).

**E10 Within-node disease**: in node j (j < 8), prevalence ρ_j; each
susceptible infected with p = clip(disease_j·ρ_j; 0, 0.65); each infected
recovers (state 2) with p = 0.32.

**E11 Survival**: individual i survives with

p_i = clip( 1 − mort_s·μ − (1 − suit_{s,j(i)})·0.24 − press_i·0.08
      − 1{infected}·0.14 + M_j·research_j·0.035 − W_j·pred_j·μ_pred·0.035
      − (1 − health_i)·0.08 − inbreeding_i·0.08 ; 0.05, 0.995 )

press_i = anthropogenic_j · anthro_sens_s · μ_anthro (μ = multipliers,
all 1.0 in base).

**E12 Reproduction** per (s, j < 8) with ≥1 female and ≥1 male of age ≥ 2:

rate = (mort_s + growth_s)·(0.5 + fert_s)·suit_{s,j}
     · max(0.05, 1 − dens_j) · 5.0
     · (1 + 0.22·spend_exsitu/B_t if managed)
     · max(0.05, 1 − local_infection·0.30)
     · max(0.05, 1 − mean_inbreeding·0.35)

births ~ Poisson(n_females·rate); dens_j = n_{s,j}/capacity_j.

**E13 Genetics**: if genetics spend > 0 and policy ≠ S0, fathers are
chosen preferring a different founder with weights ∝ clip(1 −
inbreeding, 0.05, ·); else uniform. Child inbreeding = (F_m + F_f)/2 +
0.08·1{same founder}, × 0.82 under diversity-aware mating; founder id
inherited from either parent with p = 0.5. Effective founders =
1/Σ f_k² over founder frequencies (per species, averaged).

**E14 Population cap**: new births fill dead slots then append, total
alive ≤ 1200.

**E15 Biobank**: b_s ×= 0.99 each year; if species extant and stage ≥ 2,
b_s += 0.05·(spend_biobank/B_t), clipped to [0, 1].

**E16 Extinction before discovery (EBD)**: a latent species (known =
false) extinct while stage < 2 is recorded with its extinction year.
Endpoint = last individual death before reaching stage 2 (detection-
based visibility), not formal taxonomic description — the manuscript
must phrase it as "extinction before modelled detection/recognition".

**E17 Welfare**: w_i = welfare_j − M_j·0.12·(1 − stress_tol_i) −
(predation W_j·pred_j·0.10 + food (1−suit)·0.18 + crowding
M_j·occ_j·0.12 + restriction M_j·mig_s·0.12 + infection 1{inf}·0.16 +
habituation_i·mig_s·0.10 + relocated_i·0.1·0.12). Both the mean
individual welfare and a welfare-person-year aggregate (Σ clip(w,0,1)
per year) are reported.

**E18 Engagement feedback**: exposure = mean visitor_exposure_j over
living individuals; habitat_signal = mean(q_{0..2});
engagement ← clip(engagement + 0.08·(exposure +
0.2·spend_engagement/B_t) + 0.02·habitat_signal; 0, 1.5);
B_{t+1} = 100·(0.82 + 0.24·engagement).

## Primary outcomes

survival_50/100 (fraction of the 8 species extant), species_retained,
total/wild abundance, n_ebd and fraction_ebd, lifetime/mean welfare,
founder_effective, mean_inbreeding, heterozygosity proxy,
successful_reintroductions (managed→wild moves), refuge_moves,
origin_returns, cost, available_budget, cost_per_species_retained,
engagement, habitat_integrity = mean(q_{0..2}), future_option_value =
0.45·survival + 0.25·min(founder_eff/25, 1) + 0.20·mean(biobank) +
0.10·mean(q_{0..2}), disease_prevalence, quarantine_cost,
relocation_burden, biobank_coverage, discovered_latent; per-burden
welfare decomposition.

## Experimental design (analysis.py)

- Paired seeds: each (replicate seed, process, year) instantiates its own
  generator via SeedSequence([seed, stream_id, year]); environmental
  draws (funding, catastrophe, observation, discovery, demography) are
  shared across policies at the same seed, but policy-dependent RNG
  consumption (movement, disease, demography downstream of different
  actions) means pairing is approximate, not exact common random
  numbers. The manuscript must say "paired seeds", not "common random
  streams".
- Production: 192 replicates/policy; S7 comparator 192 paired runs;
  nested convergence audit through 384.
- Sensitivity: Latin hypercube, 128 designs × 4 replicates, 12
  parameters (SENSITIVITY_RANGES); replicates averaged before Spearman
  and partial-rank interaction screening (descriptive, not causal).
- Five two-factor sweeps (5×5 grid × 8 paired reps) on S4/S6/S7; a cell
  direction is "robust" only if sign-stable from N=4 to N=8 and |mean| >
  1.96·MCSE.
- 9 ablations + 6 adverse-condition designs (S4/S6/S7, 12 reps).
- Pareto: 6 objectives {survival ↑, welfare ↑, genetics ↑, EBD ↓, cost ↓,
  future_option ↑} on policy means, tolerance 1e-12 (float equality, not
  an MC-uncertainty claim).
- Intervals are replicate percentiles; MC half-widths are simulation
  standard errors; neither is an empirical confidence interval.

## Known limitations to state in the manuscript

- All parameters are synthetic class C (no empirical calibration);
  units are model units. Mechanisms are qualitative, not taxon-specific
  effect sizes.
- S6's rescue allocation (3%) is spent but its movement engine never
  triggers (S6 never moves individuals); document as design detail.
- S2 sends every movable individual to the conventional-zoo node — a
  deliberate captivity-centric archetype, not an optimized strategy.
- Utility weights (E-utility in `config/analysis.json`) are illustrative
  normative choices used only for the comparator contrast, never for a
  winner declaration.
- The no-hindsight comparator contrast is an information effect, not
  EVPI.
