"""Single-bit fault models on a fixed-width register (e.g. a MAC accumulator)."""

from __future__ import annotations

FAULT_TYPES = ("bit-flip", "stuck-at-0", "stuck-at-1")


def apply_fault(value: int, bit: int, fault_type: str, width: int = 32) -> int:
    """Return ``value`` after a fault on one bit of an unsigned ``width``-bit register."""
    if width < 1:
        raise ValueError("width must be >= 1")
    if not 0 <= bit < width:
        raise ValueError(f"bit must be in 0..{width - 1}")
    if not 0 <= value < 2**width:
        raise ValueError(f"value does not fit in {width} unsigned bits")
    mask = 1 << bit
    if fault_type == "bit-flip":
        return value ^ mask
    if fault_type == "stuck-at-0":
        return value & ~mask
    if fault_type == "stuck-at-1":
        return value | mask
    raise ValueError(f"unknown fault type: {fault_type!r}")


def fault_sweep(value: int, fault_type: str, width: int = 32) -> list[dict]:
    """Absolute and relative error for a fault on each bit position."""
    rows = []
    for bit in range(width):
        faulty = apply_fault(value, bit, fault_type, width)
        error = abs(faulty - value)
        rows.append(
            {
                "bit": bit,
                "faulty": faulty,
                "abs_error": error,
                "rel_error": error / value if value else float(error > 0),
            }
        )
    return rows
