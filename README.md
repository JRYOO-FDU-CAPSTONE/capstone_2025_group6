# capstone_2025_group6
## Group Information
Group Number: 6

Members:
-- Jun Tang	2111172	j.tang4@student.fdu.edu
-- Xiaoyi Han	2133542	x.han1@student.fdu.edu
-- Kaiwen Wang	2073512	k.wang4@student.fdu.edu
-- Ziyan Qiu	2089937	z.qiu1@student.fdu.edu
-- Hongyi Niu	2104640	h.niu@student.fdu.edu
---

## System Requirements

OS: Ubuntu 21 (tested), macOS 14 (expected compatible)
CPU: x86_64 with AVX2 support
RAM: >= 8 GB
GPU: Optional (for PyTorch acceleration)

Python: 3.12.9

Dependencies:
- numpy==1.23.5
- matplotlib==3.7.1
- torch==2.1.0

---

## Setup Instructions

Step 1 – Create virtual environment
    python -m venv baleen-env
    source baleen-env/bin/activate

Step 2 – Install dependencies
    pip install -r requirements.txt

Step 3 – Clone repository (if not already in this repo)
    git clone https://github.com/JRYOO-FDU-CAPSTONE/capstone_2025_group6.git
    cd capstone_2025_group6

All commands above have been tested from a fresh clone.

---

## Reproducing Results

The following commands regenerate the main figure and table referenced in our report.

Eviction Policy Comparison
    python scripts/fig5.py 

---

## Validation Checklist

Test 1 – Peak DT computation
    python scripts/e1.py

---

## Limitations

1. Results may not exactly match the FAST 2024 paper because proprietary disk-head-time constants from Meta are not available; approximate constants are used instead.
2. Running full experiments on large traces can take tens of minutes per run and requires sufficient CPU and RAM.
3. GPU acceleration is optional and not required, but training-related steps may be slower without it.
4. Some scripts assume the default directory structure of this repository (e.g., paths under scripts/, configs/, data/).
5. macOS has been lightly tested; Linux (Ubuntu 22.04) is the primary tested platform.

---

## Repository Organization

Directory layout (most relevant paths):

- scripts/      : Python scripts used for experiments, plotting, and profiling
- configs/      : YAML configuration files for experiments (e.g., eviction.yaml)
- figures/         : Directory where generated figures (e.g., figure2.pdf) are written
- output/      : Directory where generated tables (e.g., table1.csv) are written
- data/         : Trace files and other input data (may need to be downloaded separately)

All plots used in the report are generated using matplotlib and live under scripts/.
All commands have been validated to run from a fresh clone with the setup instructions above.

---

## Reproduction Summary

To reproduce the key results:
1. Follow the “Setup Instructions” section on a supported system.
2. Run the commands in the “Reproducing Results” section to regenerate the main figure and table.
3. Run the three commands in the “Validation Checklist” section to confirm correct functionality and expected outputs.

If all commands complete successfully and outputs are close to the stated expectations, the artifact has been reproduced as required for A7.

---

## Citation

This artifact is based on the Baleen simulator from:

“Baleen: ML Admission & Prefetching for Flash Caches”
USENIX FAST 2024 – Daniel Lin-Kit Wong et al.

---

## Repository URL

Main repository URL (replace with your group repo):
https://github.com/JRYOO-FDU-CAPSTONE/capstone_2025_group6.git
