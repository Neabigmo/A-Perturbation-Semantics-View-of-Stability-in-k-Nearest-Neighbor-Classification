"""Run the reproducible machine-learning submission pipeline.

This script orchestrates witness search, benchmark generation, and rendering
steps from a single TOML config. Outputs are split into:

- raw: JSON artifacts produced by experiments and searches
- summaries: copied prose/control documents for the run
- rendered: Nature-style figures and tables generated from raw artifacts
- manifests: run metadata, commands, and file hashes
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class RunPaths:
    root: Path
    raw: Path
    raw_witnesses: Path
    raw_experiments: Path
    summaries: Path
    rendered: Path
    rendered_figures: Path
    rendered_tables: Path
    manifests: Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def repo_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def make_run_paths(run_name: str, timestamp: str) -> RunPaths:
    root = ROOT / "outputs" / "runs" / run_name / timestamp
    raw = root / "raw"
    raw_witnesses = raw / "witnesses"
    raw_experiments = raw / "experiments"
    summaries = root / "summaries"
    rendered = root / "rendered"
    rendered_figures = rendered / "figures"
    rendered_tables = rendered / "tables"
    manifests = root / "manifests"
    for path in [
        raw_witnesses,
        raw_experiments,
        summaries,
        rendered_figures,
        rendered_tables,
        manifests,
    ]:
        path.mkdir(parents=True, exist_ok=True)
    return RunPaths(
        root=root,
        raw=raw,
        raw_witnesses=raw_witnesses,
        raw_experiments=raw_experiments,
        summaries=summaries,
        rendered=rendered,
        rendered_figures=rendered_figures,
        rendered_tables=rendered_tables,
        manifests=manifests,
    )


def build_command(script: str, *args: object, python_executable: str) -> list[str]:
    cmd = [python_executable, script]
    cmd.extend(str(arg) for arg in args)
    return cmd


def run_step(name: str, cmd: list[str], manifest_entries: list[dict[str, Any]]) -> None:
    started_at = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    finished_at = datetime.now(timezone.utc).isoformat()
    manifest_entries.append(
        {
            "step": name,
            "command": cmd,
            "returncode": result.returncode,
            "started_at": started_at,
            "finished_at": finished_at,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    )
    if result.returncode != 0:
        raise RuntimeError(f"{name} failed with return code {result.returncode}")


def write_run_reproducibility(summary_path: Path, config_relpath: str, head_sha: str) -> None:
    summary_path.write_text(
        "\n".join(
            [
                "# Run Reproducibility",
                "",
                f"- Config: `{config_relpath}`",
                f"- Git HEAD: `{head_sha}`",
                "- LaTeX: `D:\\texlive\\2025\\bin\\windows\\latexmk.exe`",
                "- Figure standard: `external/nature-skills/skills/nature-figure`",
                "- Entry point: `python experiments/run_all.py --config ...`",
                "- Output layout:",
                "  - `raw/`: JSON artifacts from search and benchmark stages",
                "  - `rendered/`: generated figures and LaTeX tables",
                "  - `summaries/`: copied reference/control documents for this run",
                "  - `manifests/`: commands, timestamps, and SHA-256 checksums",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def collect_file_manifest(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        files.append(
            {
                "path": str(path.relative_to(root)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full ML submission pipeline from a TOML config.")
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "experiments" / "configs" / "ml_submission.toml",
    )
    parser.add_argument("--timestamp", type=str, default=None)
    parser.add_argument(
        "--with-figures",
        action="store_true",
        help="Also run the optional manuscript figure renderer if experiments/nature_figures.py is present.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    run_name = config.get("run_name", "ml_submission")
    python_executable = config.get("python_executable", sys.executable)
    timestamp = args.timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
    paths = make_run_paths(run_name, timestamp)
    manifest_entries: list[dict[str, Any]] = []
    head_sha = repo_head()

    config_copy = paths.manifests / "config.toml"
    shutil.copy2(args.config, config_copy)
    write_run_reproducibility(paths.summaries / "REPRODUCIBILITY.md", str(args.config), head_sha)
    shutil.copy2(ROOT / "docs" / "literature" / "LIT_TABLE.md", paths.summaries / "LIT_TABLE.md")

    witness = config["witness_search"]
    synthetic = config["synthetic"]
    tabular = config["tabular"]

    separation_json = paths.raw_witnesses / "1nn_separation_witnesses.json"
    tie_free_json = paths.raw_witnesses / "1nn_tie_free_witnesses.json"
    certificate_json = paths.raw_witnesses / "1nn_minimality_certificate.json"
    certificate_md = paths.summaries / "1nn_minimality_certificate.md"
    gadget_json = paths.raw_witnesses / "k_gadget_candidates.json"
    synthetic_json = paths.raw_experiments / "synthetic_benchmark.json"
    tabular_json = paths.raw_experiments / "tabular_benchmark.json"

    run_step(
        "search_minimal_1nn",
        build_command(
            "experiments/search_minimal_1nn.py",
            "--max_vertices",
            witness["max_vertices"],
            "--output",
            separation_json,
            python_executable=python_executable,
        ),
        manifest_entries,
    )
    run_step(
        "search_tie_free",
        build_command(
            "experiments/search_tie_free.py",
            "--input",
            separation_json,
            "--output",
            tie_free_json,
            python_executable=python_executable,
        ),
        manifest_entries,
    )
    run_step(
        "certify_minimality",
        build_command(
            "experiments/certify_minimality.py",
            "--separation",
            separation_json,
            "--tie_free",
            tie_free_json,
            "--json_output",
            certificate_json,
            "--markdown_output",
            certificate_md,
            python_executable=python_executable,
        ),
        manifest_entries,
    )
    run_step(
        "search_k_gadgets",
        build_command(
            "experiments/search_k_gadgets.py",
            "--k_values",
            *witness["gadget_k_values"],
            "--min_vertices",
            witness["gadget_min_vertices"],
            "--max_vertices",
            witness["gadget_max_vertices"],
            "--length_modes",
            *witness["gadget_length_modes"],
            "--max_candidates_per_k",
            witness["gadget_max_candidates_per_k"],
            "--output",
            gadget_json,
            python_executable=python_executable,
        ),
        manifest_entries,
    )
    run_step(
        "synthetic_benchmark",
        build_command(
            "experiments/stability_gap_synthetic.py",
            "--k_values",
            *synthetic["k_values"],
            "--n_vertices",
            *synthetic["n_vertices"],
            "--sample_sizes",
            *synthetic["sample_sizes"],
            "--duplicate_ratios",
            *synthetic["duplicate_ratios"],
            "--conflict_ratios",
            *synthetic["conflict_ratios"],
            "--noise_ratios",
            *synthetic["noise_ratios"],
            "--n_trials",
            synthetic["n_trials"],
            "--base_seed",
            synthetic["base_seed"],
            "--output",
            synthetic_json,
            python_executable=python_executable,
        ),
        manifest_entries,
    )
    run_step(
        "tabular_benchmark",
        build_command(
            "experiments/stability_gap_tabular.py",
            "--datasets",
            *tabular["datasets"],
            "--k_values",
            *tabular["k_values"],
            "--subsample_sizes",
            *tabular["subsample_sizes"],
            "--n_replicates",
            tabular["n_replicates"],
            "--base_seed",
            tabular["base_seed"],
            "--output",
            tabular_json,
            python_executable=python_executable,
        ),
        manifest_entries,
    )
    figure_script = ROOT / "experiments" / "nature_figures.py"
    if args.with_figures and figure_script.exists():
        run_step(
            "nature_figures",
            build_command(
                "experiments/nature_figures.py",
                "--synthetic_json",
                synthetic_json,
                "--tabular_json",
                tabular_json,
                "--output_dir",
                paths.rendered_figures,
                python_executable=python_executable,
            ),
            manifest_entries,
        )
    run_step(
        "generate_paper_tables",
        build_command(
            "experiments/generate_paper_tables.py",
            "--witness_dir",
            paths.raw_witnesses,
            "--reproducibility_md",
            paths.summaries / "REPRODUCIBILITY.md",
            "--lit_table",
            paths.summaries / "LIT_TABLE.md",
            "--output_dir",
            paths.rendered_tables,
            python_executable=python_executable,
        ),
        manifest_entries,
    )

    manifest = {
        "run_name": run_name,
        "timestamp": timestamp,
        "config": str(args.config),
        "git_head": head_sha,
        "steps": manifest_entries,
        "files": collect_file_manifest(paths.root),
    }
    (paths.manifests / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print(f"Run complete: {paths.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
