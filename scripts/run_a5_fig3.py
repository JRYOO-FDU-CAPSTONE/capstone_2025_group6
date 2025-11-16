# Save as: capstone_2025_group6/run_a5_fig3.py
# (This version is corrected to use the actual code)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from collections import defaultdict
import logging

# --- Configure logging to show progress ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Project Imports ---
# These are the CORRECT imports based on your code files
from BCacheSim.cachesim.sim_cache import simulate_cache
from BCacheSim.cachesim.eviction_policies import Cache  # <-- This was the missing import
from BCacheSim.cachesim.admission_policies import AdmitAllPolicy
from BCacheSim.cachesim.prefetchers import NoPrefetcher
from BCacheSim.episodic_analysis.trace_utils import load_trace

# Import your new EDE policy
try:
    from BCacheSim.cachesim.a5_eviction_policies import EDE
except ImportError:
    logging.error("FATAL: Could not find 'a5_eviction_policies.py'.")
    logging.error("Please save the EDE policy file inside 'BCacheSim/cachesim/'.")
    exit(1)

# -------------------------------------------------------------------------
# --- 1. Experiment Configuration ---
# -------------------------------------------------------------------------

# This path is relative to this script (your project root)
TRACE_PATH = "data/tectonic/201910/Region1/" 
TRACE_NAME = "full_0_0.1" 

# Set fixed parameters from A4/A5
CACHE_SIZE_BYTES = 400 * 1024 * 1024 * 1024 # 400 GiB
SEGMENT_SIZE = 128 * 1024 # 128 KiB

# Disk-head Time (DT) constants from Baleen paper
T_SEEK = 4  # ms
T_READ = 0.0000068 # ms / byte (equiv. to 143 MB/s)

# A5: Peak DT (primary). Paper uses 10-minute (600s) windows.
PEAK_DT_WINDOW_SEC = 600
LOG_INTERVAL_REQS = 100000

# -------------------------------------------------------------------------
# --- 2. Simulator Wrapper for Peak DT ---
# -------------------------------------------------------------------------

def calculate_dt(n_bytes, n_ios):
    """Calculates Disk-head Time (DT) in milliseconds."""
    return (n_ios * T_SEEK) + (n_bytes * T_READ)

def run_simulation_pass(trace_df, trace_stats, cache_size, admission_policy, 
                          eviction_policy_instance, prefetcher, **kwargs):
    """
    This wrapper creates a cache and calls the 'simulate_cache' function.
    """
    logging.info("Starting simulation run...")
    
    # --- 1. Create a new cache object for this run ---
    # We instantiate the Cache class from eviction_policies.py
    # and pass our custom EDE policy instance to it.
    cache = Cache(
        cache_size_bytes=cache_size,
        eviction_policy=eviction_policy_instance,
        segment_size=kwargs.get("segment_size")
    )

    # --- 2. Setup Peak DT tracking ---
    window_stats = defaultdict(lambda: {'miss_bytes': 0, 'miss_ios': 0})

    def miss_callback(key, size, metadata):
        ts = metadata['timestamp']
        window_key = int(ts / PEAK_DT_WINDOW_SEC)
        window_stats[window_key]['miss_bytes'] += size
        window_stats[window_key]['miss_ios'] += 1

    # --- 3. Call the correct simulation function ---
    stats = simulate_cache(
        cache=cache,
        accesses=trace_df,
        sample_ratio=trace_stats['sample_ratio'],
        total_iops_get=trace_stats['total_iops_get'],
        total_iops=trace_stats['total_iops'],
        trace_duration_secs=trace_stats['trace_duration_secs'],
        admission_policy=admission_policy,
        prefetcher=prefetcher,
        miss_callback=miss_callback,
        log_interval=LOG_INTERVAL_REQS,
        **kwargs
    )
    
    # --- 4. Post-process to find Peak DT ---
    if not window_stats:
        logging.warning("No misses recorded.")
        stats['peak_dt_ms'] = 0
        stats['median_dt_ms'] = 0
        return stats

    dt_per_window = []
    for window_key, data in window_stats.items():
        dt_ms = calculate_dt(data['miss_bytes'], data['miss_ios'])
        dt_per_window.append(dt_ms)

    stats['peak_dt_ms'] = np.max(dt_per_window)
    stats['median_dt_ms'] = np.median(dt_per_window)
    
    logging.info(f"Simulation complete. Hit Rate: {stats.get('hit_rate', 0):.4f}, Peak DT (ms): {stats['peak_dt_ms']:.2f}")
    
    return stats

# -------------------------------------------------------------------------
# --- 3. A5 Experiment Script (Figure 3) ---
# -------------------------------------------------------------------------

logging.info("--- Starting A5: Figure 3 Ablation Study ---")
logging.info(f"Policy: EDE (E2)")
logging.info(f"Parameter: PROTECTED cap")

PROTECTED_CAP_VALUES = [0.1, 0.3, 0.5, 0.7, 0.9]
NUM_RUNS = 3

logging.info(f"Values: {PROTECTED_CAP_VALUES}")
logging.info(f"Runs per value: {NUM_RUNS}")
logging.info(f"Cache Size: {CACHE_SIZE_BYTES / (1024**3):.0f} GiB")
logging.info("---------------------------------------------")

# --- Load Trace File ONCE ---
full_trace_path = os.path.join(TRACE_PATH, TRACE_NAME)
if not os.path.exists(full_trace_path + ".trace"):
    logging.error(f"FATAL ERROR: Trace file not found at '{full_trace_path}.trace'")
    logging.error(f"Please check your TRACE_PATH and TRACE_NAME variables.")
    logging.error(f"Expected path: {os.path.abspath(TRACE_PATH)}")
    exit(1)

logging.info(f"Loading trace '{TRACE_NAME}'... (This may take a few minutes)")
trace_df, trace_stats = load_trace(TRACE_PATH, TRACE_NAME)
logging.info("Trace loaded successfully.")
logging.info("---------------------------------------------")


final_peak_dt_results = []

ADMISSION_POLICY = AdmitAllPolicy()
PREFETCHER = NoPrefetcher()


for cap_value in PROTECTED_CAP_VALUES:
    
    run_results_for_value = []
    logging.info(f"\n[Testing PROTECTED_cap = {cap_value}]")
    
    for i in range(NUM_RUNS):
        logging.info(f"  Run {i+1}/{NUM_RUNS}...")
        
        # Instantiate your EDE policy
        ede_policy_instance = EDE(
            cache_size=CACHE_SIZE_BYTES,
            protected_cap=cap_value,
            otti=0.5 # Held constant at a default, as per A5
        )
        
        stats = run_simulation_pass(
            trace_df=trace_df,
            trace_stats=trace_stats,
            cache_size=CACHE_SIZE_BYTES,
            admission_policy=ADMISSION_POLICY,
            eviction_policy_instance=ede_policy_instance,
            prefetcher=PREFETCHER,
            segment_size=SEGMENT_SIZE,
        )
        
        run_results_for_value.append(stats['peak_dt_ms'])
        
    average_peak_dt = np.mean(run_results_for_value)
    final_peak_dt_results.append(average_peak_dt)
    logging.info(f"  -> Average Peak DT for cap={cap_value}: {average_peak_dt:.2f} ms")

logging.info("\n--- Ablation Study Complete ---")

# --- 4. Generate Figure 3 ---

logging.info("Generating plot using matplotlib...")

plt.figure(figsize=(10, 6))
plt.plot(
    PROTECTED_CAP_VALUES,
    final_peak_dt_results,
    marker='o',
    linestyle='-',
    label=f'EDE (E2) Policy (Avg. of {NUM_RUNS} Runs)'
)

plt.title("Figure 3: Peak DT vs PROTECTED cap (EDE)")
plt.xlabel("PROTECTED cap (EDE)")
plt.ylabel("Peak DT (ms per 10-min window)")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(PROTECTED_CAP_VALUES)

plot_filename = "figure_3_peak_dt_vs_protected_cap.pdf"
plt.savefig(plot_filename)

logging.info(f"\nSuccessfully saved plot to '{plot_filename}'")
logging.info("Script finished.")