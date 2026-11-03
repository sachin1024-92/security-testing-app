import streamlit as st
import hashlib
import numpy as np
import pandas as pd

st.set_page_config(page_title="Hardware Security Testing Toolkit", layout="wide")

st.title("🛡️ Hardware Security Testing Toolkit for AI Accelerators")
st.caption("PhD Research Context: VLSI / AI Accelerators / Hardware Security / Neuromorphic Hardware | Security Maintainer: Sachin Majhee")

tab1, tab2, tab3, tab4 = st.tabs(["Side-Channel Simulation", "Fault Injection Estimator", "Secure Design Checklist", "Integrity Hasher"])

with tab1:
    st.header("Side-Channel Leakage Estimation (Simple Power Model)")
    st.write("Simulates differential power analysis style leakage based on Hamming weight of intermediate values.")
    data_width = st.slider("Data width (bits)", 8, 32, 16)
    operations = st.number_input("Number of operations to simulate", 10, 1000, 100)
    if st.button("Generate Simulated Power Trace"):
        # Simple HW-based leakage model
        intermediates = np.random.randint(0, 2**data_width, operations)
        hamming_weights = [bin(x).count('1') for x in intermediates]
        noise = np.random.normal(0, 0.5, operations)
        power_trace = np.array(hamming_weights) + noise
        df = pd.DataFrame({"Operation": range(operations), "Hamming Weight": hamming_weights, "Simulated Power": power_trace})
        st.line_chart(df.set_index("Operation")["Simulated Power"])
        st.success("Trace generated. Higher correlation with HW indicates potential leakage.")

with tab2:
    st.header("Fault Injection Impact Estimator")
    st.write("Estimate effect of bit-flips or stuck-at faults on MAC operations typical in AI accelerators.")
    original_value = st.number_input("Original accumulator value", value=1000)
    fault_type = st.selectbox("Fault type", ["Bit-flip (random)", "Stuck-at-0", "Stuck-at-1"])
    bit_position = st.slider("Bit position affected", 0, 31, 5)
    if st.button("Apply Fault Model"):
        if fault_type == "Bit-flip (random)":
            faulty = original_value ^ (1 << bit_position)
        elif fault_type == "Stuck-at-0":
            faulty = original_value & ~(1 << bit_position)
        else:
            faulty = original_value | (1 << bit_position)
        delta = abs(faulty - original_value)
        st.metric("Faulty Value", faulty)
        st.metric("Absolute Error", delta)
        st.info("In AI accelerators, such faults can propagate into inference accuracy degradation.")

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
        "Secure key storage for encrypted model weights"
    ]
    for c in checks:
        st.checkbox(c, value=False)
    st.write("Tick items as they are verified during design review. Aligns with hardware security research goals.")

with tab4:
    st.header("Configuration Integrity Hasher")
    config = st.text_area("Paste accelerator config / model hash input", "accelerator_config_v1_weights_encrypted")
    algo = st.selectbox("Hash algorithm", ["SHA-256", "SHA-512", "MD5 (not recommended)"])
    if st.button("Compute Integrity Hash"):
        if algo == "SHA-256":
            h = hashlib.sha256(config.encode()).hexdigest()
        elif algo == "SHA-512":
            h = hashlib.sha512(config.encode()).hexdigest()
        else:
            h = hashlib.md5(config.encode()).hexdigest()
        st.code(h)
        st.success("Use this hash to verify configuration integrity before loading into the accelerator.")

st.sidebar.title("About")
st.sidebar.info("Developed for PhD research on Hardware Security of AI Accelerators.\nSecurity Maintainer: Sachin Majhee")
st.sidebar.warning("Educational / Research testing tool only.")
