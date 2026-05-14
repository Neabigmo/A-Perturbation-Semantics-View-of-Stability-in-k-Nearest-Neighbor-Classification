# Next Phase Paper Plan

This document operationalizes the next-phase paper instructions in
`NEXT_PHASE_PAPER_PLAN_FOR_CODEX.md` for the repository state as of
2026-05-14.

## Goal

Turn the repository into a credible paper package for a first full draft of:

`A Stability Calculus for Local Learning Rules: Delete-One, Replace-One, and Leave-One-Out Characterizations for k-Nearest Neighbors`

The result should support three reader actions:

1. Read the paper and understand the stability calculus.
2. Inspect proof notes and distinguish theorem from certificate.
3. Reproduce figures, tables, and finite-metric witness outputs.

## Hard Gates

1. Novelty gate before large-scale writing.
2. Claim registry before theorem-style presentation.
3. Proof-note coverage before upgrading any statement to theorem.
4. Reproducibility artifacts before calling the draft submission-grade.

## Current Phase

The repository is in the novelty-and-claim-freeze phase.

Immediate Codex-owned outputs:

- `docs/decisions/DR-20260514-paper-scope.md`
- `docs/decisions/DR-20260514-paper-claims.md`
- `docs/literature/LIT_TABLE.md`
- `docs/literature/novelty_assessment.md`
- `docs/literature/refs_to_add.bib`
- `docs/proof-notes/CLAIM_REGISTRY.md`
- `docs/proof-notes/*.md` for each major mathematical section
- `paper/sections/02_related_work.tex`

Immediate Claude-safe outputs:

- figure production task card
- table generation task card
- LaTeX infrastructure task card
- reproducibility task card
- appendix task card
- BibTeX formatting task card
- README / reproduction task card

## Execution Order

1. `C-TASK-014` Novelty gate.
2. `TASK-017` Reproduce current experiments.
3. `C-TASK-015` Freeze paper claims.
4. `TASK-016` Upgrade LaTeX infrastructure.
5. `TASK-014` Publication-quality figures.
6. `TASK-015` Paper tables.
7. `C-TASK-016` Proof notes.
8. `C-TASK-017` Narrative pass.
9. `TASK-018` Appendix scaffolding.
10. `TASK-019` BibTeX formatting.
11. `TASK-020` README and reproducibility polish.
12. `C-TASK-018` Final integration and audit.

## Current Claim Boundaries

- Uniform perturbation relations: safe as theorem/proposition candidates once
  notation is frozen and proof notes are complete.
- Exact k-NN perturbation criterion: likely proposition-level core technical
  claim; must stay modest and deterministic.
- Two-point 1-NN witness: safe as explicit proposition/example if checked by
  hand.
- Minimality over graph size: computational certificate only unless upgraded by
  a separate proof argument.
- General odd-k lifting: conjectural or certificate-level until Codex proves it.
- Consistency compatibility: discussion claim, not a new consistency theorem.

## Repository Discipline

- Use `E:\anaconda3\envs\pytorch-clean\python.exe` for Python commands.
- Use `D:\texlive\2025\bin\windows\latexmk.exe` for LaTeX builds when needed.
- Before network access, set proxy variables to `127.0.0.1:7897`.
- Claude Code receives only bounded task cards and must not redefine
  mathematics.

## Success Criteria For This Phase

- At least 15 relevant references inspected.
- Every core claim assigned a novelty and proof-status label.
- The related-work section is no longer placeholder text.
- Mechanical task cards exist for the next execution wave.
