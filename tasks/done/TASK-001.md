# TASK-001: Initialize repository skeleton

## Owner

Claude Code

## Role

You are an execution agent. Do not redefine mathematical concepts. Implement exactly what is specified here.

## Goal

Check and complete the repository skeleton for the k-NN stability calculus project.

## Context

Codex has created the initial control plane. Your job is only to fill missing mechanical skeleton pieces, not to implement mathematical logic.

## Inputs

- `AGENTS.md`
- `README.md`
- `pyproject.toml`
- `environment.yml`
- `docs/project-control/`
- `tasks/TASK_INDEX.md`

## Required work

1. Verify that the directory structure requested in `CODEX_MASTER_ORCHESTRATION.md` exists.
2. Create missing empty package/test/paper skeleton files if needed.
3. Ensure placeholder source modules contain no final mathematical implementation.
4. Ensure tests are minimal skeleton tests only.
5. Run validation commands.

## Do not do

- Do not change definitions.
- Do not implement `FiniteMetricSpace`, graph metrics, k-NN, or stability logic.
- Do not edit unrelated files.
- Do not simplify assumptions.
- Do not claim a theorem is proved.
- Do not touch API keys or create `.env`.

## Validation

Run:

```powershell
conda run -p E:\anaconda3\envs\pytorch-clean python -m pytest
```

If pytest is unavailable or fails because the environment is incomplete, report the exact command and exit code.

## Report

Return a structured JSON report with:

- status;
- summary;
- files changed;
- commands run;
- tests;
- mathematical assumptions;
- ambiguities;
- next steps.

