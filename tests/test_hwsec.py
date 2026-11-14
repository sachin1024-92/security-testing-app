import hashlib
import math

import numpy as np
import pytest

from hwsec import apply_fault, compute_hash, fault_sweep, hamming_weight, leakage_correlation
from hwsec import simulate_power_trace, traces_needed, verify_hash
from hwsec.sidechannel import expected_correlation


def test_hamming_weight():
    assert hamming_weight([0, 1, 3, 255, 2**32 - 1]).tolist() == [0, 1, 2, 8, 32]


def test_trace_is_reproducible_with_seed():
    a = simulate_power_trace(200, seed=7)
    b = simulate_power_trace(200, seed=7)
    assert np.array_equal(a["power"], b["power"])
    assert not np.array_equal(a["power"], simulate_power_trace(200, seed=8)["power"])


def test_noiseless_trace_correlates_perfectly():
    t = simulate_power_trace(500, noise_sigma=0.0, seed=1)
    assert leakage_correlation(t["hamming_weight"], t["power"]) == pytest.approx(1.0)


def test_correlation_matches_theory_and_falls_with_noise():
    low = simulate_power_trace(50000, 16, noise_sigma=1.0, seed=3)
    high = simulate_power_trace(50000, 16, noise_sigma=8.0, seed=3)
    r_low = leakage_correlation(low["hamming_weight"], low["power"])
    r_high = leakage_correlation(high["hamming_weight"], high["power"])
    assert r_low == pytest.approx(expected_correlation(16, 1.0), abs=0.02)
    assert r_high == pytest.approx(expected_correlation(16, 8.0), abs=0.02)
    assert r_high < r_low


def test_traces_needed_grows_as_leakage_shrinks():
    assert traces_needed(0.1) > traces_needed(0.5) > traces_needed(0.9)
    assert math.isinf(traces_needed(0.0))
    assert traces_needed(1.0) == 3.0


def test_invalid_trace_arguments():
    with pytest.raises(ValueError):
        simulate_power_trace(1)
    with pytest.raises(ValueError):
        simulate_power_trace(10, data_width=64)


def test_fault_models():
    assert apply_fault(1000, 5, "bit-flip") == 968  # bit 5 was 1
    assert apply_fault(1000, 4, "bit-flip") == 1016  # bit 4 was 0
    assert apply_fault(1000, 3, "bit-flip") == 992
    assert apply_fault(1000, 3, "stuck-at-0") == 992
    assert apply_fault(1000, 3, "stuck-at-1") == 1000  # masked: bit already 1
    assert apply_fault(0, 31, "stuck-at-1") == 2**31


def test_fault_validation():
    with pytest.raises(ValueError):
        apply_fault(1000, 8, "bit-flip", width=8)
    with pytest.raises(ValueError):
        apply_fault(1, 0, "glitch")


def test_fault_sweep_bit_flip_errors_are_powers_of_two():
    rows = fault_sweep(1000, "bit-flip", width=16)
    assert [r["abs_error"] for r in rows] == [2**b for b in range(16)]


def test_hash_and_verify():
    digest = compute_hash("config-v1")
    assert digest == hashlib.sha256(b"config-v1").hexdigest()
    assert verify_hash("config-v1", digest.upper() + "  ")
    assert not verify_hash("config-v2", digest)
    assert compute_hash(b"x", "SHA3-256") == hashlib.sha3_256(b"x").hexdigest()
    with pytest.raises(ValueError):
        compute_hash("x", "MD5")
