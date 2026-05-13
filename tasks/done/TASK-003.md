# TASK-003: Implement graph shortest-path metrics

## Owner

Claude Code

## Goal

Implement unweighted connected graph shortest-path metrics.

## Context

Use `docs/project-control/02_DEFINITIONS_SPEC.md` and the finite metric interface from TASK-002.

## Required work

1. Convert an undirected unweighted connected graph into shortest-path distances.
2. Reject disconnected graphs.
3. Add tests for paths, cycles, complete graphs, and disconnected graphs.

## Do not do

- Do not change finite metric validation semantics.
- Do not implement enumeration.

## Validation

```powershell
conda run -p E:\anaconda3\envs\pytorch-clean python -m pytest
```

## Report

Return structured status, files changed, tests, ambiguities, and next steps.

