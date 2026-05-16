# Project Map

This repository is paper-first. The center of gravity is `main.pdf`, and every
other directory exists to support, verify, reproduce, or archive it.

## Canonical Flow

`paper/main.tex` -> `paper/sections/*.tex` + `paper/refs.bib` -> `main.pdf`

Supporting layers:

- `src/knn_stability/`: implementation of the deterministic k-NN / stability
  machinery used in the paper
- `experiments/`: witness search, certification, figure generation, and
  tabular reporting
- `outputs/`: generated artifacts that feed the paper or document the run
- `build/`: transient LaTeX intermediate files and local build cache
- `tests/`: regression coverage for the core stability code
- `archive/`: legacy drafts, old notes, historical build products, and other
  retired material

## What To Open First

1. `main.pdf`
2. `README.md`
3. `paper/main.tex`
4. `outputs/REPRODUCIBILITY.md`
5. `archive/README.md`

## Draft vs Canonical

- Canonical paper source: `paper/main.tex` and `paper/sections/`
- Alternate draft lane: `archive/drafts/`
- Generated LaTeX build products: stored under `archive/build/` when retained

## Recommended Editing Order

1. Update paper prose in `paper/sections/`
2. Update code in `src/knn_stability/` only if the paper claim depends on it
3. Regenerate the needed outputs in `experiments/`
4. Rebuild `main.pdf`
5. Check the PDF before touching any downstream summary tables

## Current Reading Guide

- The abstract and introduction explain the semantic gap between leave-one-out
  and replacement robustness.
- The perturbation calculus and margin criterion live in the middle sections.
- The witness constructions and empirical support live later in the paper.
- Appendix sections collect proofs, protocols, and extra figures.
