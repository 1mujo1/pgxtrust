"""Simulation-based precision check for the H1 drift penalty (protocol section 6, gate G2).

Plain-language summary: we pretend we already know the truth (models are, say, 15 percentage
points worse on recommendations that changed between CPIC releases), generate many fake studies
with exactly our item structure, and ask how wide the 95% confidence interval would be. A wide
interval means the real study could not distinguish a big effect from a small one.

Why a *cluster* bootstrap: items from the same gene-drug pair (e.g. 43 thiopurine rows for one
drug) tend to be right or wrong together, so they are not independent. We therefore resample
whole clusters, not single items. Within-cluster similarity is simulated with a random effect
``u_j ~ Normal(0, cluster_sd)`` on the log-odds scale shared by all items of cluster ``j``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


def _logit(p: float) -> float:
    return math.log(p / (1 - p))


def _expit(x: float) -> float:
    return 1 / (1 + math.exp(-x))


@dataclass(frozen=True)
class ClusterCounts:
    """Correct/total counts for one cluster, for changed and matched unchanged items."""

    changed_correct: int
    changed_total: int
    unchanged_correct: int
    unchanged_total: int


def simulate_study(
    cluster_sizes: list[int],
    p_unchanged: float,
    p_changed: float,
    cluster_sd: float,
    rng: random.Random,
    penalty_sd: float = 0.0,
) -> list[ClusterCounts]:
    """One fake study: each cluster has n changed items and n matched unchanged items (1:1).

    ``cluster_sd`` shifts changed and unchanged items of a cluster together (it cancels out of
    the difference). ``penalty_sd`` adds an extra effect to the *changed* items only, so the
    drift penalty itself varies between gene-drug pairs; this is the variance that makes the
    cluster bootstrap of the penalty wide.
    """
    base_u, base_c = _logit(p_unchanged), _logit(p_changed)
    study = []
    for n in cluster_sizes:
        u = rng.gauss(0.0, cluster_sd) if cluster_sd > 0 else 0.0
        v = rng.gauss(0.0, penalty_sd) if penalty_sd > 0 else 0.0
        pu, pc = _expit(base_u + u), _expit(base_c + u + v)
        study.append(
            ClusterCounts(
                changed_correct=sum(rng.random() < pc for _ in range(n)),
                changed_total=n,
                unchanged_correct=sum(rng.random() < pu for _ in range(n)),
                unchanged_total=n,
            )
        )
    return study


def drift_penalty(clusters: list[ClusterCounts]) -> float:
    """acc(unchanged) - acc(changed), pooled over items (the H1 effect)."""
    cc = sum(c.changed_correct for c in clusters)
    ct = sum(c.changed_total for c in clusters)
    uc = sum(c.unchanged_correct for c in clusters)
    ut = sum(c.unchanged_total for c in clusters)
    return uc / ut - cc / ct


def cluster_bootstrap_ci(
    clusters: list[ClusterCounts], n_boot: int, rng: random.Random, level: float = 0.95
) -> tuple[float, float]:
    """Percentile CI for the drift penalty, resampling whole clusters with replacement."""
    k = len(clusters)
    stats = sorted(drift_penalty([clusters[rng.randrange(k)] for _ in range(k)])
                   for _ in range(n_boot))
    lo_i = int((1 - level) / 2 * n_boot)
    hi_i = int((1 + level) / 2 * n_boot) - 1
    return stats[lo_i], stats[hi_i]


@dataclass(frozen=True)
class PowerResult:
    mean_half_width: float
    share_lower_bound_above_zero: float  # how often H1's pre-registered test would succeed
    mean_estimate: float


def expected_precision(
    cluster_sizes: list[int],
    p_unchanged: float = 0.80,
    p_changed: float = 0.65,
    cluster_sd: float = 1.0,
    n_sims: int = 200,
    n_boot: int = 1000,
    seed: int = 20261009,
    penalty_sd: float = 0.0,
) -> PowerResult:
    """Average CI half-width and success rate over `n_sims` simulated studies."""
    rng = random.Random(seed)
    half_widths, successes, estimates = [], 0, []
    for _ in range(n_sims):
        study = simulate_study(cluster_sizes, p_unchanged, p_changed, cluster_sd, rng,
                               penalty_sd=penalty_sd)
        lo, hi = cluster_bootstrap_ci(study, n_boot, rng)
        half_widths.append((hi - lo) / 2)
        successes += lo > 0
        estimates.append(drift_penalty(study))
    return PowerResult(
        mean_half_width=sum(half_widths) / n_sims,
        share_lower_bound_above_zero=successes / n_sims,
        mean_estimate=sum(estimates) / n_sims,
    )
