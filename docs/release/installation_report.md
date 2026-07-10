# Installation & Setup Verification Report

This document reports scratch installation steps and config verification checks.

---

## 1. Scratch Installation Steps
1. Clone the repository: `git clone https://github.com/Anzar0904/Aios.git`
2. Create Python virtual environment: `python3 -m venv .venv`
3. Activate virtual environment: `source .venv/bin/activate`
4. Install dependencies: `pip install -e .`
5. Run the onboarding wizard: `aios setup`

---

## 2. Setup Validation
The interactive wizard validates your credentials files and writes the initial TOML config blocks to `config/config.toml` securely.
