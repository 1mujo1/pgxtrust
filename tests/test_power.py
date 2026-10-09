"""Sanity tests for the G2 precision simulation (synthetic inputs only)."""

from __future__ import annotations

import random

from pgxtrust.power import (
    ClusterCounts,
    cluster_bootstrap_ci,
    drift_penalty,
    expected_precision,
    simulate_study,
)


def test_drift_penalty_is_pooled_difference():
    clusters = [ClusterCounts(5, 10, 8, 10), ClusterCounts(1, 10, 6, 10)]
    assert drift_penalty(clusters) == (14 / 20) - (6 / 20)


def test_simulation_is_reproducible_with_seed():
    a = expected_precision([10, 10, 10], n_sims=5, n_boot=50, seed=1)
    b = expected_precision([10, 10, 10], n_sims=5, n_boot=50, seed=1)
    assert a == b


def test_more_clusters_give_narrower_intervals():
    few = expected_precision([60] * 4, n_sims=40, n_boot=300, seed=3)
    many = expected_precision([10] * 24, n_sims=40, n_boot=300, seed=3)
    assert many.mean_half_width < few.mean_half_width


def test_no_effect_rarely_clears_zero():
    result = expected_precision([20] * 20, p_unchanged=0.7, p_changed=0.7,
                                n_sims=60, n_boot=300, seed=5)
    assert result.share_lower_bound_above_zero <= 0.15
    assert abs(result.mean_estimate) < 0.05


def test_penalty_heterogeneity_widens_intervals():
    # Regression test for the G2 modelling flaw: a shared cluster effect cancels out of the
    # difference, so only between-cluster variation of the *penalty* should widen the CI.
    sizes = [43, 38, 34, 30, 16, 16, 14, 5, 5, 5]
    homogeneous = expected_precision(sizes, penalty_sd=0.0, n_sims=40, n_boot=300, seed=9)
    heterogeneous = expected_precision(sizes, penalty_sd=1.0, n_sims=40, n_boot=300, seed=9)
    assert heterogeneous.mean_half_width > homogeneous.mean_half_width * 1.3


def test_bootstrap_ci_contains_point_estimate():
    rng = random.Random(7)
    study = simulate_study([15] * 12, 0.8, 0.65, 0.5, rng)
    lo, hi = cluster_bootstrap_ci(study, 500, rng)
    assert lo <= drift_penalty(study) <= hi
