# TASK-005: Implement deterministic k-NN classifier

## Owner

Claude Code

## Goal

Implement deterministic k-NN prediction using the frozen metric, sample, and tie-breaking definitions.

## Context

Use `docs/project-control/02_DEFINITIONS_SPEC.md`, `metrics.py`, and `tie_breaking.py`.

## Required work

1. Implement ordered neighbor selection.
2. Implement binary-label vote prediction for odd and even k.
3. Add tests for training-point queries, distance ties, and label ties.

## Do not do

- Do not implement stability indicators.
- Do not change definitions.

## Validation

```powershell
conda run -p E:\anaconda3\envs\pytorch-clean python -m pytest
```

## Report

Return structured report.

