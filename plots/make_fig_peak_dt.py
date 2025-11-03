# plots/make_fig_peak_dt.py
import json, os
import matplotlib.pyplot as plt

paths = {
    "E0: LRU": "./output/lru_baseline/metrics.json",
    "E1: DT-SLRU": "./output/e1_dt_slru/metrics.json",
    "E2: EDE": "./output/e2_ede/metrics.json",
}

def load_peak(path):
    with open(path) as f:
        j = json.load(f)
    # Try a few keys your extractor might have produced
    for k in ["Peak DT (%)", "Peak Backend Load (% of no cache)", "Peak Service Time Utilization (%)"]:
        if k in j and j[k] is not None:
            return float(j[k])
    raise KeyError(f"Peak DT not found in {path}. Keys: {list(j.keys())}")

labels = list(paths.keys())
values = [load_peak(paths[k]) for k in labels]

plt.figure()
plt.bar(labels, values)
plt.ylabel("Peak DT (% of no cache)")
plt.title("Peak DT across E0–E2")
plt.tight_layout()
os.makedirs("plots/out", exist_ok=True)
plt.savefig("plots/out/fig_peak_dt_e0e2.png", dpi=200)
print("Wrote plots/out/fig_peak_dt_e0e2.png")
