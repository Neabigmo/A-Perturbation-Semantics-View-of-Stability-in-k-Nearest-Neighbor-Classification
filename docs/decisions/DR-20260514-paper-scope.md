# DR-20260514 Paper Scope

## Status

Accepted for the next drafting phase.

## Decision

The paper will be written as a finite-sample, deterministic, definition-driven
study of one-sample perturbations for local learning rules, with deterministic
k-nearest neighbors as the main worked example.

The main scope is:

1. Definition hygiene for delete-one, add-one, replace-one, and LOO.
2. Uniform perturbation relations for deterministic learners under bounded loss.
3. Exact deterministic k-NN perturbation analysis via ordered top-k margins.
4. Explicit finite-metric separations, especially the 1-NN LOO vs replace-one
   witness.
5. Reproducible computational certificates and visualizations.
6. A compatibility discussion with classical asymptotic consistency results.

## In Scope

- Ordered samples with duplicate occurrences allowed.
- Conflicting labels at the same metric point.
- Finite metric spaces and graph shortest-path metrics.
- Deterministic tie-breaking by distance, then sample index, with vote ties
  favoring label `0`.
- Binary 0-1 loss.
- Worst-case finite-sample statements and computational certificates.

## Out Of Scope For Current Draft

- Multiclass labels.
- Random tie-breaking.
- Learned metric spaces.
- Approximate nearest-neighbor data structures.
- High-dimensional asymptotic risk analysis beyond a compatibility discussion.
- Any "first-ever" novelty claim before external literature review deepening.

## Why

This scope is strong enough to support a serious paper while narrow enough to
keep mathematical boundaries honest. The repository already contains witness
search, tie-free filtering, minimality certification, and deterministic k-NN
infrastructure that support this scope directly.
