# TASK-007: Search minimal 1-NN witnesses

## Owner

Claude Code

## Goal

Enumerate small graph metric examples and produce witness JSON for 1-NN separation candidates.

## Context

Use frozen definitions and implemented modules. Computational witnesses are not proofs.
For this task, the searched sample is an ordered tuple that contains each
graph vertex exactly once, with the vertex order explicitly enumerated.
Do not introduce duplicate sample occurrences in TASK-007.

The separation target for this task is:

- fixed-sample brute-force LOO maximum versus
- fixed-sample brute-force replace-one maximum,

both at `k=1`, using the accepted semantics from `stability.py`.

Search space for `--max_vertices M`:

- all connected simple undirected labeled graphs on vertex sets
  `{0, ..., v-1}` for each `1 <= v <= M`;
- all binary labelings of the ordered sample;
- all orderings of the vertex set as the sample order.

## Required work

1. Enumerate the specified finite graph search space.
2. Search for witness candidates where the fixed-sample brute-force maxima for
   `LOO` and `replace-one` differ.
3. Record constraints and assumptions.
4. Save witness JSON under `outputs/witnesses/`.
5. Provide reproducibility command.

## Do not do

- Do not claim minimality as theorem.
- Do not change stability definitions.
- Do not search a narrower space without writing that restriction into the
  output metadata.

## Validation

```powershell
conda run -p E:\anaconda3\envs\pytorch-clean python experiments/search_minimal_1nn.py --max_vertices 4
```

## Report

Return search space, constraints, witnesses, no-solution ranges, output paths, and commands.

