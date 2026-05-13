"""Finite metric-space primitives."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


class FiniteMetricSpace:
    """A finite metric space represented by indexed points and a distance matrix."""

    _TRIANGLE_TOLERANCE = 1e-10

    def __init__(self, points: ArrayLike, distances: ArrayLike) -> None:
        self.points = tuple(points)
        self.distances = np.asarray(distances, dtype=np.float64)
        if self.distances.size == 0:
            self.distances = np.zeros((0, 0), dtype=np.float64)
        self._validate()
        self._n = len(self.points)

    def _validate(self) -> None:
        """Validate the distance matrix satisfies metric axioms."""
        self._validate_square()
        self._validate_point_count()
        self._validate_symmetry()
        self._validate_non_negative()
        self._validate_zero_diagonal()
        self._validate_positive_off_diagonal()
        self._validate_triangle_inequality()

    def _validate_square(self) -> None:
        """Check that distance matrix is square."""
        if self.distances.ndim != 2:
            raise ValueError(
                f"Distance matrix must be 2-dimensional, got shape {self.distances.shape}"
            )
        n, m = self.distances.shape
        if n != m:
            raise ValueError(
                f"Distance matrix must be square, got shape {self.distances.shape}"
            )

    def _validate_point_count(self) -> None:
        """Check that the matrix dimension matches the number of points."""
        matrix_size = self.distances.shape[0]
        if matrix_size != len(self.points):
            raise ValueError(
                "Distance matrix dimension must match number of points, "
                f"got {matrix_size} distances for {len(self.points)} points"
            )

    def _validate_symmetry(self) -> None:
        """Check that distance matrix is symmetric."""
        if not np.allclose(self.distances, self.distances.T):
            raise ValueError("Distance matrix must be symmetric (d[i,j] = d[j,i])")

    def _validate_non_negative(self) -> None:
        """Check that all distances are non-negative."""
        if np.any(self.distances < 0):
            raise ValueError("All distances must be non-negative")

    def _validate_zero_diagonal(self) -> None:
        """Check that diagonal entries are zero."""
        diagonal = np.diag(self.distances)
        if not np.allclose(diagonal, 0):
            raise ValueError(
                f"Diagonal entries must be zero, got diagonal values: {diagonal}"
            )

    def _validate_positive_off_diagonal(self) -> None:
        """Check that distinct points have strictly positive distance."""
        if self.distances.shape[0] <= 1:
            return
        off_diagonal = self.distances[~np.eye(self.distances.shape[0], dtype=bool)]
        if np.any(off_diagonal <= 0):
            raise ValueError("Distances between distinct points must be strictly positive")

    def _validate_triangle_inequality(self) -> None:
        """Check that triangle inequality holds: d(x,z) <= d(x,y) + d(y,z) for all x,y,z."""
        n = self.distances.shape[0]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    if (
                        self.distances[i, j] + self.distances[j, k]
                        < self.distances[i, k] - self._TRIANGLE_TOLERANCE
                    ):
                        raise ValueError(
                            f"Triangle inequality violated: d({i},{k}) = {self.distances[i, k]} "
                            f"> d({i},{j}) + d({j},{k}) = {self.distances[i, j]} + {self.distances[j, k]}"
                        )

    @property
    def n(self) -> int:
        """Number of points in the metric space."""
        return self._n

    def d(self, i: int, j: int) -> float:
        """Return the distance between points i and j.

        Parameters
        ----------
        i : int
            Index of first point
        j : int
            Index of second point

        Returns
        -------
        float
            Distance between points i and j
        """
        return float(self.distances[i, j])

    def __repr__(self) -> str:
        return f"FiniteMetricSpace(n={self.n})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FiniteMetricSpace):
            return False
        return self.points == other.points and np.allclose(self.distances, other.distances)


def is_valid_metric(distances: ArrayLike) -> bool:
    """Check if a distance matrix is a valid metric.

    Parameters
    ----------
    distances : ArrayLike
        A potential distance matrix

    Returns
    -------
    bool
        True if the matrix is a valid metric, False otherwise
    """
    try:
        matrix = np.asarray(distances, dtype=np.float64)
        if matrix.size == 0:
            _ = FiniteMetricSpace([], [])
        else:
            if matrix.ndim != 2:
                return False
            _ = FiniteMetricSpace(range(matrix.shape[0]), matrix)
        return True
    except ValueError:
        return False
