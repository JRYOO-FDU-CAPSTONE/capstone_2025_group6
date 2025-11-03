#!/usr/bin/env python3
import lzma, json, os, math

# Update paths if yours differ
FILES = [
    ("LRU",    "./output/lru_baseline/acceptall-0_lru_50GB/full_0_0.1_cache_perf.txt.lzma"),
    ("DTSLRU", "./output/e1_dt_slru/acceptall-0_lru_50GB/full_0_0.1_cache_perf.txt.lzma"),
]

def fmt(x, nd=5):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "NA"
    return f"{x:.{nd}g}"

def load_json_lzma(p):
    with lzma.open(p, "rt", encoding="utf-8", errors="ignore") as fh:
        return json.load(fh)

def extract_metrics(d):
    # Overall Service Time Utilization (%) over the whole trace:
    # STU% = 100 * service_time_used / traceSeconds
    trace_secs = d.get("traceSeconds")
    stu_used   = d.get("stats", {}).get("service_time_used")
    stu_pct    = 100.0 * stu_used / trace_secs if (trace_secs and stu_used) else None

    # Flash Cache Hit Rate:
    hit_rate   = d.get("results", {}).get("FlashCacheHitRate")

    return stu_pct, hit_rate

def pct_change(new, old):
    if new is None or old in (None, 0):
        return None
    return 100.0 * (new - old) / old

def main():
    rows = []
    for label, path in FILES:
        if not os.path.exists(path):
            print(f"== {label}: {path} ==\nERROR: not found\n")
            continue
        d = load_json_lzma(path)
        stu_pct, hit_rate = extract_metrics(d)
        rows.append((label, path, stu_pct, hit_rate))

    # Print metrics
    for label, path, stu, hr in rows:
        print(f"== {label}: {path} ==")
        print("Overall Service Time Utilization (%) :", fmt(stu))
        print("Flash Cache Hit Rate                 :", fmt(hr))
        print()

    # If both present, also print deltas (DTSLRU vs LRU)
    d = {label: (stu, hr) for label, _, stu, hr in rows}
    if "LRU" in d and "DTSLRU" in d:
        stu_lru, hr_lru = d["LRU"]
        stu_dt,  hr_dt  = d["DTSLRU"]
        d_stu = pct_change(stu_dt, stu_lru)
        d_hr  = pct_change(hr_dt,  hr_lru)
        print("== Delta (DTSLRU vs LRU) ==")
        print("Δ Overall ST Utilization (rel %) :", fmt(d_stu))
        print("Δ Flash Hit Rate (rel %)         :", fmt(d_hr))

if __name__ == "__main__":
    main()
