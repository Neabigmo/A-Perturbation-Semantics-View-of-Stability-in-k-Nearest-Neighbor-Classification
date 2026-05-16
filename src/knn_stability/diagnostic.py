"""StabilityGapDiagnostic: Algorithm for diagnosing LOO/replace-one stability gaps.

The diagnostic takes a distance matrix, labels, k, tie-breaking rule,
and replacement candidate set, and outputs:
- LOO instability profile
- Delete/insert/replace instability profile
- Vulnerable queries (where margin is within replace-one flip range)
- Margin-crossing certificates
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from knn_stability.knn import LabeledSample, predict_knn
from knn_stability.metrics import FiniteMetricSpace
from knn_stability.stability import (
    pointwise_loo_stability,
    pointwise_delete_one_stability,
    pointwise_add_one_stability,
    pointwise_replace_one_stability,
    binary_loss,
)
from knn_stability.tie_breaking import (
    select_k_neighbors,
    compute_majority_vote,
    order_neighbors_by_distance_and_index,
)


@dataclass
class DiagnosticResult:
    """Output of the StabilityGapDiagnostic for a single sample and k.

    Attributes
    ----------
    k : int
        Number of nearest neighbors.
    n_sample : int
        Sample size.
    n_metric : int
        Metric space size.
    loo_profile : list[int]
        LOO indicator for each index i.
    max_loo : int
        Maximum LOO indicator.
    all_loo_zero : bool
        True if all LOO indicators are zero.
    delete_one_max : int
        Maximum delete-one indicator over all indices and queries.
    insert_one_max : int
        Maximum insert-one indicator over all insertions and queries.
    replace_one_max : int
        Maximum replace-one indicator over all indices, replacements, and queries.
    loo_rep_gap : int
        replace_one_max - max_loo.
    vulnerable_queries : list[VulnerableQuery]
        List of queries flagged as potentially vulnerable.
    margin_profile : list[MarginRecord]
        Signed margin at each query point before and after key perturbations.
    """

    k: int
    n_sample: int
    n_metric: int
    loo_profile: list[int]
    max_loo: int
    all_loo_zero: bool
    delete_one_max: int
    insert_one_max: int
    replace_one_max: int
    loo_rep_gap: int
    vulnerable_queries: list[VulnerableQuery] = field(default_factory=list)
    margin_profile: list[MarginRecord] = field(default_factory=list)


@dataclass
class VulnerableQuery:
    """A query identified as potentially vulnerable to replace-one perturbation.

    Attributes
    ----------
    query_point_idx : int
        Index of the query point in the metric space.
    query_label : int
        The query label.
    original_margin : int
        Signed vote margin before perturbation.
    margin_gap : int
        Distance from margin to the prediction threshold (0).
    max_single_change : int
        Maximum possible change to margin from a single replacement.
    is_vulnerable : bool
        True if margin_gap <= max_single_change.
    """

    query_point_idx: int
    query_label: int
    original_margin: int
    margin_gap: int
    max_single_change: int
    is_vulnerable: bool


@dataclass
class MarginRecord:
    """Signed margin before and after a specified perturbation.

    Attributes
    ----------
    query_point_idx : int
        Query point index in metric space.
    perturbation_type : str
        'original', 'loo', 'replace_one', etc.
    perturbation_index : int | None
        Index of the perturbed occurrence.
    margin : int
        Signed vote margin after perturbation.
    prediction : int
        Predicted label (0 or 1).
    """

    query_point_idx: int
    perturbation_type: str
    perturbation_index: int | None
    margin: int
    prediction: int


def compute_signed_margin(sample: LabeledSample, query_point_idx: int, k: int) -> int:
    """Compute the signed vote margin M_k(S, x).

    Returns the sum of (2*y_i - 1) over the top-k ordered neighbors.
    """
    neighbor_indices = select_k_neighbors(
        query_point_idx=query_point_idx,
        sample_point_indices=np.array(sample.point_indices),
        distances=sample.metric.distances,
        k=k,
    )
    neighbor_labels = np.array([sample.labels[i] for i in neighbor_indices])
    margin = int(np.sum(2 * neighbor_labels - 1))
    return margin


def predict_from_margin(margin: int) -> int:
    """Predict label from signed margin with tie-breaking (0 < 1)."""
    return 1 if margin > 0 else 0


def diagnose_sample(
    sample: LabeledSample,
    k: int,
    compute_all_replacements: bool = True,
    skip_delete_one: bool = False,
    skip_insert_one: bool = False,
) -> DiagnosticResult:
    """Run the full stability diagnostic on a sample.

    Parameters
    ----------
    sample : LabeledSample
        The ordered training sample to diagnose.
    k : int
        Number of nearest neighbors.
    compute_all_replacements : bool
        If True, computes exhaustive replace-one max (expensive for large spaces).
    skip_delete_one : bool
        If True, skips the O(n*m) delete-one computation.
    skip_insert_one : bool
        If True, skips the O(m^2) insert-one computation.

    Returns
    -------
    DiagnosticResult
        Complete diagnostic output.
    """
    n = sample.n
    m = sample.metric.n

    # --- LOO profile ---
    loo_profile: list[int] = []
    for i in range(n):
        try:
            val = pointwise_loo_stability(sample, i, k)
        except (ValueError, IndexError):
            val = 0
        loo_profile.append(val)

    max_loo = max(loo_profile) if loo_profile else 0
    all_loo_zero = all(v == 0 for v in loo_profile)

    # --- Delete-one max (skip when only LOO/replace-one needed) ---
    if skip_delete_one:
        del_max = -1
    else:
        del_max = 0
        for i in range(n):
            for q_idx in range(m):
                for q_label in (0, 1):
                    try:
                        val = pointwise_delete_one_stability(sample, i, q_idx, q_label, k)
                        del_max = max(del_max, val)
                    except (ValueError, IndexError):
                        pass

    # --- Insert-one max (expensive O(m^2), skip when not needed) ---
    if skip_insert_one:
        ins_max = -1
    else:
        ins_max = 0
        for new_idx in range(m):
            for new_label in (0, 1):
                for q_idx in range(m):
                    for q_label in (0, 1):
                        try:
                            val = pointwise_add_one_stability(
                                sample, new_idx, new_label, q_idx, q_label, k
                            )
                            ins_max = max(ins_max, val)
                        except (ValueError, IndexError):
                            pass

    # --- Replace-one max ---
    if compute_all_replacements:
        rep_max = 0
        for rep_idx in range(n):
            for new_idx in range(m):
                for new_label in (0, 1):
                    for q_idx in range(m):
                        for q_label in (0, 1):
                            try:
                                val = pointwise_replace_one_stability(
                                    sample, rep_idx, new_idx, new_label,
                                    q_idx, q_label, k,
                                )
                                rep_max = max(rep_max, val)
                            except (ValueError, IndexError):
                                pass
    else:
        # Fast approximate: only test same-point label flips
        rep_max = 0
        for rep_idx in range(n):
            orig_point = sample.point_indices[rep_idx]
            flipped_label = 1 - sample.labels[rep_idx]
            for q_idx in range(m):
                for q_label in (0, 1):
                    try:
                        val = pointwise_replace_one_stability(
                            sample, rep_idx, orig_point, flipped_label,
                            q_idx, q_label, k,
                        )
                        rep_max = max(rep_max, val)
                    except (ValueError, IndexError):
                        pass

    loo_rep_gap = rep_max - max_loo

    # --- Margin profile and vulnerability analysis ---
    margin_profile: list[MarginRecord] = []
    vulnerable_queries: list[VulnerableQuery] = []

    for q_idx in range(m):
        original_margin = compute_signed_margin(sample, q_idx, k)
        original_prediction = predict_from_margin(original_margin)

        margin_profile.append(MarginRecord(
            query_point_idx=q_idx,
            perturbation_type="original",
            perturbation_index=None,
            margin=original_margin,
            prediction=original_prediction,
        ))

        # Check vulnerability: how close is the margin to the threshold?
        margin_gap = abs(original_margin)  # Distance from 0
        # The max change from flipping one neighbor label: 2 (from -1 to +1)
        # But if the neighbor is at distance > k-th neighbor, it may not be in top-k
        max_single_change = 2  # Applies if the flipped entry is in top-k

        # For k-NN specifically: if we replace the i-th occurrence with the
        # same point but flipped label, the margin changes by 2 if the
        # occurrence is in top-k (since contribution goes from -1 to +1).
        # More precisely, the margin change is exactly 2 * (2*y'_i - 1 - (2*y_i - 1))
        # which is 2 * (1 - (-1)) = 4 for a 0->1 flip and 2 * (-1 - 1) = -4 for 1->0 flip.
        # Actually: (2y'-1) - (2y-1) = 2(y'-y). When y=0,y'=1: 2(1-0)=2. Net margin change = 2.
        # When y=1,y'=0: 2(0-1)=-2. Net margin change = -2.
        # Absolute change = 2.

        is_vulnerable = margin_gap <= max_single_change and margin_gap > 0

        vulnerable_queries.append(VulnerableQuery(
            query_point_idx=q_idx,
            query_label=original_prediction,  # The current prediction
            original_margin=int(original_margin),
            margin_gap=int(margin_gap),
            max_single_change=max_single_change,
            is_vulnerable=bool(is_vulnerable),
        ))

    return DiagnosticResult(
        k=k,
        n_sample=n,
        n_metric=m,
        loo_profile=loo_profile,
        max_loo=int(max_loo),
        all_loo_zero=bool(all_loo_zero),
        delete_one_max=int(del_max),
        insert_one_max=int(ins_max),
        replace_one_max=int(rep_max),
        loo_rep_gap=int(loo_rep_gap),
        vulnerable_queries=vulnerable_queries,
        margin_profile=margin_profile,
    )


def format_diagnostic_report(result: DiagnosticResult) -> str:
    """Format a DiagnosticResult as a human-readable text report."""
    lines = [
        "=" * 60,
        "StabilityGapDiagnostic Report",
        "=" * 60,
        f"k = {result.k}, sample size = {result.n_sample}, metric space = {result.n_metric} points",
        "",
        "--- LOO Profile ---",
        f"Max LOO indicator: {result.max_loo}",
        f"All LOO zero: {result.all_loo_zero}",
        f"LOO profile: {result.loo_profile[:20]}{'...' if len(result.loo_profile) > 20 else ''}",
        "",
        "--- Instability Maxima ---",
        f"Max delete-one:   {result.delete_one_max}",
        f"Max insert-one:   {result.insert_one_max}",
        f"Max replace-one:  {result.replace_one_max}",
        f"LOO/Replace gap:  {result.loo_rep_gap}",
        "",
        "--- Vulnerable Queries ---",
    ]

    n_vuln = sum(1 for q in result.vulnerable_queries if q.is_vulnerable)
    lines.append(f"Total vulnerable: {n_vuln} / {len(result.vulnerable_queries)}")

    for q in result.vulnerable_queries:
        if q.is_vulnerable:
            lines.append(
                f"  Query idx {q.query_point_idx}: margin={q.original_margin}, "
                f"gap={q.margin_gap}, max_change={q.max_single_change}"
            )

    lines.extend([
        "",
        "--- Margin Profile (first 10) ---",
    ])

    for rec in result.margin_profile[:10]:
        lines.append(
            f"  Query {rec.query_point_idx}: {rec.perturbation_type} -> "
            f"margin={rec.margin}, predict={rec.prediction}"
        )

    if len(result.margin_profile) > 10:
        lines.append(f"  ... {len(result.margin_profile) - 10} more records")

    lines.append("=" * 60)
    return "\n".join(lines)


def find_margin_crossing_certificates(
    sample: LabeledSample,
    k: int,
) -> list[dict]:
    """Find margin-crossing certificates for replace-one perturbations.

    For each query and each replacement, check whether the perturbation
    causes the signed margin to cross zero. Returns all such certificates.
    """
    n = sample.n
    m = sample.metric.n
    certificates: list[dict] = []

    for rep_idx in range(n):
        orig_point = sample.point_indices[rep_idx]
        orig_label = sample.labels[rep_idx]

        for new_label in (0, 1):
            if new_label == orig_label:
                continue

            for q_idx in range(m):
                original_margin = compute_signed_margin(sample, q_idx, k)
                original_pred = predict_from_margin(original_margin)

                # Build replaced sample
                new_points = list(sample.point_indices)
                new_labels = list(sample.labels)
                new_points[rep_idx] = orig_point  # Same point, different label
                new_labels[rep_idx] = new_label

                replaced_sample = LabeledSample(
                    metric=sample.metric,
                    point_indices=tuple(new_points),
                    labels=tuple(new_labels),
                )

                new_margin = compute_signed_margin(replaced_sample, q_idx, k)
                new_pred = predict_from_margin(new_margin)

                if original_pred != new_pred:
                    certificates.append({
                        "query_point_idx": int(q_idx),
                        "replace_index": int(rep_idx),
                        "new_label": int(new_label),
                        "original_margin": int(original_margin),
                        "original_prediction": int(original_pred),
                        "new_margin": int(new_margin),
                        "new_prediction": int(new_pred),
                        "margin_change": int(new_margin - original_margin),
                    })

    return certificates


def summarize_diagnostic(result: DiagnosticResult) -> dict:
    """Produce a JSON-serializable summary of the diagnostic result."""
    return {
        "k": result.k,
        "n_sample": result.n_sample,
        "n_metric": result.n_metric,
        "max_loo": result.max_loo,
        "all_loo_zero": result.all_loo_zero,
        "delete_one_max": result.delete_one_max,
        "insert_one_max": result.insert_one_max,
        "replace_one_max": result.replace_one_max,
        "loo_rep_gap": result.loo_rep_gap,
        "n_vulnerable_queries": sum(1 for q in result.vulnerable_queries if q.is_vulnerable),
        "total_queries": len(result.vulnerable_queries),
    }
