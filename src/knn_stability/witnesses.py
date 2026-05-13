"""Witness serialization helpers.

Witnesses are computational evidence unless Codex supplies a separate proof audit.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WitnessRecord:
    """Serialized record for a fixed-sample separation witness candidate."""

    num_vertices: int
    num_edges: int
    adjacency_list: dict[int, list[int]]
    sample_order: list[int]
    labels: list[int]
    loo_max: int
    loo_witness_index: int
    replace_max: int
    replace_witness_index: int
    replace_witness_replacement_point: int
    replace_witness_replacement_label: int
    replace_witness_query_point: int
    replace_witness_query_label: int
    separation_gap: int


def witness_record_to_dict(record: WitnessRecord) -> dict[str, Any]:
    """Convert a witness record into a JSON-serializable dictionary."""
    return asdict(record)


def save_witness_search(
    output_path: Path,
    metadata: dict[str, Any],
    witnesses: list[WitnessRecord],
) -> None:
    """Save witness-search metadata and records to JSON."""
    payload = {
        "metadata": metadata,
        "witnesses": [witness_record_to_dict(record) for record in witnesses],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_witness_search(output_path: Path) -> dict[str, Any]:
    """Load a witness-search JSON payload."""
    return json.loads(output_path.read_text(encoding="utf-8"))
