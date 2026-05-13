# Claude Delegation Protocol

## Principles

- One task card per Claude Code run.
- Minimal context only.
- No full research blueprint unless required.
- Claude Code must not change mathematical definitions.
- Claude Code must return a structured report.

## Command Template

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:7897"
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
$env:ALL_PROXY = "socks5://127.0.0.1:7897"
$env:ANTHROPIC_MODEL = "opus"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "claude-opus-4-7"
python tools/run_claude_task.py tasks/active/TASK-001.md --model opus
```

## Required Report Fields

- status;
- summary;
- files changed;
- commands run;
- tests;
- mathematical assumptions;
- ambiguities;
- next steps.

## Codex Review

Codex must inspect the report, run `git diff`, run tests, and check consistency with `02_DEFINITIONS_SPEC.md` before accepting.
