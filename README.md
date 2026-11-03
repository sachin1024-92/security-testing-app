# Hardware Security Testing Toolkit for AI Accelerators

**Security Maintainer:** Sachin Majhee (@sachin1024-92)

## Overview
Defensive research on hardware security and AI-accelerator architectures at PDPM IIITDM Jabalpur, including vulnerability analysis and secure design validation for research systems and related open hardware designs.

This repository hosts a practical testing application related to hardware security aspects of AI accelerators and neuromorphic hardware. It is developed in the context of PhD research on VLSI / AI accelerators / Hardware Security / Neuromorphic hardware architectures at PDPM IIITDM Jabalpur.

The app provides interactive tools for:
- Vulnerability analysis via side-channel leakage estimation and fault injection modeling
- Secure design validation through checklists and integrity verification
- Educational awareness of common hardware security threats (side-channel attacks, fault injection, hardware Trojans) in a defensive research context
- Simulation of security properties for research systems and open hardware designs

**Purpose:** Defensive security research, vulnerability analysis, secure design validation, and educational demonstration for AI-accelerator and neuromorphic hardware. Not for production offensive use.

## Features
- Streamlit-based interactive dashboard for defensive research
- Simple power-trace simulation for side-channel vulnerability analysis
- Fault model impact calculator (stuck-at, bit-flip) for secure design validation
- Hardware security checklist for AI/neuromorphic designs
- Secure configuration hashing for integrity validation

## Installation & Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Role
- **Security Maintainer:** Sachin Majhee
- Responsible for security-related updates, vulnerability assessments of the toolkit itself, and alignment with PhD research goals in defensive hardware security for AI accelerators.

## Disclaimer
This is a research and testing tool for defensive hardware security analysis. Use only on systems you own or have permission to test. Educational and research purposes only.

## License
MIT
