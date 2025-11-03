import json, os
import matplotlib.pyplot as plt

def load(path):
    with open(path) as f:
        j = json.load(f)
    # Try a few common keys; adjust if your extractor uses different names.
    def get(*candidates, default=None):
        for k in candidates:
            if k in j: return j[k]
        if default is not None: return default
        raise KeyError(f"Missing keys {candidates} in {path}")
    return {
        "peak_dt": float(get("Peak DT (%)", "Peak Backend Load (% of no cache)", "peak_dt", default=None)),
        "median_dt": float(get("Median DT (%)", "Median Backend Load (% of no cache)", "median_dt", default=None)),
        "hit_rate": float(get("IO Hit Rate (%)", "Chunk hit ratio (%)", "hit_rate", default=None)),
    }

runs = {
    "E0: LRU":       "./output/lru_baseline/metrics.json",
    "E1: DT-SLRU":   "./output/e1_dt_slru/metrics.json",
    "E2: EDE":       "./output/e2_ede/metrics.json",
}
data = {k: load(v) for k,v in runs.items()}

# Fig 1 — Peak DT across E0–E2
labels = list(runs.keys())
vals = [data[k]["peak_dt"] for k in labels]
plt.figure()
plt.bar(labels, vals)
plt.ylabel("Peak DT (% of no cache)")
plt.title("Figure 1: Peak DT across eviction schemes (E0–E2)")
plt.tight_layout()
plt.savefig("Figure1_peakDT_E0E2.png", dpi=200)

# Fig 2 — Median DT across E0–E2
vals = [data[k]["median_dt"] for k in labels]
plt.figure()
plt.bar(labels, vals)
plt.ylabel("Median DT (% of no cache)")
plt.title("Figure 2: Median DT across eviction schemes (E0–E2)")
plt.tight_layout()
plt.savefig("Figure2_medianDT_E0E2.png", dpi=200)

# Fig 3 — Hit Rate across E0–E2
vals = [data[k]["hit_rate"] for k in labels]
plt.figure()
plt.bar(labels, vals)
plt.ylabel("Cache Hit Rate (%)")
plt.title("Figure 3: Cache Hit Rate across eviction schemes (E0–E2)")
plt.tight_layout()
plt.savefig("Figure3_hitRate_E0E2.png", dpi=200)

print("Wrote: Figure1_peakDT_E0E2.png, Figure2_medianDT_E0E2.png, Figure3_hitRate_E0E2.png")
