"""Generate computational minimality certificates from accepted witness outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from knn_stability.witnesses import load_witness_search  # noqa: E402


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hash of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_certificate(
    separation_path: Path,
    tie_free_path: Path,
) -> dict[str, object]:
    """Build the computational certificate payload."""
    separation_payload = load_witness_search(separation_path)
    tie_free_payload = load_witness_search(tie_free_path)

    separation_metadata = separation_payload["metadata"]
    tie_free_metadata = tie_free_payload["metadata"]

    return {
        "title": "Computational Minimality Certificate for 1-NN Separation Search",
        "status": "computational_evidence_only",
        "not_a_proof": True,
        "source_outputs": {
            "task_007": {
                "path": str(separation_path),
                "sha256": sha256_file(separation_path),
            },
            "task_008": {
                "path": str(tie_free_path),
                "sha256": sha256_file(tie_free_path),
            },
        },
        "search_ranges": {
            "task_007_vertex_range": separation_metadata["search_space"]["vertex_range"],
            "task_008_vertex_range": tie_free_metadata["search_space"]["vertex_range"],
        },
        "observed_no_solution_ranges": {
            "task_007": separation_metadata["no_solution_vertex_counts"],
            "task_008": tie_free_metadata["no_solution_vertex_counts"],
        },
        "observed_minimal_vertex_counts": {
            "task_007": separation_metadata["minimal_vertex_count"],
            "task_008": tie_free_metadata["minimal_vertex_count"],
        },
        "counts_by_vertices": {
            "task_007": separation_metadata["counts_by_vertices"],
            "task_008": tie_free_metadata["counts_by_vertices"],
        },
        "reproducibility_commands": [
            "conda run -p E:\\anaconda3\\envs\\pytorch-clean python experiments/search_minimal_1nn.py --max_vertices 4",
            "E:\\anaconda3\\envs\\pytorch-clean\\python.exe experiments/search_tie_free.py --input outputs/witnesses/1nn_separation_witnesses.json --output outputs/witnesses/1nn_tie_free_witnesses.json",
            "conda run -p E:\\anaconda3\\envs\\pytorch-clean python experiments/certify_minimality.py",
        ],
        "assumptions": [
            "All certificate statements are restricted to the searched spaces recorded in the source outputs.",
            "The sample contains each graph vertex exactly once in the searched witness tasks.",
            "Computational evidence is not a theorem-level minimality proof.",
        ],
    }


def write_markdown_certificate(payload: dict[str, object], output_path: Path) -> None:
    """Write a human-readable Markdown certificate summary."""
    lines = [
        "# Computational Minimality Certificate",
        "",
        "This document is computational evidence only. It is not a proof.",
        "",
        "## Observed Minimal Vertex Counts",
        "",
        f"- TASK-007 separation witnesses: `{payload['observed_minimal_vertex_counts']['task_007']}`",
        f"- TASK-008 tie-free witnesses: `{payload['observed_minimal_vertex_counts']['task_008']}`",
        "",
        "## Observed No-Solution Vertex Counts",
        "",
        f"- TASK-007: `{payload['observed_no_solution_ranges']['task_007']}`",
        f"- TASK-008: `{payload['observed_no_solution_ranges']['task_008']}`",
        "",
        "## Output Hashes",
        "",
        f"- `TASK-007`: `{payload['source_outputs']['task_007']['sha256']}`",
        f"- `TASK-008`: `{payload['source_outputs']['task_008']['sha256']}`",
        "",
        "## Reproducibility Commands",
        "",
    ]
    lines.extend([f"- `{command}`" for command in payload["reproducibility_commands"]])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate computational minimality certificates from TASK-007 and TASK-008 outputs."
    )
    parser.add_argument(
        "--separation",
        type=Path,
        default=ROOT / "outputs" / "witnesses" / "1nn_separation_witnesses.json",
        help="TASK-007 witness JSON path.",
    )
    parser.add_argument(
        "--tie_free",
        type=Path,
        default=ROOT / "outputs" / "witnesses" / "1nn_tie_free_witnesses.json",
        help="TASK-008 tie-free witness JSON path.",
    )
    parser.add_argument(
        "--json_output",
        type=Path,
        default=ROOT / "outputs" / "witnesses" / "1nn_minimality_certificate.json",
        help="Output path for the JSON certificate.",
    )
    parser.add_argument(
        "--markdown_output",
        type=Path,
        default=ROOT / "outputs" / "tables" / "1nn_minimality_certificate.md",
        help="Output path for the Markdown certificate summary.",
    )
    return parser.parse_args()


def main() -> int:
    """Generate the certificate files."""
    args = parse_args()
    payload = build_certificate(args.separation, args.tie_free)

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)

    args.json_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_markdown_certificate(payload, args.markdown_output)

    print(f"Wrote JSON certificate to {args.json_output}")
    print(f"Wrote Markdown certificate to {args.markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
