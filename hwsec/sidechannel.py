"""Hamming-weight power leakage model, for studying countermeasures.

Everything here is a simulation on synthetic data. It models how strongly a
power trace follows the Hamming weight of processed values, which is the
quantity a designer wants to drive down with masking or hiding.
"""

from __future__ import annotations

import math

import numpy as np


def hamming_weight(values) -> np.ndarray:
    """Number of set bits in each (non-negative) integer."""
    arr = np.asarray(values, dtype=np.uint64)
    counts = np.zeros(arr.shape, dtype=np.int64)
    while arr.any():
        counts += (arr & np.uint64(1)).astype(np.int64)
        arr = arr >> np.uint64(1)
    return counts


def simulate_power_trace(
    operations: int,
    data_width: int = 16,
    noise_sigma: float = 0.5,
    seed: int | None = None,
) -> dict[str, np.ndarray]:
    """Simulate one power sample per operation: Hamming weight + Gaussian noise."""
    if operations < 2:
        raise ValueError("need at least 2 operations")
    if not 1 <= data_width <= 63:
        raise ValueError("data_width must be between 1 and 63 bits")
    if noise_sigma < 0:
        raise ValueError("noise_sigma must be >= 0")
    rng = np.random.default_rng(seed)
    intermediates = rng.integers(0, 2**data_width, size=operations, dtype=np.uint64)
    hw = hamming_weight(intermediates)
    power = hw + rng.normal(0.0, noise_sigma, size=operations)
    return {"intermediates": intermediates, "hamming_weight": hw, "power": power}


def leakage_correlation(hamming_weights, power) -> float:
    """Pearson correlation between the leakage model and the measured trace."""
    hw = np.asarray(hamming_weights, dtype=float)
    p = np.asarray(power, dtype=float)
    if hw.shape != p.shape or hw.size < 2:
        raise ValueError("inputs must have the same length (>= 2)")
    if hw.std() == 0 or p.std() == 0:
        return 0.0
    return float(np.corrcoef(hw, p)[0, 1])


def expected_correlation(data_width: int, noise_sigma: float) -> float:
    """Theoretical correlation for uniform data: signal variance is width / 4."""
    signal_var = data_width / 4.0
    return math.sqrt(signal_var / (signal_var + noise_sigma**2))


def traces_needed(correlation: float, confidence_z: float = 3.719) -> float:
    """Rule-of-thumb number of traces to detect a correlation of this size.

    N ~ 3 + 8 * (z / ln((1 + r) / (1 - r)))^2 (Mangard et al.). A larger number
    means the design leaks less; ``inf`` means no detectable leakage.
    """
    r = abs(correlation)
    if r >= 1.0:
        return 3.0
    if r == 0.0:
        return math.inf
    return 3.0 + 8.0 * (confidence_z / math.log((1.0 + r) / (1.0 - r))) ** 2
