import math

import pandas as pd
import streamlit as st

from hwsec import (
    FAULT_TYPES,
    HASH_ALGORITHMS,
    apply_fault,
    compute_hash,
    fault_sweep,
    leakage_correlation,
    simulate_power_trace,
    traces_needed,
    verify_hash,
)
from hwsec.sidechannel import expected_correlation

st.set_page_config(page_title="Hardware Security Testing Toolkit", layout="wide")

st.title("🛡️ Hardware Security Testing Toolkit for AI Accelerators")
st.caption(
    "Defensive research on hardware security and AI-accelerator architectures at PDPM IIITDM Jabalpur | "
    "Vulnerability analysis & secure design validation | Security Maintainer: Sachin Majhee"
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Side-Channel Leakage Model", "Fault Impact Estimator", "Secure Design Checklist", "Integrity Hasher"]
)

with tab1:
    st.header("Side-Channel Leakage Model (Hamming weight)")
    st.write(
        "Simulates a power trace that follows the Hamming weight of processed values, then measures how "
        "strongly the two correlate. Raise the noise to see how hiding countermeasures reduce leakage. "
        "All data is synthetic."
    )
    c1, c2, c3 = st.columns(3)
    data_width = c1.slider("Data width (bits)", 8, 32, 16)
    operations = c2.number_input("Operations to simulate", 10, 100000, 1000)
    noise_sigma = c3.slider("Noise sigma (Hamming-weight units)", 0.0, 20.0, 0.5, 0.1)
    seed = st.number_input("Random seed (same seed = same trace)", 0, 2**31 - 1, 42)
    if st.button("Generate simulated power trace"):
        trace = simulate_power_trace(int(operations), data_width, noise_sigma, int(seed))
        r = leakage_correlation(trace["hamming_weight"], trace["power"])
        n = traces_needed(r)
        m1, m2, m3 = st.columns(3)
        m1.metric("Measured correlation", f"{r:.3f}")
        m2.metric("Expected (theory)", f"{expected_correlation(data_width, noise_sigma):.3f}")
        m3.metric("Traces needed to detect", "no leakage" if math.isinf(n) else f"{math.ceil(n):,}")
        df = pd.DataFrame({"Hamming weight": trace["hamming_weight"], "Simulated power": trace["power"]})
        st.line_chart(df.head(300))
        st.info(
            "Lower correlation means more traces are needed to exploit the leakage. Masking and hiding "
            "aim to push that number beyond what an attacker can collect."
        )

with tab2:
    st.header("Fault Impact Estimator")
    st.write("Effect of a single-bit fault on an unsigned accumulator, as found in MAC units of AI accelerators.")
    width = st.selectbox("Register width (bits)", [8, 16, 24, 32], index=3)
    original_value = st.number_input("Original accumulator value", 0, 2**width - 1, min(1000, 2**width - 1))
    fault_type = st.selectbox("Fault type", FAULT_TYPES)
    bit_position = st.slider("Bit position affected", 0, width - 1, min(5, width - 1))
    faulty = apply_fault(int(original_value), bit_position, fault_type, width)
    delta = abs(faulty - int(original_value))
    f1, f2, f3 = st.columns(3)
    f1.metric("Faulty value", f"{faulty:,}")
    f2.metric("Absolute error", f"{delta:,}")
    f3.metric("Relative error", f"{delta / original_value:.2%}" if original_value else "n/a")
    if delta == 0:
        st.caption("This fault is masked: the bit already had the stuck-at value.")
    sweep = pd.DataFrame(fault_sweep(int(original_value), fault_type, width)).set_index("bit")
    st.subheader("Error by bit position")
    st.bar_chart(sweep["abs_error"])
    st.info("Faults in high-order bits dominate the error, which is why they are the first to protect with parity or redundancy.")

with tab3:
    st.header("Secure Design Checklist for AI / Neuromorphic Hardware")
    checks = [
        "Side-channel resistant arithmetic units (masking / hiding)",
        "Fault detection via redundant computation or parity",
        "Secure boot / attestation for accelerator configuration",
        "Memory isolation between tenants in multi-tenant accelerators",
        "Protection against hardware Trojans in supply chain",
        "Neuromorphic spike encoding resistant to timing attacks",
        "Power analysis countermeasures on MAC arrays",
        "Secure key storage for encrypted model weights",
    ]
    done = [st.checkbox(c, value=False) for c in checks]
    st.progress(sum(done) / len(checks), text=f"{sum(done)} of {len(checks)} verified")
    open_items = [c for c, d in zip(checks, done) if not d]
    st.download_button(
        "Download review status",
        "\n".join(f"[{'x' if d else ' '}] {c}" for c, d in zip(checks, done)),
        file_name="design_review_checklist.txt",
    )
    if open_items:
        st.write("Still open: " + "; ".join(open_items))

with tab4:
    st.header("Configuration Integrity Hasher")
    config = st.text_area("Paste accelerator config / model manifest", "accelerator_config_v1_weights_encrypted")
    uploaded = st.file_uploader("...or upload a file (hashed in memory, not stored)")
    algo = st.selectbox("Hash algorithm", HASH_ALGORITHMS)
    expected = st.text_input("Known-good hash to verify against (optional)")
    if st.button("Compute integrity hash"):
        data = uploaded.getvalue() if uploaded is not None else config
        st.code(compute_hash(data, algo))
        if expected.strip():
            if verify_hash(data, expected, algo):
                st.success("Match: the configuration is unchanged.")
            else:
                st.error("Mismatch: the configuration differs from the known-good version.")

st.sidebar.title("About")
st.sidebar.info(
    "Defensive research on hardware security and AI-accelerator architectures at PDPM IIITDM Jabalpur.\n"
    "Including vulnerability analysis and secure design validation.\nSecurity Maintainer: Sachin Majhee"
)
st.sidebar.warning("Educational / research tool. All side-channel and fault data is simulated.")
