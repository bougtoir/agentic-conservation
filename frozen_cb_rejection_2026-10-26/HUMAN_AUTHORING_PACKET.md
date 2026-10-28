# Human authoring packet

This is a factual, code-derived packet for accountable human authors. It is not
a manuscript and does not supply final scientific interpretation.

## Candidate title

Dynamic conservation networks under environmental change and hidden biodiversity

## Article type and limits

- *Conservation Biology* Contributed Paper.
- IMRAD organization.
- Maximum 7,000 words from Abstract through Acknowledgments under the live
  instructions verified 2026-09-24.
- Abstract no longer than 300 words; 5–8 keywords; impact statement no longer
  than 140 characters.
- Double-blind manuscript; identifying cover page separate. All former
  Supporting Information content is integrated in the main text.

## Central question

When do dynamic networks spanning wild and managed environments change
biodiversity, welfare, genetic, information, and cost outcomes relative to
fixed strategies, and when do those differences disappear or reverse?

## Candidate model hypotheses for human framing

These were not externally preregistered and must not be described as
confirmatory hypotheses.

1. No single policy will dominate every alternative across persistence,
   welfare, cost, EBD, genetics, and future-option value.
2. S7 will exceed habitat-first S6 when directional habitat change is strong
   and movement harm is limited, but the ordering will reverse under stable
   origins or costly movement.
3. Survey investment will reduce EBD only when latent taxa remain detectable
   before extinction and survey opportunity costs do not displace higher-value
   interventions.
4. True current-state information will have an aggregation-dependent effect
   under a fixed heuristic rather than a necessarily positive EVPI.

## Defensible contribution

The transferable contribution is a transparent simulation framework that
combines latent species, noisy delayed observations, individual heterogeneity,
wild and managed nodes, finite budgets, human feedback, disease, welfare,
genetics, biobanking, and explicit policy reversals. The study should be framed
as a conditional decision-analysis experiment, not an empirical demonstration
that one institutional arrangement is generally superior.

## Methods facts to convert into human prose

1. Eight synthetic species were followed for 100 annual steps across nine
   node types. Five species were initially known and three were hidden from
   feasible decision makers.
2. Individuals carried demographic, health, disease, behavioral, origin,
   founder, and inbreeding states.
3. Latent taxa advanced through detection, description, monitoring, threat
   recognition, and protection; extinction before description was retained as
   an explicit endpoint.
4. Eight policies (S0–S7) ranged from no intervention through fixed habitat or
   captivity rules to state-dependent circulation, global allocation, and a
   hybrid forward-quality proxy.
5. Policy outcomes used paired seed sets. The full run used
   192 replications per policy. Percentile
   intervals describe simulation distributions; Monte Carlo half-widths are
   reported separately.
6. Sensitivity used a Latin-hypercube design plus five prespecified two-factor
   sweeps. Nine feature ablations and six adverse-condition designs sought
   disappearance and reversal conditions.
7. A current-state-information S7 comparison supplied true current abundance
   and habitat quality to the same action class. It did not supply future
   environmental draws and was not optimized as a POMDP or monetary EVPI.
   Effects were evaluated against a declared weighted utility and component
   outcomes.
8. The empirical component saved GBIF taxonomy and occurrence-year aggregates
   plus bibliographic metadata and bounded literature evidence snapshots. It
   was not used to calibrate synthetic parameters.

Detailed methods are in `docs/model_specification.md` and
`docs/analysis_plan.md`. Figure 1 depicts the node network.
Table 1 lists base parameters and Table 2 lists policy
allocations.

## Code-derived result prompts

- The largest mean 100-year survival proportion in the current run was
  0.529 for S6; its replicate-distribution interval was
  [0.000, 0.875]. This ranking is descriptive and not a
  claim of general superiority.
- S7 survival was 0.473 [0.125, 0.750]; S6 survival was
  0.529 [0.000, 0.875]; state-dependent S4 survival was
  0.378 [0.125, 0.625].
- S7 mean individual welfare was
  0.617 [0.441, 0.742], while S2 lifetime
  captivity was 0.477 [0.369, 0.514].
- S7 extinction-before-discovery fraction was
  0.227 [0.000, 0.667]; S5 was
  0.311 [0.000, 1.000].
- The paired current-state-information effect on the prespecified utility
  scale was -0.003
  [-0.112, 0.131].
- Robust two-factor sweep contrasts favored S7 in 35 cells
  and S6 in 26; 64 cells were indeterminate because
  their sign changed from N=4 to N=8 or their absolute mean did not exceed
  1.96 Monte Carlo standard errors. The existence of opposite-direction
  regions, not the raw cell tally, is the supported result.

All figures and tables are in the main text and numbered by first citation.
Figure 2 provides the multiobjective Pareto comparison,
Figure 3 100-year trajectories, Figure 4 EBD sensitivity,
Figure 5 cross-objective trade-offs, Figure 6 the
observation architecture, Figure 7 the policy-reversal surfaces,
Figure 8 exploration–exploitation patterns, and
Figure 9 the origin-to-future optimum shift.
Table 3 and Table 4 provide sensitivity and
interaction screens, Table 5 and Table 6 empirical-source
summaries, Table 7 policy estimates, Table 8
robustness summaries, and Table 9 information-weight
summaries.

## Robust, fragile, and alternative interpretations

- Robust implementation-level findings: policy rankings reverse across
  prespecified conditions; welfare, persistence, EBD, genetics, cost, and
  future-option value are noninterchangeable; and the six-objective Pareto
  analysis yields a broad nondominated set rather than a unique winner.
- Monte Carlo convergence: all registered S6, S7, and S7-S6 endpoint estimates
  at N=192 were within two N=192 Monte Carlo standard errors of N=384; the
  largest observed ratio was 1.58. Current-state
  information effects also met the criterion. Production therefore remains
  N=192, with N=384 retained only as an audit.
- Population-cap robustness: doubling the synthetic cap from 1200 to 2400
  changed the paired S7-S6 survival contrast by
  0.0000. Total abundance is cap-sensitive
  and is not used for the primary policy conclusions.
- Assumption-dependent findings: the base S6–S7 ordering, sweep-cell counts,
  S3 collapse under directional change, and the sign or magnitude of the
  aggregated information effect.
- Negative findings: current-state information did not produce a detectable
  positive utility effect under the fixed S7 heuristic; S7 did not exceed S6
  in the base production scenario; and the analysis does not identify a
  universally preferred institutional form.
- Alternative interpretations: reversals may reflect unavoidable ecological
  trade-offs, limitations of the policy heuristics, or arbitrary synthetic
  parameter regions. The experiment cannot distinguish those explanations
  empirically.
- Information-weight diagnostics:

- registered: -0.003 [-0.112, 0.131]
- equal_components: -0.002 [-0.110, 0.125]
- persistence_priority: -0.006 [-0.162, 0.169]
- welfare_priority: -0.000 [-0.063, 0.076]
- future_option_priority: -0.001 [-0.095, 0.117]
- ebd_priority: 0.001 [-0.221, 0.223]

## Empirical observation-coverage facts

- Przewalski's horse: 785 coordinate-bearing present records in the saved aggregate query; 663 were dated 2015–2025.
- Scimitar-horned oryx: 227 coordinate-bearing present records in the saved aggregate query; 125 were dated 2015–2025.
- California condor: 33,646 coordinate-bearing present records in the saved aggregate query; 25,910 were dated 2015–2025.

These counts are affected by observation effort, digitization, data publishing,
taxonomy, and the query date. They are not abundance, occupancy, population
trend, or intervention-effect estimates.

## Full-text-verified literature evidence

40 sources are cited. Complete article text was appraised for 4; 31 are cited only for statements in retained author abstracts or titles; and 5 are cited only for title-bounded background after exact-DOI Crossref verification. 5 former candidates without verified text are marked NOT_VERIFIED, excluded from the bibliography, and not used for substantive claims. Bounded uses by source:

- Kaczensky et al. (2007), DOI 10.22353/mjbs.2007.05.03: A Przewalski's horse reintroduction developed from captive-born release toward standardized monitoring and broader ecosystem work. Evidence level: FULL_TEXT_LOCAL; location: Abstract; Introduction; Monitoring; Conclusion. Boundary: Keep the claim bounded to this documented project.
- D’Elia et al. (2015), DOI 10.1016/j.biocon.2015.01.002: Activity-specific niche models evaluated with withheld data can inform condor reintroduction screening, but site selection still requires ground reconnaissance and unmodeled-threat assessment. Evidence level: FULL_TEXT_LOCAL; location: Abstract; Methods; Results; Discussion. Boundary: Do not treat modeled suitability as site validation.
- Mee et al. (2007), DOI 10.1017/s095927090700069x: Anthropogenic material ingestion contributed to nestling mortality and low nest success in a reintroduced southern California condor population. Evidence level: FULL_TEXT_LOCAL; location: Summary; Methods; Results; Discussion. Boundary: Keep the claim population- and period-specific.
- Williams & Brown (2022), DOI 10.1002/ece3.9197: Ecological decisions under partial observability distinguish hidden states from observations and track belief states, with substantial computational and interpretive costs. Evidence level: FULL_TEXT_LOCAL; location: Introduction; Process specification; Discussion. Boundary: Do not imply that the present heuristic simulation solves a POMDP.
- Conde et al. (2011), DOI 10.1126/science.1200674: About one in seven threatened terrestrial vertebrate species is held in captivity. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Conde et al. (2013), DOI 10.1371/journal.pone.0080311: Threatened species are unevenly represented in the zoo network and managing zoo metapopulations requires coordination among many institutions. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Pritchard et al. (2012), DOI 10.1017/S0030605310001766: Ex situ conservation has been argued to deserve a larger and more integrated role alongside dominant in situ approaches. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Redford et al. (2012), DOI 10.1126/science.1228899: Conservation management increasingly integrates zoo-derived and wild management approaches. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Seddon et al. (2014), DOI 10.1126/science.1251818: Conservation translocations span reinforcement and reintroduction to conservation introductions outside the indigenous range. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Gilbert et al. (2017), DOI 10.1111/izy.12159: Zoos and aquariums can provide source populations for reintroductions but do not necessarily hold globally rare species. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Snyder et al. (1996), DOI 10.1046/j.1523-1739.1996.10020338.x: Captive breeding has documented limitations including reintroduction failure; cost; domestication; disease; and preemption of other recovery techniques. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Frankham (2008), DOI 10.1111/j.1365-294X.2007.03399.x: Genetic adaptation to captivity is generally deleterious when populations are returned to the wild. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Araki et al. (2007), DOI 10.1126/science.1145621: In steelhead trout captive rearing reduced subsequent reproductive success in the wild by about 40% per captive-reared generation. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Williams & Hoffman (2009), DOI 10.1016/j.biocon.2009.05.034: Approaches for minimizing genetic adaptation in captive breeding programs have been reviewed. Evidence level: METADATA_ONLY; location: Verified title. Boundary: Background citation only; do not strengthen beyond the article title.
- Hoban et al. (2020), DOI 10.1016/j.biocon.2020.108654: Genetic-diversity targets and indicators were undeveloped in earlier global biodiversity strategies. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Jule et al. (2008), DOI 10.1016/j.biocon.2007.11.007: Captive experience has been analyzed as a determinant of reintroduction survival in carnivores. Evidence level: METADATA_ONLY; location: Verified title. Boundary: Background citation only; do not strengthen beyond the article title.
- Dickens et al. (2010), DOI 10.1016/j.biocon.2010.02.032: Stress is an inherent component of animal translocation. Evidence level: METADATA_ONLY; location: Verified title. Boundary: Background citation only; do not strengthen beyond the article title.
- Kock et al. (2010), DOI 10.20506/rst.29.2.1980: Translocation of wildlife carries disease risks. Evidence level: ABSTRACT_LOCAL; location: Verified title. Boundary: Background citation only; do not strengthen beyond the article title.
- Harrington et al. (2013), DOI 10.1111/cobi.12021: Potential welfare issues were recorded in most reviewed reintroduction projects whereas welfare was rarely addressed explicitly. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Beausoleil et al. (2018), DOI 10.3389/fvets.2018.00296: Conservation welfare argues that welfare harms to individuals can also hamper conservation goals. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Mellor et al. (2020), DOI 10.3390/ani10101870: The Five Domains Model assesses welfare through nutrition; physical environment; health; behavioural interactions; and mental state. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Hoegh-Guldberg et al. (2008), DOI 10.1126/science.1157897: Moving species outside historic ranges has been proposed to mitigate biodiversity loss under climate change. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- McLachlan et al. (2007), DOI 10.1111/j.1523-1739.2007.00676.x: Assisted migration under climate change requires an explicit framework for debate. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Richardson et al. (2009), DOI 10.1073/pnas.0902327106: Managed relocation involves interacting value-laden considerations and decisions under imperfect information. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Thomas (2011), DOI 10.1016/j.tree.2011.02.006: Climate-driven translocation challenges the goal of recreating past ecological communities. Evidence level: METADATA_ONLY; location: Verified title. Boundary: Background citation only; do not strengthen beyond the article title.
- Mora et al. (2011), DOI 10.1371/journal.pbio.1001127: Most eukaryotic species may remain undescribed. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Costello et al. (2013), DOI 10.1126/science.1230318: Estimates of species richness and of extinction before description are contested. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Tedesco et al. (2014), DOI 10.1111/cobi.12285: Undescribed extinct species may form a substantial share of recent extinctions. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Boehm & Cronk (2021), DOI 10.1098/rsbl.2021.0007: Dark extinction denotes extinction of species before they are discovered and named. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Liu et al. (2022), DOI 10.1111/conl.12876: More recently described vertebrate species are more often threatened; implying elevated risk for undescribed species. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Chadès et al. (2008), DOI 10.1073/pnas.0805265105: Managing for a cryptic threatened species can be optimal even when its presence is uncertain; and management versus survey is a partially observable decision. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Chadès et al. (2021), DOI 10.1111/2041-210X.13692: Partially observable Markov decision processes formalize trade-offs between management and surveillance under imperfect observation. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Canessa et al. (2015), DOI 10.1111/2041-210X.12423: Value-of-information analysis asks whether reducing uncertainty would change a management decision. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- McCarthy & Possingham (2007), DOI 10.1111/j.1523-1739.2007.00677.x: Active adaptive management balances management performance against learning. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Joseph et al. (2009), DOI 10.1111/j.1523-1739.2008.01124.x: Resource allocation among threatened species should account for management cost and probability of success. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Kennedy et al. (2008), DOI 10.1111/j.1365-2664.2007.01367.x: Pareto non-dominance displays trade-offs among conflicting objectives without weighting them into a single value. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Howell et al. (2021), DOI 10.1111/conl.12776: Integrating biobanked sperm into captive breeding reduced inbreeding and programme cost in a modeled amphibian system. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Bolton et al. (2022), DOI 10.1530/RAF-22-0005: Cryobanking with assisted reproductive technologies can reinstate lost genetic diversity. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Moss et al. (2015), DOI 10.1111/cobi.12383: Biodiversity understanding increased over zoo and aquarium visits in a multinational visitor study. Evidence level: ABSTRACT_LOCAL; location: Author abstract. Boundary: Background citation only; do not strengthen beyond the abstract.
- Watson et al. (2014), DOI 10.1038/nature13947: The performance of protected areas depends on recognition; funding; planning; and enforcement. Evidence level: METADATA_ONLY; location: Verified title. Boundary: Background citation only; do not strengthen beyond the article title.

Former candidates that remain auditable but are not cited:

- Van Dierendonck & Wallis de Vries (1996), DOI 10.1046/j.1523-1739.1996.10030728.x: NOT_VERIFIED and excluded from substantive manuscript use.
- Xia et al. (2014), DOI 10.1016/j.biocon.2014.06.021: NOT_VERIFIED and excluded from substantive manuscript use.
- Ogden et al. (2020), DOI 10.1016/j.biocon.2019.108244: NOT_VERIFIED and excluded from substantive manuscript use.
- Moore & Runge (2012), DOI 10.1111/j.1523-1739.2012.01907.x: NOT_VERIFIED and excluded from substantive manuscript use.
- Memarzadeh & Boettiger (2018), DOI 10.1016/j.biocon.2018.05.009: NOT_VERIFIED and excluded from substantive manuscript use.

Cited sources support only the bounded statements above at their recorded
evidence levels; they do not calibrate model parameters or validate simulated
policy effects. Abstract- and metadata-level sources must not be strengthened
without full-text review.

## Parameter provenance

- Registry entries: 347.
- Classification counts: C=347.
- All registered model, species, node, and policy-allocation values are
  deliberately synthetic or illustrative (class C); none is presented as an
  empirical estimate, and no class-D entry remains.
- The registry records value, range or distribution, unit, rationale,
  sensitivity or robustness coverage, manuscript location, and action for
  every entry.
- The `max_individuals` computational cap is class C and covered by the
  twofold population-cap audit. This audit supports endpoint robustness but
  not interpretation of capped total abundance.

## S0 benign-control conclusion

The directional-change S0 design retained
0.000
species on average at year 100. Removing directional deterioration and climate
velocity while retaining ordinary catastrophe risk, predation, anthropogenic
pressure, and demographic stochasticity retained
1.792
species with survival
0.224.
The stable excellent-origin and combined benign controls retained
6.875
and 7.250
species, respectively. Zero-intervention extinction is therefore specific to
the configured directional-change scenario, not structurally required.

## Pareto conclusion

The reproducible analysis maximizes persistence, welfare, genetics, and future
option value and minimizes EBD and cost. Dominance uses an absolute numerical
tolerance of 1e-12 and no weighted overall score. Nondominated policies are
S0, S1, S3, S4, S6, S7; dominated policies are S2, S5. Table 7 and
`results/manuscript_values.csv` are checked against the same production means
and Pareto flags.

## Current AI-policy boundary

The live Wiley ethics guidance checked on 2026-09-25 permits AI only as an
additional tool, not a replacement for accountable human expertise and
judgment. Authors must document and disclose substantial AI use, including its
purpose, influence on arguments or conclusions, and personal review and
verification. AI cannot be an author. Human authors must ensure the final work
reflects their own expertise, voice, originality, and scientific decisions,
and must verify provider rights, privacy, and confidentiality terms.

## Exact passages requiring human scientific judgment

1. **HUMAN AUTHOR REQUIRED:** Results passage beginning “Supplying true current
   state to the same S7 action class” — decide whether the near-zero,
   weight-dependent negative result merits main-text emphasis.
2. **HUMAN AUTHOR REQUIRED:** Discussion passage beginning “The central result
   was conditionality rather than dominance” — determine the final novelty,
   conservation relevance, and alternative scientific interpretation.
3. **HUMAN AUTHOR REQUIRED:** Discussion passage beginning “The results do not
   identify a universal best institutional form” — approve the boundary
   between model proposition and applied recommendation.
4. **HUMAN AUTHOR REQUIRED:** Acknowledgments and AI-use disclosure — provide
   accurate tool, purpose, human-verification, funding, conflict, and
   contribution statements under the live journal policy.

## Discussion boundaries

- Explain why movement can help when origin quality deteriorates or future
  suitability shifts, but can harm through mortality, stress, pathogens, and
  maladaptation.
- Separate persistence in managed care from restoration of free-living
  populations.
- Treat welfare, genetics, habitat integrity, EBD, and cost as separate
  objectives; do not collapse them into a moral ranking.
- Explain why additional information has value only relative to a decision
  rule and normative utility.
- Discuss hidden biodiversity as a resource-allocation problem without
  asserting that the synthetic EBD rate predicts real global loss.
- State that fixed policy allocations, simplified genetics, aggregate
  biobanking, and noncalibrated synthetic species limit external validity.
- Present reversal surfaces and adverse conditions prominently. A conclusion
  that ignores them would overstate the evidence.

## Exact remaining human actions before submission

1. **HUMAN AUTHOR REQUIRED:** inspect the cited passages and approve every
   bounded literature claim at its recorded evidence level; read full text
   before strengthening any abstract- or metadata-level citation.
2. **HUMAN AUTHOR REQUIRED:** decide whether the synthetic parameterization,
   policy archetypes, utility weights, and interpretation are scientifically
   defensible; do not convert class-C values into empirical claims.
3. **HUMAN AUTHOR REQUIRED:** write or substantively revise the final manuscript
   in the authors' own scientific voice and approve every claim, citation,
   figure, table, and limitation.
4. **HUMAN AUTHOR REQUIRED:** supply authors, affiliations, contributions,
   funding, conflicts, acknowledgments, and the accurate AI-use disclosure on
   the nonanonymous cover material.
5. **HUMAN AUTHOR REQUIRED:** recheck live Conservation Biology and ScholarOne
   requirements on the submission date and arrange durable anonymous
   code/data review access if requested.

## References for human approval

Araki H, Cooper B, Blouin MS. 2007. Genetic Effects of Captive Breeding Cause a Rapid, Cumulative Fitness Decline in the Wild. *Science*. https://doi.org/10.1126/science.1145621 (ABSTRACT_LOCAL)
Beausoleil NJ, Mellor DJ, Baker L, Baker SE, Bellio M, Clarke AS, Dale A, Garlick S, Jones B, Harvey A, Pitcher BJ, Sherwen S, Stockin KA, Zito S. 2018. “Feelings and Fitness” Not “Feelings or Fitness”–The Raison d'être of Conservation Welfare, Which Aligns Conservation and Animal Welfare Objectives. *Frontiers in Veterinary Science*. https://doi.org/10.3389/fvets.2018.00296 (ABSTRACT_LOCAL)
Boehm MMA, Cronk QCB. 2021. Dark extinction: the problem of unknown historical extinctions. *Biology Letters*. https://doi.org/10.1098/rsbl.2021.0007 (ABSTRACT_LOCAL)
Bolton RL, Mooney A, Pettit MT, Bolton AE, Morgan L, Drake GJ, Appeltant R, Walker SL, Gillis JD, Hvilsom C. 2022. Resurrecting biodiversity: advanced assisted reproductive technologies and biobanking. *Reproduction and Fertility*. https://doi.org/10.1530/RAF-22-0005 (ABSTRACT_LOCAL)
Canessa S, Guillera-Arroita G, Lahoz-Monfort JJ, Southwell DM, Armstrong DP, Chadès I, Lacy RC, Converse SJ. 2015. When do we need more data? A primer on calculating the value of information for applied ecologists. *Methods in Ecology and Evolution*. https://doi.org/10.1111/2041-210X.12423 (ABSTRACT_LOCAL)
Chadès I, McDonald-Madden E, McCarthy MA, Wintle B, Linkie M, Possingham HP. 2008. When to stop managing or surveying cryptic threatened species. *Proceedings of the National Academy of Sciences*. https://doi.org/10.1073/pnas.0805265105 (ABSTRACT_LOCAL)
Chadès I, Pascal LV, Nicol S, Fletcher CS, Ferrer-Mestres J. 2021. A primer on partially observable Markov decision processes (POMDPs). *Methods in Ecology and Evolution*. https://doi.org/10.1111/2041-210X.13692 (ABSTRACT_LOCAL)
Conde DA, Colchero F, Gusset M, Pearce-Kelly P, Byers O, Flesness N, Browne RK, Jones OR. 2013. Zoos through the Lens of the IUCN Red List: A Global Metapopulation Approach to Support Conservation Breeding Programs. *PLoS ONE*. https://doi.org/10.1371/journal.pone.0080311 (ABSTRACT_LOCAL)
Conde DA, Flesness N, Colchero F, Jones OR, Scheuerlein A. 2011. An Emerging Role of Zoos to Conserve Biodiversity. *Science*. https://doi.org/10.1126/science.1200674 (ABSTRACT_LOCAL)
Costello MJ, May RM, Stork NE. 2013. Can We Name Earth's Species Before They Go Extinct?. *Science*. https://doi.org/10.1126/science.1230318 (ABSTRACT_LOCAL)
Dickens MJ, Delehanty DJ, Romero LM. 2010. Stress: An inevitable component of animal translocation. *Biological Conservation*. https://doi.org/10.1016/j.biocon.2010.02.032 (METADATA_ONLY)
D’Elia J, Haig SM, Johnson M, Marcot BG, Young R. 2015. Activity-specific ecological niche models for planning reintroductions of California condors ( Gymnogyps californianus ). *Biological Conservation*. https://doi.org/10.1016/j.biocon.2015.01.002 (FULL_TEXT_LOCAL)
Frankham R. 2008. Genetic adaptation to captivity in species conservation programs. *Molecular Ecology*. https://doi.org/10.1111/j.1365-294X.2007.03399.x (ABSTRACT_LOCAL)
Gilbert T, Gardner R, Kraaijeveld AR, Riordan P. 2017. Contributions of zoos and aquariums to reintroductions: historical reintroduction efforts in the context of changing conservation perspectives. *International Zoo Yearbook*. https://doi.org/10.1111/izy.12159 (ABSTRACT_LOCAL)
Harrington LA, Moehrenschlager A, Gelling M, Atkinson RPD, Hughes J, Macdonald DW. 2013. Conflicting and Complementary Ethics of Animal Welfare Considerations in Reintroductions. *Conservation Biology*. https://doi.org/10.1111/cobi.12021 (ABSTRACT_LOCAL)
Hoban S, Bruford M, D'Urban Jackson J, Lopes-Fernandes M, Heuertz M, Hohenlohe PA, Paz-Vinas I, Sjögren-Gulve P, Segelbacher G, Vernesi C, Aitken S, Bertola LD, Bloomer P, Breed M, Rodríguez-Correa H, Funk WC, Grueber CE, Hunter ME, Jaffe R, Liggins L, Mergeay J, Moharrek F, O'Brien D, Ogden R, Palma-Silva C, Pierson J, Ramakrishnan U, Simo-Droissart M, Tani N, Waits L, Laikre L. 2020. Genetic diversity targets and indicators in the CBD post-2020 Global Biodiversity Framework must be improved. *Biological Conservation*. https://doi.org/10.1016/j.biocon.2020.108654 (ABSTRACT_LOCAL)
Hoegh-Guldberg O, Hughes L, McIntyre S, Lindenmayer DB, Parmesan C, Possingham HP, Thomas CD. 2008. Assisted Colonization and Rapid Climate Change. *Science*. https://doi.org/10.1126/science.1157897 (ABSTRACT_LOCAL)
Howell LG, Frankham R, Rodger JC, Witt RR, Clulow S, Upton RMO, Clulow J. 2021. Integrating biobanking minimises inbreeding and produces significant cost benefits for a threatened frog captive breeding programme. *Conservation Letters*. https://doi.org/10.1111/conl.12776 (ABSTRACT_LOCAL)
Joseph LN, Maloney RF, Possingham HP. 2009. Optimal Allocation of Resources among Threatened Species: a Project Prioritization Protocol. *Conservation Biology*. https://doi.org/10.1111/j.1523-1739.2008.01124.x (ABSTRACT_LOCAL)
Jule KR, Leaver LA, Lea SEG. 2008. The effects of captive experience on reintroduction survival in carnivores: A review and analysis. *Biological Conservation*. https://doi.org/10.1016/j.biocon.2007.11.007 (METADATA_ONLY)
Kaczensky P, Ganbaatar O, von Wehrden H, Enksaikhan N, Lkhagvasuren D, Walzer C. 2007. Przewalski’s Horse (Equus ferus przewalskii) Re-introduction in the Great Gobi B Strictly Protected Area: from Species to Ecosystem Conservation. *Mongolian Journal of Biological Sciences*. https://doi.org/10.22353/mjbs.2007.05.03 (FULL_TEXT_LOCAL)
Kennedy MC, Ford ED, Singleton P, Finney M, Agee JK. 2008. Informed multi-objective decision-making in environmental management using Pareto optimality. *Journal of Applied Ecology*. https://doi.org/10.1111/j.1365-2664.2007.01367.x (ABSTRACT_LOCAL)
Kock RA, Woodford MH, Rossiter PB. 2010. Disease risks associated with the translocation of wildlife. *Revue Scientifique et Technique de l'OIE*. https://doi.org/10.20506/rst.29.2.1980 (ABSTRACT_LOCAL)
Liu J, Slik F, Zheng S, Lindenmayer DB. 2022. Undescribed species have higher extinction risk than known species. *Conservation Letters*. https://doi.org/10.1111/conl.12876 (ABSTRACT_LOCAL)
McCarthy MA, Possingham HP. 2007. Active Adaptive Management for Conservation. *Conservation Biology*. https://doi.org/10.1111/j.1523-1739.2007.00677.x (ABSTRACT_LOCAL)
McLachlan JS, Hellmann JJ, Schwartz MW. 2007. A Framework for Debate of Assisted Migration in an Era of Climate Change. *Conservation Biology*. https://doi.org/10.1111/j.1523-1739.2007.00676.x (ABSTRACT_LOCAL)
Mee A, Rideout BA, Hamber JA, Todd JN, Austin G, Clark M, Wallace MP. 2007. Junk ingestion and nestling mortality in a reintroduced population of California Condors Gymnogyps californianus. *Bird Conservation International*. https://doi.org/10.1017/s095927090700069x (FULL_TEXT_LOCAL)
Mellor DJ, Beausoleil NJ, Littlewood KE, McLean AN, McGreevy PD, Jones B, Wilkins C. 2020. The 2020 Five Domains Model: Including Human–Animal Interactions in Assessments of Animal Welfare. *Animals*. https://doi.org/10.3390/ani10101870 (ABSTRACT_LOCAL)
Mora C, Tittensor DP, Adl S, Simpson AGB, Worm B. 2011. How Many Species Are There on Earth and in the Ocean?. *PLoS Biology*. https://doi.org/10.1371/journal.pbio.1001127 (ABSTRACT_LOCAL)
Moss A, Jensen E, Gusset M. 2015. Evaluating the contribution of zoos and aquariums to Aichi Biodiversity Target 1. *Conservation Biology*. https://doi.org/10.1111/cobi.12383 (ABSTRACT_LOCAL)
Pritchard DJ, Fa JE, Oldfield S, Harrop SR. 2012. Bring the captive closer to the wild: redefining the role of ex situ conservation. *Oryx*. https://doi.org/10.1017/S0030605310001766 (ABSTRACT_LOCAL)
Redford KH, Jensen DB, Breheny JJ. 2012. Integrating the Captive and the Wild. *Science*. https://doi.org/10.1126/science.1228899 (ABSTRACT_LOCAL)
Richardson DM, Hellmann JJ, McLachlan JS, Sax DF, Schwartz MW, Gonzalez P, Brennan EJ, Camacho A, Root TL, Sala OE, Schneider SH, Ashe DM, Clark JR, Early R, Etterson JR, Fielder ED, Gill JL, Minteer BA, Polasky S, Safford HD, Thompson AR, Vellend M. 2009. Multidimensional evaluation of managed relocation. *Proceedings of the National Academy of Sciences*. https://doi.org/10.1073/pnas.0902327106 (ABSTRACT_LOCAL)
Seddon PJ, Griffiths CJ, Soorae PS, Armstrong DP. 2014. Reversing defaunation: Restoring species in a changing world. *Science*. https://doi.org/10.1126/science.1251818 (ABSTRACT_LOCAL)
Snyder NFR, Derrickson SR, Beissinger SR, Wiley JW, Smith TB, Toone WD, Miller B. 1996. Limitations of Captive Breeding in Endangered Species Recovery. *Conservation Biology*. https://doi.org/10.1046/j.1523-1739.1996.10020338.x (ABSTRACT_LOCAL)
Tedesco PA, Bigorne R, Bogan AE, Giam X, Jézéquel C, Hugueny B. 2014. Estimating How Many Undescribed Species Have Gone Extinct. *Conservation Biology*. https://doi.org/10.1111/cobi.12285 (ABSTRACT_LOCAL)
Thomas CD. 2011. Translocation of species, climate change, and the end of trying to recreate past ecological communities. *Trends in Ecology & Evolution*. https://doi.org/10.1016/j.tree.2011.02.006 (METADATA_ONLY)
Watson JEM, Dudley N, Segan DB, Hockings M. 2014. The performance and potential of protected areas. *Nature*. https://doi.org/10.1038/nature13947 (METADATA_ONLY)
Williams BK, Brown ED. 2022. Partial observability and management of ecological systems. *Ecology and Evolution*. https://doi.org/10.1002/ece3.9197 (FULL_TEXT_LOCAL)
Williams SE, Hoffman EA. 2009. Minimizing genetic adaptation in captive breeding programs: A review. *Biological Conservation*. https://doi.org/10.1016/j.biocon.2009.05.034 (METADATA_ONLY)
