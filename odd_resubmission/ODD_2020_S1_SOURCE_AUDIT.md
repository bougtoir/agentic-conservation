# ODD 2020 and Supplement S1 source audit

| Item | Verified value | How verified |
|---|---|---|
| Article | Grimm V, Railsback SF, Vincenot CE, Berger U, Gallagher C, DeAngelis DL, et al. (19 authors). The ODD protocol for describing agent-based and other simulation models: a second update to improve clarity, replication, and structural realism. *JASSS* 23(2):7, 2020 | Crossref record for doi:10.18564/jasss.4259; publisher HTML |
| DOI | 10.18564/jasss.4259 | Crossref |
| Official URL | https://www.jasss.org/23/2/7.html | HTTP 200 |
| Supplement S1 | https://www.jasss.org/23/2/7/S1-ODD.pdf (ODD template with guidance and checklists) | HTTP 200, read in full (2,753 extracted lines) |
| Other supplements | S0 (xlsx), S2-S7 (pdf) downloaded | HTTP 200 |
| Local copies | `data/raw/odd_2020_sources/` + `ACQUISITION_LEDGER.csv` (URL, UTC time, bytes, SHA-256) | sha256 recomputed after copy |
| Grimm et al. 2027 | "Twenty years of the ODD protocol ..." *Environ Model Softw* 207:107203, doi:10.1016/j.envsoft.2026.107203 (43 authors, CC BY 4.0) | Crossref |
| Accessibility limits | none for the article or S1. The Ecological Modelling guide for authors returns HTTP 403 to non-browser requests and is NOT VERIFIED yet. | |

## S1 guidance used for the crosswalk (paraphrased; official labels and order)

1. **Purpose and patterns**: state the specific purpose as a clear question and the general purpose type; define terms; make it independent of the Introduction; list the patterns used as criteria for whether the model is fit for purpose. For models of no specific system, the patterns can be general beliefs.
2. **Entities, state variables, and scales**: say what kinds of entities there are and why they are included (and why others are left out); give a state-variable table with units, ranges, and whether each variable is static or dynamic; describe temporal and spatial scales and justify them.
3. **Process overview and scheduling**: give the hierarchy of actions, which entities perform them, which state variables they update, and the execution order (synchronous or asynchronous); justify the order.
4. **Design concepts**: Basic principles, Emergence, Adaptation, Objectives, Learning, Prediction, Sensing, Interaction, Stochasticity, Collectives, Observation. Concepts that are not implemented should be stated as such (S1: e.g. "Learning is not implemented").
5. **Initialization**: initial entities and their values, how they vary among runs, and the rationale.
6. **Input data**: time-varying external drivers. If there are none, say so.
7. **Submodels**: one subsection per submodel, giving equations, parameter values and how they were chosen, the rationale, and any analysis of the submodel.

S1 asks for an ODD that is complete enough for replication without the code, and asks that the design rationale go especially in Design concepts and Submodels. This matches the Associate Editor's request as summarised in the user's instruction. The verbatim decision letter has not been provided, so this document quotes none of it.
