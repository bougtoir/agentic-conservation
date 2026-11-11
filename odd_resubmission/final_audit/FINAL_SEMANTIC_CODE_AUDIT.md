# Final semantic code audit

Checked against `src/agentic_conservation/simulation.py`, `scripts/run_odd_verification.py`, `scripts/psi_confirmatory.py`.

| item | text | code | status |
|---|---|---|---|
| estimand S7−S6 | paired mean over seeds, SE = sd/√n | pivot by seed, S7−S6 | match |
| determinate | |mean| > 2 SE | same | match |
| regret | mean persistence forgone vs better observed policy | recomputed identically | match |
| Wilson | 95%, z = 1.96 | `wilson(k, n, z=1.96)` | match |
| climate forms | accelerating v·t/T; linear; decelerating mirrored; step at mid-run | `climate_increment` (step in year `first_year + years//2 − 1` = 50) | match |
| Q1 endpoints | individual / co-located mature pair in non-biobank node / wild node | observer outputs, no RNG draws | match |
| replication unit | paired seed per cell | `seed` column in all run CSVs | match |
| dev / held-out / prospective split | disjoint; prospective excludes earlier cells | designs.csv, freeze record | match |
| funding shock | one-year ×0.72, p = 0.015 | config | match |
| engagement | non-decreasing | increments ≥ 0 | match (disclosed) |
| release events | counted before release mortality | counter placement | match (disclosed) |
| Algorithm 1 order | 14 steps | step function order | match |
