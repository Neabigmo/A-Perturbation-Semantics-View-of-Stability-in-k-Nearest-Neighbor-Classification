# TASK-008: Search tie-free witnesses

## Owner

Claude Code

## Goal

Search for separation witnesses with distance ties excluded.

## Context

Use the same frozen definitions and output conventions as TASK-007.
For TASK-008, use `k=1` and the same search space as TASK-007 unless an
explicitly documented restriction is added to the output metadata.

Tie-free means the witness does not rely on distance ties in the predictions
that certify separation. Concretely, for every prediction actually used in the
accepted LOO and replace-one witness records:

- the relevant query point has a unique nearest sample occurrence;
- this must hold both before and after the corresponding perturbation.

## Required work

1. Implement or run a tie-free search mode.
2. Verify the tie-free condition explicitly.
3. Save results and logs.
4. Record whether the TASK-007 minimal witnesses survive the tie-free filter.

## Do not do

- Do not weaken the tie-free condition.
- Do not claim mathematical impossibility from incomplete search.
- Do not check only the original sample while ignoring the witness perturbation.

## Validation

Run the relevant deterministic experiment and pytest.

## Report

Return structured report with search space and reproducibility command.
