# k-NN Stability Calculus

Project for a paper tentatively titled:

**A Stability Calculus for Local Learning Rules: Exact Delete-One, Replace-One, and Leave-One-Out Characterizations for k-Nearest Neighbors**

Codex acts as principal architect and reviewer. Claude Code handles bounded execution tasks through short task cards.

## Current Stage

The repository control plane is being initialized:

- project-control documents in `docs/project-control/`;
- task cards in `tasks/`;
- Claude Code dispatch tooling in `tools/`;
- source skeleton under `src/knn_stability/`;
- tests, experiments, outputs, and paper directories.

## Environment

Use the existing conda environment:

```powershell
conda run -p E:\anaconda3\envs\pytorch-clean python -V
conda run -p E:\anaconda3\envs\pytorch-clean python -m pytest
```

For network commands, set:

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
$env:ALL_PROXY = "socks5://127.0.0.1:7897"
```

## Task Workflow

1. Codex creates or selects a task card from `tasks/TASK_INDEX.md`.
2. Claude Code executes only the bounded task card.
3. Codex reviews the report, diff, tests, and definition consistency.
4. Accepted changes are committed with the task id in the commit message.

Current Claude task runs should target the Opus 4.7 line through the `opus` alias on the configured gateway.
