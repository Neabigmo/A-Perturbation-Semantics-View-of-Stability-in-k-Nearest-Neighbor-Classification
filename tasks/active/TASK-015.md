# TASK-015: Generate LaTeX tables from experiment outputs

## Owner
Claude Code

## Goal
Create reproducible LaTeX tables from witness and certificate JSON files.

## Required work
1. Read `outputs/witnesses/*.json`.
2. Create `experiments/generate_paper_tables.py`.
3. Generate:
   - `outputs/tables/stability_notions.tex`
   - `outputs/tables/minimal_witnesses.tex`
   - `outputs/tables/k_gadget_candidates.tex`
   - `outputs/tables/certificate_summary.tex`
   - `outputs/tables/reproducibility_summary.tex`
4. Tables must include a note when status is computational evidence only.
5. Do not edit mathematical statements in paper sections.

## Validation
`E:\anaconda3\envs\pytorch-clean\python.exe experiments\generate_paper_tables.py`
`E:\anaconda3\envs\pytorch-clean\python.exe -m pytest`

## Report
Return changed files, generated files, commands, and assumptions.
