# Oracle and information-value audit

## Comparator definition

The comparator supplies the **true current state** within the same S7
action class. In each decision year it receives current true abundance and
current habitat quality. It does not receive future environmental shocks,
future demographic draws, or realized future outcomes. S7 remains a
forward-quality heuristic; it is not a solved POMDP.

The former analysis retained the feasible realization whenever the oracle
realization had lower post hoc utility. That was hindsight selection and forced
the reported contrast to be nonnegative. This behavior was removed. The
reported quantity is now the paired effect of current-state information under
the fixed S7 heuristic and may be positive or negative.

At N=384, the mean decision-utility effect was
0.0050 (Monte Carlo half-width
0.0065). It is not monetary EVPI and is not
used to declare an overall policy winner.

## Remaining limitation

True current-state information can change actions under a heuristic that was not
re-optimized for each information regime. The contrast therefore measures the
value or harm of feeding current truth into that heuristic, not the theoretical
EVPI of an optimal decision problem.
