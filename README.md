# k-NN Stability Calculus

Primary artifact: [`main.pdf`](./main.pdf)

This repository is organized around a single paper-centered workflow:

1. Read `main.pdf` first.
2. Trace claims back to `paper/main.tex` and `paper/sections/`.
3. Use `src/knn_stability/` for the deterministic k-NN and stability logic.
4. Use `experiments/` to regenerate witnesses, figures, and tables.
5. Treat `outputs/` as generated artifacts that support the paper.
6. Use `archive/` for legacy drafts, historical notes, and backed-up build
   artifacts.

The paper studies deterministic finite-sample perturbation notions for local
learning rules, with k-nearest neighbors as the main example. The central
claim is that leave-one-out stability is not a certificate of
replace-one robustness.

## Project Map

- `main.pdf`: canonical reading copy of the paper
- `paper/main.tex`: canonical LaTeX entrypoint that builds the paper
- `paper/sections/`: canonical section sources for the current paper draft
- `src/knn_stability/`: core deterministic k-NN and stability code
- `experiments/`: scripts for witnesses, certificates, figures, and tables
- `outputs/`: generated witnesses, figures, tables, and reproducibility notes
- `build/`: transient build cache and LaTeX intermediate files
- `tests/`: regression tests for the core library and stability claims
- `archive/`: backup area for old versions, draft lanes, and retired notes

Legacy and retired material that used to live at the repository root now sits
under `archive/` so the active paper and code are easier to scan.

## Rebuild

Use the existing environment and LaTeX toolchain:

```powershell
E:\anaconda3\envs\pytorch-clean\python.exe -m pytest
D:\texlive\2025\bin\windows\latexmk.exe -pdf -output-directory=paper paper\main.tex
```

The root-level `main.pdf` is the paper artifact to open and share. The
`paper/main.tex` source is the path to update when the paper itself changes.
Historical LaTeX outputs and alternate draft material are retained in
`archive/`.

## Reproducibility

See [outputs/REPRODUCIBILITY.md](./outputs/REPRODUCIBILITY.md) for the current
environment, logs, hashes, and regeneration commands.
