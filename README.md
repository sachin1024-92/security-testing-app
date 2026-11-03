# Hardware Security Testing Toolkit for AI Accelerators

**Security Maintainer:** Sachin Majhee (@sachin1024-92)

## Overview
This repository hosts a practical testing application related to hardware security aspects of AI accelerators and neuromorphic hardware. It is developed in the context of PhD research on VLSI / AI accelerators / Hardware Security / Neuromorphic hardware architectures at PDPM IIITDM Jabalpur.

The app provides interactive tools for:
- Simulating side-channel leakage estimation
- Estimating fault injection impact on accelerator operations
- Running secure design checklists
- Demonstrating integrity verification via hashing
- Educational awareness of common hardware security threats (side-channel attacks, fault injection, hardware Trojans)

**Purpose:** Security testing, research experimentation, and educational demonstration. Not for production offensive use.

## Features
- Streamlit-based interactive dashboard
- Simple power-trace simulation for side-channel analysis
- Fault model impact calculator (stuck-at, bit-flip)
- Hardware security checklist for AI/neuromorphic designs
- Secure configuration hashing

## Installation & Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Role
- **Security Maintainer:** Sachin Majhee
- Responsible for security-related updates, vulnerability assessments of the toolkit itself, and alignment with PhD research goals in hardware security.

## Disclaimer
This is a research and testing tool. Use only on systems you own or have permission to test. Educational purposes only.

## License
MIT
