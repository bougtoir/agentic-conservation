# FINAL_MODEL_TRACEABILITY_AUDIT — PASS

Method: EQUATION_ALGORITHM_CODE_MATRIX.csv (31 mechanisms) cross-checked against
src/agentic_conservation/simulation.py, policies.py, species config; manuscript
Methods §2 read end-to-end for self-contained intelligibility.

- E1 suitability, E2 survival, E3 reproduction: inline equations in §2.3 match
  code functions _species_node_suitability / survival / reproduction terms.
- Algorithm 1 (14 steps, implemented order) and Algorithm 2 (action selection)
  are verbatim-faithful to simulation.step / policy rule code.
- All remaining matrix rows (quality dynamics, disease, discovery, welfare,
  engagement, biobank, EBD, budget) are narrated in §2.3–2.6 with exact
  constants (0.18 LogNormal sigma, 0.10 quality noise, 0.035 catastrophe,
  0.015 funding collapse, 0.72 cut, 1200 cap, stage gates, mate-limit 8).
- Psi equation = Word-native OMML (m:oMathPara present, 2 occurrences);
  no broken/placeholder math; zero markdown asterisks; no hard-wrap artifacts.
- Prohibited terms audit: no "oracle", no POMDP/EVPI/MCMC claim, no
  "universal law"/"general theorem". VERIFIED by grep over document.xml.
- No secrets, absolute private paths, or user identifiers in shipped code.
