"""Tests for finite metric space implementation."""

import numpy as np
import pytest

from knn_stability.metrics import FiniteMetricSpace, is_valid_metric


class TestFiniteMetricSpaceBasic:
    """Test basic construction and properties."""

    def test_empty_space(self):
        """Empty space is valid."""
        fms = FiniteMetricSpace([], [])
        assert fms.n == 0

    def test_single_point(self):
        """Single point with zero distance to itself."""
        points = ["a"]
        distances = [[0.0]]
        fms = FiniteMetricSpace(points, distances)
        assert fms.n == 1
        assert fms.d(0, 0) == 0.0

    def test_two_points(self):
        """Two points with symmetric positive distance."""
        points = ["a", "b"]
        distances = [[0.0, 1.0], [1.0, 0.0]]
        fms = FiniteMetricSpace(points, distances)
        assert fms.n == 2
        assert fms.d(0, 1) == 1.0
        assert fms.d(1, 0) == 1.0


class TestFiniteMetricSpaceValidation:
    """Test validation of metric properties."""

    def test_point_count_mismatch_rejected(self):
        """Matrix dimension must match the number of points."""
        with pytest.raises(ValueError, match="must match number of points"):
            FiniteMetricSpace(["a"], [[0.0, 1.0], [1.0, 0.0]])

    def test_non_square_matrix_rejected(self):
        """Non-square matrices are rejected."""
        with pytest.raises(ValueError, match="must be square"):
            FiniteMetricSpace(["a", "b"], [[0, 1], [1, 0], [0, 1]])

    def test_non_symmetric_matrix_rejected(self):
        """Non-symmetric matrices are rejected."""
        with pytest.raises(ValueError, match="must be symmetric"):
            FiniteMetricSpace(["a", "b"], [[0, 1], [2, 0]])

    def test_negative_distance_rejected(self):
        """Negative distances are rejected."""
        with pytest.raises(ValueError, match="non-negative"):
            FiniteMetricSpace(["a", "b"], [[0, -1], [-1, 0]])

    def test_non_zero_diagonal_rejected(self):
        """Non-zero diagonal entries are rejected."""
        with pytest.raises(ValueError, match="Diagonal entries must be zero"):
            FiniteMetricSpace(["a", "b"], [[1, 0], [0, 0]])

    def test_zero_off_diagonal_rejected(self):
        """Distinct points must have strictly positive distance."""
        with pytest.raises(ValueError, match="strictly positive"):
            FiniteMetricSpace(["a", "b"], [[0.0, 0.0], [0.0, 0.0]])

    def test_triangle_inequality_violation_rejected(self):
        """Triangle inequality violations are rejected."""
        # Points a, b, c where d(a,b) + d(b,c) < d(a,c)
        # This is a violation: 0.5 + 0.5 < 2.0 is False if we set d(a,c)=2.0
        distances = [[0, 0.5, 1.5], [0.5, 0, 0.5], [1.5, 0.5, 0]]
        with pytest.raises(ValueError, match="Triangle inequality violated"):
            FiniteMetricSpace(["a", "b", "c"], distances)

    def test_valid_triangle_inequality_accepted(self):
        """Valid triangle inequalities are accepted."""
        # Euclidean distances for points at vertices of equilateral triangle
        distances = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
        fms = FiniteMetricSpace(["a", "b", "c"], distances)
        assert fms.n == 3


class TestFiniteMetricSpaceEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_integer_distances(self):
        """Integer distance matrices are accepted."""
        distances = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
        fms = FiniteMetricSpace([0, 1, 2], distances)
        assert fms.d(0, 1) == 1.0

    def test_float32_input(self):
        """Float32 input is accepted and converted."""
        distances = np.array([[0, 1], [1, 0]], dtype=np.float32)
        fms = FiniteMetricSpace([0, 1], distances)
        assert fms.distances.dtype == np.float64

    def test_one_dimensional_matrix_rejected(self):
        """1D array is not a valid distance matrix."""
        with pytest.raises(ValueError, match="2-dimensional"):
            FiniteMetricSpace([0, 1], [0, 1, 1, 0])

    def test_three_dimensional_matrix_rejected(self):
        """3D array is not a valid distance matrix."""
        with pytest.raises(ValueError, match="2-dimensional"):
            FiniteMetricSpace([0, 1], [[[0, 1], [1, 0]], [[0, 1], [1, 0]]])


class TestIsValidMetric:
    """Test the is_valid_metric helper function."""

    def test_valid_metric_returns_true(self):
        """Valid metric returns True."""
        distances = [[0, 1], [1, 0]]
        assert is_valid_metric(distances) is True

    def test_invalid_metric_returns_false(self):
        """Invalid metric returns False."""
        distances = [[0, -1], [-1, 0]]
        assert is_valid_metric(distances) is False

    def test_non_square_returns_false(self):
        """Non-square matrix returns False."""
        distances = [[0, 1], [1, 0], [0, 1]]
        assert is_valid_metric(distances) is False


class TestFiniteMetricSpaceRepr:
    """Test string representation."""

    def test_repr(self):
        """Repr shows number of points."""
        fms = FiniteMetricSpace([0, 1, 2], [[0, 1, 1], [1, 0, 1], [1, 1, 0]])
        assert "FiniteMetricSpace" in repr(fms)
        assert "n=3" in repr(fms)


class TestEquality:
    """Test equality comparison."""

    def test_equal_spaces(self):
        """Identical distance matrices are equal."""
        fms1 = FiniteMetricSpace([0, 1], [[0, 1], [1, 0]])
        fms2 = FiniteMetricSpace([0, 1], [[0, 1], [1, 0]])
        assert fms1 == fms2

    def test_different_points_not_equal(self):
        """Equality tracks both points and distances."""
        fms1 = FiniteMetricSpace([0, 1], [[0, 1], [1, 0]])
        fms2 = FiniteMetricSpace(["a", "b"], [[0, 1], [1, 0]])
        assert fms1 != fms2

    def test_different_spaces(self):
        """Different distance matrices are not equal."""
        fms1 = FiniteMetricSpace([0, 1], [[0, 1], [1, 0]])
        fms2 = FiniteMetricSpace([0, 1], [[0, 2], [2, 0]])
        assert fms1 != fms2

    def test_equality_with_non_fms(self):
        """FMS is not equal to non-FMS objects."""
        fms = FiniteMetricSpace([0, 1], [[0, 1], [1, 0]])
        assert (fms == "not an fms") is False
        assert (fms == 42) is False


def test_metrics_module_imports() -> None:
    import knn_stability.metrics  # noqa: F401
