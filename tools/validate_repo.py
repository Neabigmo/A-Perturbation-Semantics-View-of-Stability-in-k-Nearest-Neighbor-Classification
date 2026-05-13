"""Validate the initial repository skeleton."""

from __future__ import annotations

from pathlib import Path


REQUIRED_PATHS = [
    "AGENTS.md",
    "CODEX_MASTER_ORCHESTRATION.md",
    "README.md",
    "pyproject.toml",
    "environment.yml",
    ".gitignore",
    ".env.template",
    "docs/project-control/02_DEFINITIONS_SPEC.md",
    "tasks/TASK_INDEX.md",
    "tasks/active",
    "tasks/backlog/TASK-002.md",
    "tasks/done",
    "tools/run_claude_task.py",
    "src/knn_stability/__init__.py",
    "tests/test_metrics.py",
    "paper/main.tex",
]


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not Path(path).exists()]
    if missing:
        for path in missing:
            print(f"missing: {path}")
        return 1
    print("repository skeleton validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
