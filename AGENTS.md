# AGENTS.md

This repository studies stability calculus for k-nearest-neighbor and related local learning rules.

## Roles

- Codex is the principal architect, mathematical reviewer, literature reviewer, and final integrator.
- Claude Code is an execution agent for bounded, low-level, verifiable tasks.
- Claude Code must not redefine mathematical concepts, decide novelty, or promote computational evidence to theorem status.

## Environment

- Repository root: `H:\2026try\5.13`.
- Preferred conda environment path: `E:\anaconda3\envs\pytorch-clean`.
- Preferred LaTeX distribution path: `D:\texlive\2025`.
- Use non-interactive commands such as:

```powershell
conda run -p E:\anaconda3\envs\pytorch-clean python -m pytest
```

- Project Python compatibility is `>=3.9`.
- For LaTeX compilation, prefer executables under `D:\texlive\2025\bin\windows`
  when available.
- Before network commands, set proxy variables explicitly:

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
$env:ALL_PROXY = "socks5://127.0.0.1:7897"
```

## Git Rules

- Use git from the beginning.
- Use one branch or worktree per task.
- Include the task id in each task commit message.
- Do not commit secrets, `.env`, raw logs, temporary caches, or API keys.
- Codex must review `git diff`, run tests, and check mathematical consistency before accepting Claude Code output.

## Quality Rules

- Do not simplify assumptions, weaken proofs, skip tests, or reduce reproducibility without explicit user approval.
- Do not state unproved claims as theorems.
- Do not treat enumeration as proof unless a formal argument is also supplied.
- Do not mix up delete-one, add-one, replace-one, LOO, pointwise, expected, and uniform stability.
- Do not ignore tie-breaking, duplicate samples, or conflicting labels.

## Context Firewall

- Each Claude Code task receives only one short task card.
- Do not send the full research blueprint or unpublished proof sketches to Claude Code unless the task truly requires it.
- Claude Code reports must list changed files, commands run, test results, assumptions, ambiguities, and next steps.
