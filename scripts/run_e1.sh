#!/bin/bash

TRACE="data/tectonic/201910/Region1/full_0_0.1.trace"
CACHE_SIZE_GB=16  # Adjust for your evaluation setup
OUT_BASE="runs/e1_tau"
mkdir -p "${OUT_BASE}"

for TAU in 0.0 0.5 1.0 2.0 4.0 8.0; do
  echo ">>> Running DT-SLRU with τ_DT=${TAU}"
  python -m BCacheSim.cachesim.simulate_ap \
    -t "${TRACE}" \
    --eviction-policy DT-SLRU \
    --dt_slru_tau "${TAU}" \
    --prefetch never \
    --ap admit-all \
    -s "${CACHE_SIZE_GB}" \
    -o "${OUT_BASE}_${TAU}" \
    --override
done
