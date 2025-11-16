import lzma, json, sys, os, math, statistics as stats

def find_all(d, want):
    """Yield (path, value) for keys whose name contains any substring in want (case-insensitive)."""
    want = [w.lower() for w in want]
    stack = [([], d)]
    while stack:
        path, node = stack.pop()
        if isinstance(node, dict):
            for k,v in node.items():
                if any(w in k.lower() for w in want):
                    yield (".".join(path+[k]), v)
                stack.append((path+[k], v))
        elif isinstance(node, list):
            for i, v in enumerate(node):
                stack.append((path+[str(i)], v))

def median_from_series(root):
    # Try to find a per-interval Service Time Utilization (%) series
    series = []
    for path,val in find_all(root, ["service time utilization", "service_time_utilization", "stu_series", "service_time_series"]):
        if isinstance(val, list):
            for x in val:
                if isinstance(x,(int,float)) and math.isfinite(x):
                    series.append(float(x))
                elif isinstance(x, dict):
                    # common pattern: dicts like {"stu": 21.1} or {"service_time_utilization": 21.1}
                    for kk in ["stu","service_time_utilization","service time utilization"]:
                        if kk in x and isinstance(x[kk], (int,float)) and math.isfinite(x[kk]):
                            series.append(float(x[kk]))
    if series:
        return stats.median(series), max(series), stats.mean(series)
    return None, None, None

def extract_metrics(path):
    with lzma.open(path, "rt", encoding="utf-8", errors="ignore") as fh:
        root = json.load(fh)

    # Hit Rate
    hit = None
    for _, v in find_all(root, ["flash cache hit rate", "hit_rate", "cache_hit_rate"]):
        if isinstance(v,(int,float)) and math.isfinite(v):
            hit = float(v); break
        if isinstance(v,str):
            try:
                hit = float(v); break
            except: pass

    # Peak/Mean DT (direct scalars)
    peak = mean = None
    for _, v in find_all(root, ["peak service time utilization", "peak_stu"]):
        if isinstance(v,(int,float)) and math.isfinite(v):
            peak = float(v); break
        if isinstance(v,str):
            try:
                peak = float(v); break
            except: pass

    for _, v in find_all(root, ["service time utilization", "mean service time utilization", "avg_stu"]):
        if isinstance(v,(int,float)) and math.isfinite(v):
            mean = float(v); break
        if isinstance(v,str):
            try:
                mean = float(v); break
            except: pass

    # Median (and fallbacks) from series if needed
    med, peak_from_series, mean_from_series = median_from_series(root)
    if peak is None and peak_from_series is not None:
        peak = peak_from_series
    if mean is None and mean_from_series is not None:
        mean = mean_from_series

    return dict(mean_dt=mean, median_dt=med, peak_dt=peak, hit_rate=hit)

# Files to read (adjust paths if needed)
files = [
  "./output/lru_baseline/acceptall-0_lru_50GB/full_0_0.1_cache_perf.txt.lzma",
  "./output/e1_dt_slru/acceptall-0_lru_50GB/full_0_0.1_cache_perf.txt.lzma",
]

for f in files:
    if not os.path.exists(f):
        print(f"== {f} ==\nERROR: file not found\n")
        continue
    m = extract_metrics(f)
    fmt = lambda x: "NA" if x is None else f"{x:.5g}"
    print(f"== {f} ==")
    print("Mean DT (%)  :", fmt(m['mean_dt']))
    print("Median DT (%) :", fmt(m['median_dt']))
    print("Peak DT (%)  :", fmt(m['peak_dt']))
    print("Hit Rate     :", fmt(m['hit_rate']))
    print()

