# TASK-014: Build publication-quality witness figures

## Owner
Claude Code

## Role
You are a figure-production agent. Do not redefine mathematical concepts.

## Goal
Upgrade witness visualizations into publication-quality figures for the paper.

## Context
Use existing witness JSON files and the frozen definitions. If definitions are
needed, read `docs/project-control/02_DEFINITIONS_SPEC.md` or the corresponding
paper definitions section. Do not invent new definitions.

## Required work
1. Inspect `outputs/witnesses/*.json`.
2. Improve `experiments/generate_witness_figures.py` or create
   `experiments/generate_paper_figures.py`.
3. Generate:
   - `outputs/figures/stability_notions_diagram.pdf/svg/png`
   - `outputs/figures/uniform_calculus_diagram.pdf/svg/png`
   - `outputs/figures/knn_topk_boundary.pdf/svg/png`
   - `outputs/figures/minimal_1nn_witness_before_after.pdf/svg/png`
   - `outputs/figures/tie_breaking_microscope.pdf/svg/png`
   - `outputs/figures/k_gadget_candidates.pdf/svg/png` if candidate data exists
   - `outputs/figures/stability_regimes_map.pdf/svg/png`
4. Use accessible visual encodings: label text, shapes, line styles, not color alone.
5. Add caption drafts in `outputs/figures/captions.md`.
6. Do not claim computational evidence is proof.

## Validation
Run:
`E:\anaconda3\envs\pytorch-clean\python.exe experiments\generate_paper_figures.py`
`E:\anaconda3\envs\pytorch-clean\python.exe -m pytest`

## Report
Return files changed, commands run, output files, and missing data.
