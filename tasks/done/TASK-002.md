# TASK-002: Implement finite metric spaces

## Owner

Claude Code

## Role

You are an execution agent. Do not redefine mathematical concepts. Implement exactly what is specified here.

## Goal

Implement `FiniteMetricSpace` and tests after definitions are frozen.

## Context

Use `docs/project-control/02_DEFINITIONS_SPEC.md` as the authority.

## Required work

1. Implement finite point set and distance matrix validation.
2. Reject non-square, asymmetric, negative, nonzero diagonal, and triangle inequality violations.
3. Add focused pytest coverage.

## Do not do

- Do not implement graph metrics.
- Do not implement k-NN or stability definitions.

## Validation

```powershell
conda run -p E:\anaconda3\envs\pytorch-clean python -m pytest
```

## Report

Return files changed, commands run, tests, assumptions, ambiguities, and next steps.

