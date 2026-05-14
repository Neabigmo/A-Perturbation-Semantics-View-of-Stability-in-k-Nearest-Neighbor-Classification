# Statement

There exists a two-point graph metric witness for deterministic 1-NN in which
the maximum LOO indicator is `0` while the maximum replace-one indicator is `1`.

# Definitions used

- two-vertex graph metric with one edge
- ordered sample
- deterministic 1-NN
- LOO indicator
- replace-one indicator
- binary 0-1 loss

# Proof sketch

Use graph vertices `a` and `b` with one undirected edge. Consider the ordered
sample `((a,0),(b,0))`.

For LOO:

- deleting `(a,0)` leaves the sample `((b,0))`;
- evaluating at the deleted occurrence `a` still predicts `0`, so the loss at
  `(a,0)` does not change;
- the same holds symmetrically for deleting `(b,0)`.

Hence the fixed-sample maximum LOO indicator is `0`.

For replace-one:

- replace the first occurrence `(a,0)` by `(a,1)`;
- evaluate at query point `a` with evaluation label `0`;
- the original sample predicts `0`;
- the replaced sample predicts `1`;
- the 0-1 loss changes by `1`.

Hence the fixed-sample maximum replace-one indicator is `1`.

# Full proof or gap

The witness is hand-checkable and should be written explicitly in the paper.
No code is required to justify the existence claim once the above calculation is
spelled out.

# Counterexample checks

- duplicate/conflicting labels are allowed by the frozen definitions, so the
  replacement `(a,1)` is legal;
- the argument uses the paper's explicit LOO evaluation convention at the
  deleted occurrence itself.

# Risk

Low.

# Paper placement

Main text: `06_1nn_separation`
Appendix: `A_proofs`
