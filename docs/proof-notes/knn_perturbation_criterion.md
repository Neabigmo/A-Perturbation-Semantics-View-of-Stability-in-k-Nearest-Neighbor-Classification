# Statement

For deterministic k-NN with lexicographic occurrence ordering and vote ties
favoring label `0`, the prediction at query point `x` changes exactly when the
signed top-k margin crosses the threshold at `0`.

# Definitions used

- finite metric space
- ordered sample
- deterministic neighbor ordering
- top-k neighborhood
- signed margin
- tie threshold induced by fixed label order

# Proof sketch

Let `M_k(S, x)` be the number of label-`1` occurrences among the top-k
neighbors minus the number of label-`0` occurrences among the same top-k set.
Since vote ties go to `0`, the deterministic rule predicts `1` exactly when
`M_k(S, x) > 0`. Therefore

`h_S^(k)(x) != h_{S'}^(k)(x)`

if and only if

`1{M_k(S,x) > 0} != 1{M_k(S',x) > 0}`.

The perturbation-specific behavior is then reduced to understanding how the
ordered top-k multiset and its label counts change under deletion, insertion,
or replacement.

# Full proof or gap

The base proposition is straightforward. The more useful specialized corollaries
still need crisp statements:

- outside-top-k deletion cannot change prediction unless the boundary ordering
  itself changes;
- an in-top-k replacement changes prediction only if the removed/added labels
  push the signed margin across `0`.

# Counterexample checks

- even `k` matters because the threshold at `0` interacts with label-tie
  resolution;
- duplicate occurrences at the same point still count separately in the margin.

# Risk

Low for the core equivalence; medium for the sharp perturbation corollaries.

# Paper placement

Main text: `05_knn_perturbation`
Appendix: `A_proofs`
