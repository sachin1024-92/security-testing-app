"""Models behind the Hardware Security Testing Toolkit (no UI code here)."""

from .faults import FAULT_TYPES, apply_fault, fault_sweep
from .integrity import HASH_ALGORITHMS, compute_hash, verify_hash
from .sidechannel import hamming_weight, leakage_correlation, simulate_power_trace, traces_needed

__all__ = [
    "FAULT_TYPES",
    "HASH_ALGORITHMS",
    "apply_fault",
    "compute_hash",
    "fault_sweep",
    "hamming_weight",
    "leakage_correlation",
    "simulate_power_trace",
    "traces_needed",
    "verify_hash",
]
