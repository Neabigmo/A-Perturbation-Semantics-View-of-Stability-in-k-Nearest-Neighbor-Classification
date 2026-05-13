"""Run a bounded Claude Code task card and write its report.

This script intentionally does not read or print API keys. It relies on the
existing process environment for authentication.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_REPORT_DIR = Path("tasks/reports")
DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "opus")
DEFAULT_CLAUDE_BIN = os.environ.get("CLAUDE_BIN") or shutil.which("claude") or shutil.which("claude.cmd") or "claude"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one Claude Code task card.")
    parser.add_argument("task_path", type=Path, help="Path to tasks/active/TASK-XXX.md")
    parser.add_argument(
        "--allowed-tools",
        default="Read,Edit,Bash",
        help="Comma-separated Claude Code tool allow-list.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=DEFAULT_REPORT_DIR,
        help="Directory for task reports.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Claude model alias or name for this task run.",
    )
    parser.add_argument(
        "--effort",
        default=None,
        help="Optional Claude effort level for this task run.",
    )
    parser.add_argument(
        "--claude-bin",
        default=DEFAULT_CLAUDE_BIN,
        help="Path or command name for the Claude Code executable.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print the sanitized command without running Claude.",
    )
    return parser


def env_with_defaults() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("HTTP_PROXY", "http://127.0.0.1:7897")
    env.setdefault("HTTPS_PROXY", "http://127.0.0.1:7897")
    env.setdefault("ALL_PROXY", "socks5://127.0.0.1:7897")
    env.setdefault("http_proxy", env["HTTP_PROXY"])
    env.setdefault("https_proxy", env["HTTPS_PROXY"])
    env.setdefault("all_proxy", env["ALL_PROXY"])
    if env.get("ANTHROPIC_AUTH_TOKEN") and not env.get("ANTHROPIC_API_KEY"):
        # Claude --bare requires ANTHROPIC_API_KEY, so mirror a provided token.
        env["ANTHROPIC_API_KEY"] = env["ANTHROPIC_AUTH_TOKEN"]
    env.setdefault("ANTHROPIC_MODEL", DEFAULT_MODEL)
    env.setdefault("ANTHROPIC_DEFAULT_OPUS_MODEL", "claude-opus-4-7")
    return env


def redact_secrets(text: str, env: dict[str, str]) -> str:
    redacted = text
    for key in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        value = env.get(key)
        if value:
            redacted = redacted.replace(value, f"<redacted:{key}>")
    return redacted


def run_task(
    task_path: Path,
    allowed_tools: str,
    report_dir: Path,
    model: str,
    effort: str | None,
    claude_bin: str,
    dry_run: bool,
) -> int:
    if not task_path.exists():
        raise SystemExit(f"Task file not found: {task_path}")

    task_id = task_path.stem
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{task_id}.report.json"
    failed_path = report_dir / f"{task_id}.failed.json"

    prompt = task_path.read_text(encoding="utf-8")
    cmd = [
        claude_bin,
        "--bare",
        "-p",
        prompt,
        "--model",
        model,
        "--allowedTools",
        allowed_tools,
        "--output-format",
        "json",
    ]
    if effort:
        cmd.extend(["--effort", effort])

    if dry_run:
        parts = [
            f"{claude_bin} --bare -p <task prompt>",
            f"--model {model}",
            f"--allowedTools {allowed_tools}",
            "--output-format json",
        ]
        if effort:
            parts.append(f"--effort {effort}")
        print(" ".join(parts))
        return 0

    env = env_with_defaults()
    if not env.get("ANTHROPIC_API_KEY"):
        failed = {
            "task_id": task_id,
            "status": "blocked",
            "reason": (
                "Neither ANTHROPIC_API_KEY nor ANTHROPIC_AUTH_TOKEN is set "
                "in the process environment."
            ),
            "report_path": str(report_path),
            "model": model,
        }
        failed_path.write_text(json.dumps(failed, indent=2), encoding="utf-8")
        print(f"Blocked: auth token is not set. Wrote {failed_path}", file=sys.stderr)
        return 2

    started = time.time()
    result = subprocess.run(cmd, env=env, text=True, capture_output=True, check=False)
    elapsed_seconds = round(time.time() - started, 3)

    report_path.write_text(redact_secrets(result.stdout, env), encoding="utf-8")

    metadata = {
        "task_id": task_id,
        "model": model,
        "exit_code": result.returncode,
        "elapsed_seconds": elapsed_seconds,
        "report_path": str(report_path),
    }
    if result.returncode != 0:
        failed = {
            **metadata,
            "status": "failed",
            "stderr": redact_secrets(result.stderr, env),
        }
        failed_path.write_text(json.dumps(failed, indent=2), encoding="utf-8")
        print(f"Claude task failed. Wrote {failed_path}", file=sys.stderr)
        return result.returncode

    meta_path = report_dir / f"{task_id}.meta.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return run_task(
        args.task_path,
        args.allowed_tools,
        args.report_dir,
        args.model,
        args.effort,
        args.claude_bin,
        args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
