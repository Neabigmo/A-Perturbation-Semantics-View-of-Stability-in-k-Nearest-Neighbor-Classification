"""Tests for deterministic k-NN classifier."""

import numpy as np
import pytest

from knn_stability.knn import (
    LabeledSample,
    predict_knn,
    predict_knn_even,
    predict_knn_odd,
)
from knn_stability.metrics import FiniteMetricSpace


class TestLabeledSample:
    """Test LabeledSample data structure."""

    def test_create_from_arrays(self):
        """Create sample from point indices and labels."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[[0, 1, 2], [1, 0, 1], [2, 1, 0]],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 1],
            metric=metric,
        )
        assert sample.n == 3
        assert sample.point_indices == (0, 1, 2)
        assert sample.labels == (0, 1, 1)

    def test_create_with_tuples(self):
        """Create sample with tuple inputs."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        sample = LabeledSample(
            metric=metric,
            point_indices=(0, 1, 0),
            labels=(1, 0, 1),
        )
        assert sample.n == 3

    def test_length(self):
        """Length is number of sample occurrences."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        sample = LabeledSample.from_arrays([0, 1], [0, 1], metric)
        assert len(sample) == 2

    def test_mismatched_lengths_raises(self):
        """Point indices and labels must have same length."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[[0, 1, 2], [1, 0, 1], [2, 1, 0]],
        )
        with pytest.raises(ValueError, match="same length"):
            LabeledSample.from_arrays([0, 1], [0, 1, 1], metric)

    def test_invalid_point_index_raises(self):
        """Point index outside metric space raises error."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        with pytest.raises(ValueError, match="outside metric space"):
            LabeledSample.from_arrays([0, 5], [0, 1], metric)

    def test_invalid_label_raises(self):
        """Labels must lie in the frozen binary label space {0, 1}."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        with pytest.raises(ValueError, match="binary label space"):
            LabeledSample.from_arrays([0, 1], [0, 2], metric)

    def test_duplicate_points_allowed(self):
        """Sample may contain the same point multiple times."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 0, 1],
            labels=[0, 1, 1],
            metric=metric,
        )
        assert sample.n == 3

    def test_get_labels_at_indices(self):
        """Extract labels for specific occurrence indices."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 0],
            labels=[0, 1, 1],
            metric=metric,
        )
        labels = sample.get_labels_at_indices([0, 2])
        np.testing.assert_array_equal(labels, [0, 1])

    def test_empty_sample(self):
        """Empty sample has length 0."""
        metric = FiniteMetricSpace(
            points=["a"],
            distances=[[0]],
        )
        sample = LabeledSample.from_arrays([], [], metric)
        assert len(sample) == 0


class TestPredictKnn:
    """Test k-NN prediction."""

    @pytest.fixture
    def line_metric(self):
        """Three points on a line: 0 -- 1 -- 2."""
        return FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[
                [0.0, 1.0, 2.0],
                [1.0, 0.0, 1.0],
                [2.0, 1.0, 0.0],
            ],
        )

    def test_k1_predicts_nearest_neighbor_label(self, line_metric):
        """k=1 returns the label of the closest sample occurrence."""
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 0],
            metric=line_metric,
        )
        # Query at point 2: self is present in the sample at distance 0.
        assert predict_knn(sample, query_point_idx=2, k=1) == 0
        # Query at point 0: closest is point 0 (dist 0) with label 0
        assert predict_knn(sample, query_point_idx=0, k=1) == 0

    def test_k1_with_training_point_as_query(self, line_metric):
        """Query point that is in the training sample uses its own label for k=1."""
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 0],
            metric=line_metric,
        )
        # Query at point 0: self is closest (dist 0) with label 0
        assert predict_knn(sample, query_point_idx=0, k=1) == 0
        # Query at point 1: self is closest (dist 0) with label 1
        assert predict_knn(sample, query_point_idx=1, k=1) == 1

    def test_k3_with_odd_majority(self, line_metric):
        """k=3 odd majority resolves correctly."""
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 1],
            metric=line_metric,
        )
        # Query at point 0: neighbors are 0,1,2 with labels [0,1,1]
        # Majority is label 1 (2 votes vs 1)
        assert predict_knn(sample, query_point_idx=0, k=3) == 1

    def test_k3_with_even_tie_breaks_to_0(self, line_metric):
        """k=3 with label tie breaks to 0 (0 ≺ 1)."""
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 0],
            metric=line_metric,
        )
        # Query at point 0: neighbors are 0,1,2 with labels [0,1,0]
        # Tie: 2 zeros, 1 one -> returns 0
        assert predict_knn(sample, query_point_idx=0, k=3) == 0


class TestDistanceTies:
    """Test distance tie-breaking by index."""

    def test_distance_tie_at_k_boundary(self):
        """Tie-breaking at k boundary when distance ties exist."""
        # Triangle: all points distance 1 from each other
        metric = FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[
                [0.0, 1.0, 1.0],
                [1.0, 0.0, 1.0],
                [1.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[1, 0, 0],
            metric=metric,
        )
        # Query at point 0: self is selected first at distance 0.
        assert predict_knn(sample, query_point_idx=0, k=1) == 1

    def test_distance_tie_multiple_at_same_distance(self):
        """Multiple points at same distance use occurrence index ordering."""
        # Four points: query at 0, points 1,2,3 all at distance 2
        metric = FiniteMetricSpace(
            points=["q", "a", "b", "c"],
            distances=[
                [0.0, 2.0, 2.0, 2.0],
                [2.0, 0.0, 1.0, 1.0],
                [2.0, 1.0, 0.0, 1.0],
                [2.0, 1.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2, 3],
            labels=[0, 1, 1, 1],
            metric=metric,
        )
        # Query at point 0: self is first at distance 0, then occurrence 1 at distance 2.
        # Labels are [0, 1], so the vote ties and resolves to 0.
        assert predict_knn(sample, query_point_idx=0, k=2) == 0

    def test_distance_tie_at_3nn_boundary(self):
        """k=3 with distance tie at third position."""
        metric = FiniteMetricSpace(
            points=["q", "a", "b", "c"],
            distances=[
                [0.0, 1.0, 1.0, 2.0],
                [1.0, 0.0, 1.0, 1.0],
                [1.0, 1.0, 0.0, 1.0],
                [2.0, 1.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2, 3],
            labels=[0, 0, 1, 0],
            metric=metric,
        )
        # Query at point 0: k=3 selects occurrences 0,1,2 with labels [0,0,1].
        assert predict_knn(sample, query_point_idx=0, k=3) == 0


class TestLabelTies:
    """Test label vote tie-breaking (0 ≺ 1)."""

    def test_even_k_label_tie(self):
        """Even k with label tie breaks to 0."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c", "d"],
            distances=[
                [0.0, 1.0, 1.0, 2.0],
                [1.0, 0.0, 1.0, 1.0],
                [1.0, 1.0, 0.0, 1.0],
                [2.0, 1.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2, 3],
            labels=[0, 1, 0, 1],
            metric=metric,
        )
        # Query at point 0: k=2 neighbors should have labels [0,1] -> tie -> 0
        assert predict_knn(sample, query_point_idx=0, k=2) == 0

    def test_odd_k_label_tie_at_boundary(self):
        """Odd k with tie at k boundary."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c", "d"],
            distances=[
                [0.0, 1.0, 1.0, 1.0],
                [1.0, 0.0, 1.0, 1.0],
                [1.0, 1.0, 0.0, 1.0],
                [1.0, 1.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2, 3],
            labels=[0, 0, 1, 1],
            metric=metric,
        )
        # Query at point 0: self is first, then the distance-1 occurrences by index.
        # k=3 selects labels [0,0,1] -> majority 0.
        assert predict_knn(sample, query_point_idx=0, k=3) == 0

    def test_strict_majority_label_1_wins(self):
        """Strict majority for label 1 correctly returns 1."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[
                [0.0, 1.0, 2.0],
                [1.0, 0.0, 1.0],
                [2.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 1],
            metric=metric,
        )
        # Query at point 0: k=3 -> labels [0,1,1] -> majority 1
        assert predict_knn(sample, query_point_idx=0, k=3) == 1


class TestTrainingPointQueries:
    """Test query points that are in the training sample."""

    def test_query_at_exact_training_point(self):
        """Query at a training point's location."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[
                [0.0, 1.0, 2.0],
                [1.0, 0.0, 1.0],
                [2.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 0],
            metric=metric,
        )
        # Query at point 1 (which is in sample at index 1)
        # For k=1: self is closest (dist 0) -> label 1
        assert predict_knn(sample, query_point_idx=1, k=1) == 1

    def test_query_at_training_point_with_k_greater_than_1(self):
        """Query at training point with k>1 includes self as neighbor."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[
                [0.0, 1.0, 2.0],
                [1.0, 0.0, 1.0],
                [2.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 1],
            metric=metric,
        )
        # Query at point 1: k=3 includes self and both distance-1 neighbors.
        # The labels are [1, 0, 1], so label 1 has a strict majority.
        assert predict_knn(sample, query_point_idx=1, k=3) == 1

    def test_query_at_duplicate_training_point(self):
        """Query at a point that appears multiple times in sample."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[
                [0.0, 1.0],
                [1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 0, 1],
            labels=[0, 1, 0],
            metric=metric,
        )
        # Query at point 0: k=1 -> self at dist 0
        # Both copies of point 0 are at distance 0
        # Tie-breaking picks lower occurrence index (0) -> label 0
        assert predict_knn(sample, query_point_idx=0, k=1) == 0


class TestPredictOddAndEven:
    """Test convenience functions for odd/even k."""

    def test_predict_knn_odd(self):
        """predict_knn_odd uses k=1."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[
                [0.0, 1.0, 2.0],
                [1.0, 0.0, 1.0],
                [2.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 0],
            metric=metric,
        )
        assert predict_knn_odd(sample, query_point_idx=2) == 0

    def test_predict_knn_even(self):
        """predict_knn_even uses k=2."""
        metric = FiniteMetricSpace(
            points=["a", "b", "c"],
            distances=[
                [0.0, 1.0, 2.0],
                [1.0, 0.0, 1.0],
                [2.0, 1.0, 0.0],
            ],
        )
        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 0],
            metric=metric,
        )
        # k=2: neighbors 0,1 with labels [0,1] -> tie -> 0
        assert predict_knn_even(sample, query_point_idx=0) == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_k_less_than_1_raises(self):
        """k < 1 raises ValueError."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        sample = LabeledSample.from_arrays([0, 1], [0, 1], metric)
        with pytest.raises(ValueError, match="at least 1"):
            predict_knn(sample, query_point_idx=0, k=0)

    def test_k_exceeds_sample_size_raises(self):
        """k > sample size raises ValueError."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        sample = LabeledSample.from_arrays([0, 1], [0, 1], metric)
        with pytest.raises(ValueError, match="exceeds sample size"):
            predict_knn(sample, query_point_idx=0, k=3)

    def test_query_out_of_bounds_raises(self):
        """Query point index out of metric space raises ValueError."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        sample = LabeledSample.from_arrays([0, 1], [0, 1], metric)
        with pytest.raises(ValueError, match="out of bounds"):
            predict_knn(sample, query_point_idx=5, k=1)

    def test_single_sample_point(self):
        """Single sample point works with k=1."""
        metric = FiniteMetricSpace(
            points=["a", "b"],
            distances=[[0, 1], [1, 0]],
        )
        sample = LabeledSample.from_arrays([1], [1], metric)
        assert predict_knn(sample, query_point_idx=0, k=1) == 1


class TestIntegration:
    """Integration tests for complete prediction pipeline."""

    def test_graph_metric_prediction(self):
        """k-NN prediction on a graph shortest-path metric."""
        from knn_stability.graph_metrics import adjacency_to_graph_metric

        # Triangle graph: 0 -- 1 -- 2 -- 0
        adjacency = {0: {1, 2}, 1: {0, 2}, 2: {0, 1}}
        metric = adjacency_to_graph_metric(adjacency)

        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2],
            labels=[0, 1, 1],
            metric=metric,
        )

        # All distances are 1 in triangle
        # k=2: picks neighbors by index order -> labels [0,1] -> tie -> 0
        assert predict_knn(sample, query_point_idx=0, k=2) == 0
        # k=3: labels [0,1,1] -> majority 1
        assert predict_knn(sample, query_point_idx=0, k=3) == 1

    def test_path_graph(self):
        """k-NN prediction on a path graph."""
        from knn_stability.graph_metrics import adjacency_to_graph_metric

        # Path: 0 -- 1 -- 2 -- 3
        adjacency = {0: {1}, 1: {0, 2}, 2: {1, 3}, 3: {2}}
        metric = adjacency_to_graph_metric(adjacency)

        sample = LabeledSample.from_arrays(
            point_indices=[0, 1, 2, 3],
            labels=[0, 0, 1, 1],
            metric=metric,
        )

        # Query at endpoint 0: k=3 selects occurrences 0,1,2 with labels [0,0,1].
        assert predict_knn(sample, query_point_idx=0, k=3) == 0


def test_module_docstring() -> None:
    """Verify module docstring references frozen spec."""
    from knn_stability import knn

    assert "02_DEFINITIONS_SPEC" in knn.__doc__
    assert "0 ≺ 1" in knn.__doc__ or "0 \\prec 1" in knn.__doc__
