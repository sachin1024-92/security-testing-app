"""Hamming-weight power leakage model, for studying countermeasures.

Everything here is a simulation on synthetic data. It models how strongly a
power trace follows the Hamming weight of processed values, which is the
quantity a designer wants to drive down with masking or hiding. Hiding is modelled
as added noise, masking as first-order Boolean masking with two shares.
"""

from __future__ import annotations

import math

import numpy as np


def hamming_weight(values) -> np.ndarray:
    """Number of set bits in each (non-negative) integer."""
    raw = np.asarray(values)
    if raw.size == 0:
        return np.zeros(raw.shape, dtype=np.int64)
    if raw.dtype.kind not in "iub":
        raise ValueError("values must be whole numbers")
    if raw.min() < 0:
        raise ValueError("values must not be negative")
    arr = raw.astype(np.uint64)
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
    masked: bool = False,
) -> dict[str, np.ndarray]:
    """Simulate one power sample per operation: Hamming weight + Gaussian noise.

    With ``masked=True`` the device applies first-order Boolean masking: each value
    ``v`` is split into two shares ``v ^ m`` and ``m`` with a fresh random mask ``m``,
    and the sample is ``HW(v ^ m) + HW(m) + noise``. The mean of that sample no longer
    depends on ``v``, but its spread still does (see ``second_order_correlation``).
    ``hamming_weight`` in the result is always that of the unmasked value ``v``.
    """
    if operations < 2:
        raise ValueError("need at least 2 operations")
    if not 1 <= data_width <= 63:
        raise ValueError("data_width must be between 1 and 63 bits")
    if noise_sigma < 0:
        raise ValueError("noise_sigma must be >= 0")
    rng = np.random.default_rng(seed)
    intermediates = rng.integers(0, 2**data_width, size=operations, dtype=np.uint64)
    hw = hamming_weight(intermediates)
    result = {"intermediates": intermediates, "hamming_weight": hw}
    if masked:
        masks = rng.integers(0, 2**data_width, size=operations, dtype=np.uint64)
        signal = hamming_weight(intermediates ^ masks) + hamming_weight(masks)
        result["masks"] = masks
    else:
        signal = hw
    result["power"] = signal + rng.normal(0.0, noise_sigma, size=operations)
    return result


def leakage_correlation(hamming_weights, power) -> float:
    """Pearson correlation between the leakage model and the measured trace."""
    hw = np.asarray(hamming_weights, dtype=float)
    p = np.asarray(power, dtype=float)
    if hw.shape != p.shape or hw.size < 2:
        raise ValueError("inputs must have the same length (>= 2)")
    if hw.std() == 0 or p.std() == 0:
        return 0.0
    return float(np.corrcoef(hw, p)[0, 1])


def second_order_correlation(hamming_weights, power) -> float:
    """Correlation between the leakage model and the squared, mean-centred trace.

    First-order masking removes the leakage from the mean of the trace but not from
    its variance, so this is the simplest check that still sees a masked value. For
    the two-share model here the variance is ``width - HW(v)``, so the result is
    negative; an unmasked trace gives a value near zero.
    """
    p = np.asarray(power, dtype=float)
    if p.size < 2:
        raise ValueError("inputs must have the same length (>= 2)")
    return leakage_correlation(hamming_weights, (p - p.mean()) ** 2)


def expected_correlation(data_width: int, noise_sigma: float, masked: bool = False) -> float:
    """Theoretical correlation for uniform data: signal variance is width / 4.

    A first-order masked trace has no first-order leakage, so the expected value is 0.
    """
    if masked:
        return 0.0
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
