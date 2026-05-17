from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_tables"


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_jmlr_extension_tables_exist_and_are_nonempty() -> None:
    expected = [
        "jmlr_exhaustive_minimality_map.csv",
        "jmlr_continuous_stress.csv",
        "jmlr_real_data_extended.csv",
        "jmlr_diagnostic_runtime.csv",
        "jmlr_repair_experiment.csv",
        "jmlr_margin_distribution.csv",
    ]
    for name in expected:
        rows = read_rows(name)
        assert rows, name


def test_real_data_extension_has_expected_scope() -> None:
    rows = read_rows("jmlr_real_data_extended.csv")
    datasets = {r["dataset"] for r in rows}
    metrics = {r["metric"] for r in rows}
    ks = {int(r["k"]) for r in rows}
    assert {"iris", "wine", "breast_cancer", "digits"} <= datasets
    assert {"euclidean", "manhattan", "cosine"} <= metrics
    assert {1, 3, 5, 7, 9, 11, 15} <= ks
    for row in rows[:50]:
        assert 0.0 <= float(row["loo_error"]) <= 1.0
        assert 0.0 <= float(row["replace_vulnerability"]) <= 1.0
        assert 0.0 <= float(row["near_zero_margin_mass"]) <= 1.0


def test_continuous_stress_has_jitter_grid() -> None:
    rows = read_rows("jmlr_continuous_stress.csv")
    generators = {r["generator"] for r in rows}
    jitters = {float(r["jitter"]) for r in rows}
    assert {"blobs", "moons", "circles", "anisotropic"} <= generators
    assert {0.0, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1} <= jitters


def test_repair_table_contains_both_strategies() -> None:
    rows = read_rows("jmlr_repair_experiment.csv")
    strategies = {r["strategy"] for r in rows}
    assert {"cv_min_loo", "margin_aware_k"} <= strategies
    for row in rows:
        assert int(row["selected_k"]) in {1, 3, 5, 7, 9, 11, 15}
        assert 0.0 <= float(row["replace_vulnerability"]) <= 1.0
