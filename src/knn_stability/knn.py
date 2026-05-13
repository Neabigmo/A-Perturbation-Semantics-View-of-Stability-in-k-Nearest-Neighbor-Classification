"""Deterministic k-nearest-neighbor classifier.

Implements the frozen k-NN prediction rule from:
docs/project-control/02_DEFINITIONS_SPEC.md

The sample S = ((x_1, y_1), ..., (x_n, y_n)) is an ordered tuple.
Neighbor ordering is lexicographic by:
1. smaller distance to the query point
2. smaller sample index

Label vote ties are resolved by fixed label order: 0 ≺ 1
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from knn_stability.metrics import FiniteMetricSpace
from knn_stability.tie_breaking import select_k_neighbors, compute_majority_vote


@dataclass
class LabeledSample:
    """An ordered tuple of labeled sample occurrences.

    Attributes
    ----------
    metric : FiniteMetricSpace
        The finite metric space (X, d).
    point_indices : tuple[int, ...]
        The i-th element is the metric-space index of x_i in sample S.
        Duplicates are allowed and remain distinct.
    labels : tuple[int, ...]
        The i-th element is the label y_i in sample S.
        Must have same length as point_indices.
    """

    metric: FiniteMetricSpace
    point_indices: tuple[int, ...]
    labels: tuple[int, ...]

    def __post_init__(self) -> None:
        """Validate the sample structure."""
        n = len(self.point_indices)
        if len(self.labels) != n:
            raise ValueError(
                f"point_indices and labels must have same length, "
                f"got {n} and {len(self.labels)}"
            )

        if self.metric.n == 0:
            return

        for idx in self.point_indices:
            if idx < 0 or idx >= self.metric.n:
                raise ValueError(
                    f"Sample contains point index {idx} outside metric space "
                    f"of size {self.metric.n}"
                )

        for label in self.labels:
            if label not in (0, 1):
                raise ValueError(
                    f"Sample contains label {label} outside binary label space {{0, 1}}"
                )

    @classmethod
    def from_arrays(
        cls,
        point_indices: ArrayLike,
        labels: ArrayLike,
        metric: FiniteMetricSpace,
    ) -> LabeledSample:
        """Create a LabeledSample from arrays.

        Parameters
        ----------
        point_indices : ArrayLike
            Sequence of metric-space point indices.
        labels : ArrayLike
            Sequence of binary labels (0 or 1).
        metric : FiniteMetricSpace
            The metric space.

        Returns
        -------
        LabeledSample
            A new labeled sample.
        """
        return cls(
            metric=metric,
            point_indices=tuple(np.asarray(point_indices, dtype=np.int64).flatten()),
            labels=tuple(np.asarray(labels, dtype=np.int64).flatten()),
        )

    def __len__(self) -> int:
        """Number of sample occurrences."""
        return len(self.point_indices)

    @property
    def n(self) -> int:
        """Number of sample occurrences (alias for len)."""
        return len(self)

    def get_labels_at_indices(self, occurrence_indices: ArrayLike) -> np.ndarray:
        """Get labels for sample occurrence indices.

        Parameters
        ----------
        occurrence_indices : ArrayLike
            Indices into this sample's occurrence ordering.

        Returns
        -------
        np.ndarray
            Array of labels for those occurrence indices.
        """
        indices = np.asarray(occurrence_indices, dtype=np.int64)
        return np.array([self.labels[i] for i in indices], dtype=np.int64)


def predict_knn(
    sample: LabeledSample,
    query_point_idx: int,
    k: int,
) -> int:
    """Predict the label for a query point using k-NN.

    Parameters
    ----------
    sample : LabeledSample
        The ordered training sample S = ((x_1, y_1), ..., (x_n, y_n)).
    query_point_idx : int
        Index of the query point in the metric space.
    k : int
        Number of nearest neighbors to use. Must satisfy 1 <= k <= sample.n.

    Returns
    -------
    int
        The predicted label (0 or 1).

    Raises
    ------
    ValueError
        If k is out of valid range or query point is invalid.

    Notes
    -----
    Prediction follows the frozen definition:
    1. Order neighbors by (distance to query, occurrence index)
    2. Select first k neighbors
    3. Majority vote of their labels
    4. Label ties broken in favor of 0 (0 ≺ 1)

    The query point may be a training point. If the query point's occurrence
    is in the sample, it is treated like any other neighbor.
    """
    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")
    if k > sample.n:
        raise ValueError(f"k={k} exceeds sample size {sample.n}")

    if query_point_idx < 0 or query_point_idx >= sample.metric.n:
        raise ValueError(
            f"query_point_idx {query_point_idx} out of bounds for metric "
            f"space of size {sample.metric.n}"
        )

    neighbor_occurrences = select_k_neighbors(
        query_point_idx=query_point_idx,
        sample_point_indices=np.array(sample.point_indices),
        distances=sample.metric.distances,
        k=k,
    )

    neighbor_labels = sample.get_labels_at_indices(neighbor_occurrences)

    return compute_majority_vote(neighbor_labels)


def predict_knn_odd(sample: LabeledSample, query_point_idx: int) -> int:
    """Predict using k=1 (1-NN).

    Parameters
    ----------
    sample : LabeledSample
        The training sample.
    query_point_idx : int
        Index of the query point.

    Returns
    -------
    int
        The predicted label (label of nearest neighbor).
    """
    return predict_knn(sample, query_point_idx, k=1)


def predict_knn_even(sample: LabeledSample, query_point_idx: int) -> int:
    """Predict using k=2 (2-NN).

    Parameters
    ----------
    sample : LabeledSample
        The training sample.
    query_point_idx : int
        Index of the query point.

    Returns
    -------
    int
        The predicted label.
    """
    return predict_knn(sample, query_point_idx, k=2)
