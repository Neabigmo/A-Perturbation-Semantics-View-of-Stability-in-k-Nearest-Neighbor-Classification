# DR-20260514 Paper Claims

## Decision

Core paper assertions are classified as follows.

## High-confidence main-text claims

1. Uniform replace-one can be bounded through delete-one plus add-one at the
   operation level for deterministic learners under bounded loss.
   Label: `Theorem` or `Proposition` after proof-note audit.

2. Deterministic k-NN prediction changes exactly when the signed top-k margin
   crosses the tie threshold induced by the fixed label order.
   Label: `Proposition`.

3. There exists a two-point graph-metric 1-NN example where fixed-sample LOO
   indicator is zero while fixed-sample replace-one indicator is one.
   Label: `Proposition` or `Example`, depending on final presentation.

## Claims that must remain downgraded

1. Minimality over graph size and search space.
   Label: `Computational Certificate`.

2. Odd-k gadget lifting from repeated occurrences.
   Label: `Conjecture` or `Computational Certificate` unless proved.

3. Broad novelty language such as "first" or "complete characterization of
   all perturbation phenomena".
   Label: forbidden until later external-check pass.

## Discussion-only claims

1. Finite worst-case separations do not contradict classical i.i.d.
   consistency of nearest-neighbor rules.
2. The paper's main contribution is a microscopic perturbation calculus rather
   than a new generalization bound.

## Writing Rule

No statement may be upgraded above its registry label without a corresponding
proof-note update and Codex review.
