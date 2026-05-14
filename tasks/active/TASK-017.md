# TASK-017: Reproduce all current experiments

## Owner
Claude Code

## Goal
Regenerate or verify all computational artifacts used by the paper.

## Required work
1. Run pytest.
2. Run minimal 1-NN witness search.
3. Run tie-free witness search if present.
4. Run minimality certificate generation if present.
5. Run k-gadget search for currently supported `k` values.
6. Save logs under `outputs/logs/`.
7. Compute SHA256 hashes for JSON outputs.
8. Create `outputs/REPRODUCIBILITY.md`.
9. Do not interpret results as proof unless Codex has classified them.

## Validation
`E:\anaconda3\envs\pytorch-clean\python.exe -m pytest`

Run all experiment scripts with documented commands.

## Report
Return commands, runtimes, output paths, hashes, and failures.
